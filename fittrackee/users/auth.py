import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Union

import jwt
from flask import (
    Blueprint,
    Response,
    current_app,
    request,
    send_from_directory,
)
from sqlalchemy import exc, func
from sqlalchemy.dialects.postgresql import insert
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from fittrackee import appLog, db
from fittrackee.dates import get_datetime_in_utc, get_readable_duration
from fittrackee.emails.tasks import send_email
from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.equipments.utils import handle_equipments
from fittrackee.files import get_absolute_file_path
from fittrackee.oauth2.server import require_auth
from fittrackee.reports.models import ReportAction, ReportActionAppeal
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    EquipmentInvalidPayloadErrorResponse,
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    PayloadTooLargeErrorResponse,
    UnauthorizedErrorResponse,
    get_error_response_if_file_is_invalid,
    handle_error_and_return_response,
)
from fittrackee.users.users_service import UserManagerService
from fittrackee.utils import (
    decode_short_id,
)
from fittrackee.visibility_levels import (
    VisibilityLevel,
    get_calculated_visibility,
)
from fittrackee.workouts.models import Sport

from .exceptions import UserControlsException, UserCreationException
from .models import (
    BlacklistedToken,
    BlockedUser,
    Notification,
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
    UserTask,
)
from .roles import UserRole
from .tasks import export_data
from .timezones import TIMEZONES, get_timezone
from .utils.controls import check_password, is_valid_email
from .utils.language import get_language
from .utils.tokens import decode_user_token

auth_blueprint = Blueprint("auth", __name__)

HEX_COLOR_REGEX = regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
NOT_FOUND_MESSAGE = "the requested URL was not found on the server"
BLOCKED_USERS_PER_PAGE = 5


def send_account_confirmation_email(user: User) -> None:
    if current_app.config["CAN_SEND_EMAILS"]:
        fittrackee_url = current_app.config["UI_URL"]
        email_data = {
            "username": user.username,
            "fittrackee_url": fittrackee_url,
            "operating_system": request.user_agent.platform,  # type: ignore
            "browser_name": request.user_agent.browser,  # type: ignore
            "account_confirmation_url": (
                f"{fittrackee_url}/account-confirmation"
                f"?token={user.confirmation_token}"
            ),
        }
        user_data = {
            "language": get_language(user.language),
            "email": user.email,
        }
        send_email.send(user_data, email_data, template="account_confirmation")


@auth_blueprint.route("/auth/register", methods=["POST"])
def register_user() -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Register a user and send confirmation email.

    The newly created account is inactive. The user must confirm his email
    to activate it.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/register HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - success:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

      {
        "status": "success"
      }

    - error on registration:

    .. sourcecode:: http

      HTTP/1.1 400 BAD REQUEST
      Content-Type: application/json

      {
        "message": "Errors: email: valid email must be provided\\n",
        "status": "error"
      }

    :<json string username: username (3 to 30 characters required)
    :<json string email: user email
    :<json string password: password (8 characters required)
    :<json string lang: user language preferences (if not provided or invalid,
                        fallback to 'en' (english))
    :<json boolean accepted_policy: ``true`` if user accepted privacy policy
    :<json string timezone: user timezone (if not provided or invalid,
                        fallback to 'Europe/Paris')

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``sorry, that username is already taken``
        - ``sorry, you must agree privacy policy to register``
        - ``username: 3 to 30 characters required``
        - ``username: only alphanumeric characters and the underscore
          character "_" allowed``
        - ``email: valid email must be provided``
        - ``password: 8 characters required``
    :statuscode 403: ``error, registration is disabled``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    if not current_app.config.get("is_registration_enabled"):
        return ForbiddenErrorResponse("error, registration is disabled")

    post_data = request.get_json()
    if (
        not post_data
        or post_data.get("username") is None
        or post_data.get("email") is None
        or post_data.get("password") is None
        or post_data.get("accepted_policy") is None
    ):
        return InvalidPayloadErrorResponse()

    accepted_policy = post_data.get("accepted_policy") is True
    if not accepted_policy:
        return InvalidPayloadErrorResponse(
            "sorry, you must agree privacy policy to register"
        )

    username = post_data.get("username")
    email = post_data.get("email")
    password = post_data.get("password")
    language = get_language(post_data.get("language"))
    tz = get_timezone(post_data.get("timezone"))

    try:
        user_manager_service = UserManagerService(username=username)
        new_user, _ = user_manager_service.create_user(email, password)
        # if a user exists with same email address (returned new_user is None),
        # no error is returned since a user has to confirm his email to
        # activate his account
        if new_user:
            new_user.language = language
            new_user.timezone = tz
            new_user.accepted_policy_date = datetime.now(timezone.utc)
            for admin in User.query.filter(
                User.role == UserRole.ADMIN.value,
                User.is_active == True,  # noqa
            ).all():
                if not admin.is_notification_enabled("account_creation"):
                    continue
                notification = Notification(
                    from_user_id=new_user.id,
                    to_user_id=admin.id,
                    created_at=new_user.created_at,
                    event_type="account_creation",
                    event_object_id=new_user.id,
                )
                db.session.add(notification)
            db.session.commit()
            send_account_confirmation_email(new_user)

        return {"status": "success"}, 200
    # handler errors
    except (UserControlsException, UserCreationException) as e:
        return InvalidPayloadErrorResponse(str(e))
    except (
        exc.IntegrityError,
        exc.OperationalError,
        TypeError,
        ValueError,
    ) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/login", methods=["POST"])
def login_user() -> Union[Dict, HttpResponse]:
    """
    User login.

    Only user with an active account can log in.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/login HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - successful login:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "auth_token": "JSON Web Token",
        "message": "successfully logged in",
        "status": "success"
      }

    - error on login

    .. sourcecode:: http

      HTTP/1.1 401 UNAUTHORIZED
      Content-Type: application/json

      {
        "message": "invalid credentials",
        "status": "error"
      }

    :<json string email: user email
    :<json string password: password

    :statuscode 200: ``successfully logged in``
    :statuscode 400: ``invalid payload``
    :statuscode 401: ``invalid credentials``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    # get post data
    post_data = request.get_json()
    if not post_data:
        return InvalidPayloadErrorResponse()
    email = post_data.get("email", "")
    password = post_data.get("password")
    try:
        user = User.query.filter(
            func.lower(User.email) == func.lower(email),
            User.is_active == True,  # noqa
        ).first()
        if user and user.check_password(password):
            # generate auth token
            auth_token = user.encode_auth_token(user.id)
            return {
                "status": "success",
                "message": "successfully logged in",
                "auth_token": auth_token,
            }
        return UnauthorizedErrorResponse("invalid credentials")
    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/profile", methods=["GET"])
@require_auth(scopes=["profile:read"], allow_suspended_user=True)
def get_authenticated_user_profile(
    auth_user: User,
) -> Union[Dict, HttpResponse]:
    """
    Get authenticated user info (profile, account, preferences).

    Suspended user can access this endpoint.

    **Scope**: ``profile:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/profile HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "accepted_privacy_policy": true,
          "analysis_visibility": "private",
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "followers": 0,
          "following": 0,
          "hide_profile_in_users_directory": true,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "manually_approves_followers": false,
          "map_visibility": "private",
          "nb_sports": 3,
          "nb_workouts": 6,
          "notification_preferences": {
            "comment_like": true,
            "follow": true,
            "follow_request": true,
            "follow_request_approved": true,
            "mention": true,
            "workout_comment": true,
            "workout_like": true
          }
          "picture": false,
          "records": [
            {
              "id": 9,
              "record_type": "AS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 10,
              "record_type": "FD",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 13,
              "record_type": "HA",
              "sport_id": 1,
              "user": "Sam",
              "value": 43.97,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 11,
              "record_type": "LD",
              "sport_id": 1,
              "user": "sam",
              "value": "1:01:00",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 12,
              "record_type": "MS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            }
          ],
          "role": "user",
          "segments_creation_event": "manual",
          "sports_list": [
              1,
              4,
              6
          ],
          "start_elevation_at_zero": false,
          "timezone": "Europe/Paris",
          "total_ascent": 720.35,
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "use_dark_mode": null,
          "use_raw_gpx_speed": false,
          "username": "sam",
          "weekm": false,
          "workouts_visibility": "private"
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    return {
        "status": "success",
        "data": auth_user.serialize(current_user=auth_user, light=False),
    }


@auth_blueprint.route("/auth/profile/edit", methods=["POST"])
@require_auth(scopes=["profile:write"], allow_suspended_user=True)
def edit_user(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Edit authenticated user profile.

    Suspended user can access this endpoint.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/profile/edit HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "accepted_privacy_policy": true,
          "analysis_visibility": "private",
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "followers": 0,
          "following": 0,
          "hide_profile_in_users_directory": true,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "manually_approves_followers": false,
          "map_visibility": "private",
          "nb_sports": 3,
          "nb_workouts": 6,
          "notification_preferences": {
            "comment_like": true,
            "follow": true,
            "follow_request": true,
            "follow_request_approved": true,
            "mention": true,
            "workout_comment": true,
            "workout_like": true
          }
          "picture": false,
          "records": [
            {
              "id": 9,
              "record_type": "AS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 10,
              "record_type": "FD",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 13,
              "record_type": "HA",
              "sport_id": 1,
              "user": "Sam",
              "value": 43.97,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 11,
              "record_type": "LD",
              "sport_id": 1,
              "user": "sam",
              "value": "1:01:00",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 12,
              "record_type": "MS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            }
          ],
          "role": "user",
          "segments_creation_event": "manual",
          "sports_list": [
              1,
              4,
              6
          ],
          "start_elevation_at_zero": false,
          "timezone": "Europe/Paris",
          "total_ascent": 720.35,
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "use_dark_mode": null,
          "use_raw_gpx_speed": false,
          "username": "sam"
          "weekm": true,
          "workouts_visibility": "private"
        },
        "message": "user profile updated",
        "status": "success"
      }

    :<json string first_name: user first name
    :<json string last_name: user last name
    :<json string location: user location
    :<json string bio: user biography
    :<json string birth_date: user birth date (format: ``%Y-%m-%d``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user profile updated``
    :statuscode 400: ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    # get post data
    post_data = request.get_json()
    user_mandatory_data = {
        "first_name",
        "last_name",
        "bio",
        "birth_date",
        "location",
    }
    if not post_data or not post_data.keys() >= user_mandatory_data:
        return InvalidPayloadErrorResponse()

    first_name = post_data.get("first_name")
    last_name = post_data.get("last_name")
    bio = post_data.get("bio")
    birth_date = post_data.get("birth_date")
    location = post_data.get("location")

    try:
        auth_user.first_name = first_name
        auth_user.last_name = last_name
        auth_user.bio = bio
        auth_user.location = location
        auth_user.birth_date = (
            get_datetime_in_utc(birth_date) if birth_date else None
        )
        db.session.commit()

        return {
            "status": "success",
            "message": "user profile updated",
            "data": auth_user.serialize(current_user=auth_user, light=False),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/profile/edit/account", methods=["PATCH"])
@require_auth(scopes=["profile:write"], allow_suspended_user=True)
def update_user_account(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Update authenticated user email and password.

    It sends emails if sending is enabled:

    - Password change
    - Email change:

      - one to the current address to inform user
      - another one to the new address to confirm it.

    Suspended user can access this endpoint.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      PATCH /api/auth/profile/edit/account HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "accepted_privacy_policy": true,
          "analysis_visibility": "private",
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "hide_profile_in_users_directory": true,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "manually_approves_followers": false,
          "map_visibility": "followers_only",
          "nb_sports": 3,
          "nb_workouts": 6,
          "notification_preferences": {
            "comment_like": true,
            "follow": true,
            "follow_request": true,
            "follow_request_approved": true,
            "mention": true,
            "workout_comment": true,
            "workout_like": true
          }
          "picture": false,
          "records": [
            {
              "id": 9,
              "record_type": "AS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 10,
              "record_type": "FD",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 13,
              "record_type": "HA",
              "sport_id": 1,
              "user": "Sam",
              "value": 43.97,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 11,
              "record_type": "LD",
              "sport_id": 1,
              "user": "sam",
              "value": "1:01:00",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 12,
              "record_type": "MS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            }
          ],
          "role": "user",
          "segments_creation_event": "manual",
          "sports_list": [
              1,
              4,
              6
          ],
          "start_elevation_at_zero": false,
          "timezone": "Europe/Paris",
          "total_ascent": 720.35,
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "use_dark_mode": null,
          "use_raw_gpx_speed": false,
          "username": "sam"
          "weekm": true,
          "workouts_visibility": "private"
        },
        "message": "user account updated",
        "status": "success"
      }

    :<json string email: user email
    :<json string password: user current password
    :<json string new_password: user new password

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user account updated``
    :statuscode 400:
        - ``invalid payload``
        - ``email is missing``
        - ``current password is missing``
        - ``email: valid email must be provided``
        - ``password: 8 characters required``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
        - ``invalid credentials``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    data = request.get_json()
    if not data:
        return InvalidPayloadErrorResponse()
    email_to_confirm = data.get("email")
    if not email_to_confirm:
        return InvalidPayloadErrorResponse("email is missing")
    current_password = data.get("password")
    if not current_password:
        return InvalidPayloadErrorResponse("current password is missing")
    if not auth_user.check_password(current_password):
        return UnauthorizedErrorResponse("invalid credentials")

    new_password = data.get("new_password")
    error_messages = ""
    try:
        if email_to_confirm != auth_user.email:
            if is_valid_email(email_to_confirm):
                if current_app.config["CAN_SEND_EMAILS"]:
                    auth_user.email_to_confirm = email_to_confirm
                    auth_user.confirmation_token = secrets.token_urlsafe(30)
                else:
                    auth_user.email = email_to_confirm
                    auth_user.confirmation_token = None
            else:
                error_messages = "email: valid email must be provided\n"

        if new_password is not None:
            error_messages += check_password(new_password)
            if error_messages == "":
                hashed_password = auth_user.generate_password_hash(
                    new_password
                )
                auth_user.password = hashed_password

        if error_messages != "":
            return InvalidPayloadErrorResponse(error_messages)

        db.session.commit()

        if current_app.config["CAN_SEND_EMAILS"]:
            fittrackee_url = current_app.config["UI_URL"]
            user_data = {
                "language": get_language(auth_user.language),
                "email": auth_user.email,
            }
            data = {
                "username": auth_user.username,
                "fittrackee_url": fittrackee_url,
                "operating_system": request.user_agent.platform,
                "browser_name": request.user_agent.browser,
            }

            if new_password is not None:
                send_email.send(user_data, data, template="password_change")

            if (
                auth_user.email_to_confirm is not None
                and auth_user.email_to_confirm != auth_user.email
            ):
                email_data = {
                    **data,
                    **{"new_email_address": email_to_confirm},
                }
                send_email.send(
                    user_data,
                    email_data,
                    template="email_update_to_current_email",
                )

                email_data = {
                    **data,
                    **{
                        "email_confirmation_url": (
                            f"{fittrackee_url}/email-update"
                            f"?token={auth_user.confirmation_token}"
                        )
                    },
                }
                user_data = {
                    **user_data,
                    **{"email": auth_user.email_to_confirm},
                }
                send_email.send(
                    user_data, email_data, template="email_update_to_new_email"
                )

        return {
            "status": "success",
            "message": "user account updated",
            "data": auth_user.serialize(current_user=auth_user, light=False),
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/profile/edit/preferences", methods=["POST"])
@require_auth(scopes=["profile:write"], allow_suspended_user=True)
def edit_user_preferences(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Edit authenticated user preferences.

    Supported date formats:

    - ``MM/dd/yyyy`` (default value)
    - ``dd/MM/yyyy``
    - ``yyyy-MM-dd``
    - ``date_string``, corresponding on client to:

      - ``MMM. do, yyyy`` for ``en`` locale
      - ``d MMM yyyy`` for ``es``, ``fr``, ``gl``, ``it`` and ``nl`` locales
      - ``do MMM yyyy`` for ``de`` and ``nb`` locales

    Suspended user can access this endpoint.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/profile/edit/preferences HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "accepted_privacy_policy": true,
          "analysis_visibility": "private",
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "MM/dd/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "followers": 0,
          "following": 0,
          "hide_profile_in_users_directory": true,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "manually_approves_followers": false,
          "map_visibility": "followers_only",
          "nb_sports": 3,
          "nb_workouts": 6,
          "notification_preferences": {
            "comment_like": true,
            "follow": true,
            "follow_request": true,
            "follow_request_approved": true,
            "mention": true,
            "workout_comment": true,
            "workout_like": true
          }
          "picture": false,
          "records": [
            {
              "id": 9,
              "record_type": "AS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 10,
              "record_type": "FD",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 13,
              "record_type": "HA",
              "sport_id": 1,
              "user": "Sam",
              "value": 43.97,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 11,
              "record_type": "LD",
              "sport_id": 1,
              "user": "sam",
              "value": "1:01:00",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 12,
              "record_type": "MS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            }
          ],
          "role": "user",
          "segments_creation_event": "manual",
          "sports_list": [
              1,
              4,
              6
          ],
          "start_elevation_at_zero": true,
          "timezone": "Europe/Paris",
          "total_ascent": 720.35,
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "use_dark_mode": null,
          "use_raw_gpx_speed": true,
          "username": "sam"
          "weekm": true,
          "workouts_visibility": "public"
        },
        "message": "user preferences updated",
        "status": "success"
      }

    :<json string analysis_visibility: workout analysis visibility
                  (``public``, ``followers_only``, ``private``)
    :<json string date_format: the format used to display dates in the app
    :<json boolean display_ascent: display highest ascent records and total
    :<json boolean hide_profile_in_users_directory: if ``true``, user does not
                  appear in users directory
    :<json boolean hr_visibility: heart rate visibility
                  (``public``, ``followers_only``, ``private``)
    :<json boolean imperial_units: display distance in imperial units
    :<json string language: language preferences
    :<json boolean manually_approves_followers: if ``false``, follow requests
                  are automatically approved
    :<json string map_visibility: workout map visibility
                  (``public``, ``followers_only``, ``private``)
    :<json string segments_creation_event: event triggering a segment creation
                  for .fit files (``all``, ``only_manual``, ``none``)
    :<json boolean start_elevation_at_zero: do elevation plots start at zero?
    :<json string timezone: user time zone
    :<json boolean use_dark_mode: Display interface with dark mode if ``true``.
                   If ``null``, it uses browser preferences.
    :<json boolean use_raw_gpx_speed: Use unfiltered gpx to calculate speeds
    :<json boolean weekm: does week start on Monday?
    :<json string workouts_visibility: user workouts visibility
                  (``public``, ``followers_only``, ``private``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user preferences updated``
    :statuscode 400:
        - ``invalid payload``
        - ``password: password and password confirmation don't match``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    # get post data
    post_data = request.get_json()
    user_mandatory_data = {
        "analysis_visibility",
        "date_format",
        "display_ascent",
        "hide_profile_in_users_directory",
        "hr_visibility",
        "imperial_units",
        "language",
        "manually_approves_followers",
        "map_visibility",
        "segments_creation_event",
        "start_elevation_at_zero",
        "timezone",
        "use_dark_mode",
        "use_raw_gpx_speed",
        "weekm",
        "workouts_visibility",
    }
    if not post_data or not post_data.keys() >= user_mandatory_data:
        return InvalidPayloadErrorResponse()

    date_format = post_data.get("date_format")
    display_ascent = post_data.get("display_ascent")
    imperial_units = post_data.get("imperial_units")
    language = get_language(post_data.get("language"))
    start_elevation_at_zero = post_data.get("start_elevation_at_zero")
    use_raw_gpx_speed = post_data.get("use_raw_gpx_speed")
    use_dark_mode = post_data.get("use_dark_mode")
    timezone = post_data.get("timezone")
    weekm = post_data.get("weekm")
    map_visibility = post_data.get("map_visibility")
    analysis_visibility = post_data.get("analysis_visibility")
    workouts_visibility = post_data.get("workouts_visibility")
    manually_approves_followers = post_data.get("manually_approves_followers")
    hide_profile_in_users_directory = post_data.get(
        "hide_profile_in_users_directory"
    )
    hr_visibility = post_data.get("hr_visibility")
    segments_creation_event = post_data.get("segments_creation_event")

    try:
        auth_user.date_format = date_format
        auth_user.display_ascent = display_ascent
        auth_user.imperial_units = imperial_units
        auth_user.language = language
        auth_user.start_elevation_at_zero = start_elevation_at_zero
        auth_user.timezone = timezone
        auth_user.use_dark_mode = use_dark_mode
        auth_user.use_raw_gpx_speed = use_raw_gpx_speed
        auth_user.weekm = weekm
        auth_user.workouts_visibility = VisibilityLevel(workouts_visibility)
        auth_user.analysis_visibility = get_calculated_visibility(
            visibility=VisibilityLevel(analysis_visibility),
            parent_visibility=auth_user.workouts_visibility,
        )
        auth_user.map_visibility = get_calculated_visibility(
            visibility=VisibilityLevel(map_visibility),
            parent_visibility=auth_user.analysis_visibility,
        )
        auth_user.manually_approves_followers = manually_approves_followers
        auth_user.hide_profile_in_users_directory = (
            hide_profile_in_users_directory
        )
        auth_user.hr_visibility = VisibilityLevel(hr_visibility)
        auth_user.segments_creation_event = segments_creation_event
        db.session.commit()

        return {
            "status": "success",
            "message": "user preferences updated",
            "data": auth_user.serialize(current_user=auth_user, light=False),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/profile/edit/sports", methods=["POST"])
@require_auth(scopes=["profile:write"])
def edit_user_sport_preferences(
    auth_user: User,
) -> Union[Dict, HttpResponse]:
    """
    Edit authenticated user sport preferences.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/profile/edit/sports HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "color": "#000000",
          "default_equipment_ids": [],
          "is_active": true,
          "sport_id": 1,
          "stopped_speed_threshold": 1,
          "user_id": 1
        },
        "message": "user sport preferences updated",
        "status": "success"
      }

    :<json int sport_id: id of the sport for which preferences are
           created/modified
    :<json string color: valid hexadecimal color
    :<json boolean is_active: is sport available when adding a workout
    :<json float stopped_speed_threshold: stopped speed threshold used by gpxpy
    :<json array of strings default_equipment_ids: the default equipment id
           to use for this sport.
           **Note**: for now only one equipment can be associated.

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user sport preferences updated``
    :statuscode 400:
        - ``invalid payload``
        - ``invalid hexadecimal color``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
        - ``equipment_ids must be an array of strings``
        - ``only one equipment can be added``
        - ``equipment with id <equipment_id> does not exist``
        - ``invalid equipment id <equipment_id> for sport``
        - ``equipment with id <equipment_id> is inactive``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``sport does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    post_data = request.get_json()
    if (
        not post_data
        or "sport_id" not in post_data
        or len(post_data.keys()) == 1
    ):
        return InvalidPayloadErrorResponse()

    sport_id = post_data.get("sport_id")
    sport = Sport.query.filter_by(id=sport_id).first()
    if not sport:
        return NotFoundErrorResponse("sport does not exist")

    color = post_data.get("color")
    is_active = post_data.get("is_active")
    stopped_speed_threshold = post_data.get("stopped_speed_threshold")
    default_equipment_ids = post_data.get("default_equipment_ids")

    try:
        user_sport = UserSportPreference.query.filter_by(
            user_id=auth_user.id,
            sport_id=sport_id,
        ).first()
        if not user_sport:
            user_sport = UserSportPreference(
                user_id=auth_user.id,
                sport_id=sport_id,
                stopped_speed_threshold=sport.stopped_speed_threshold,
            )
            db.session.add(user_sport)
            db.session.flush()
        if color:
            if re.match(HEX_COLOR_REGEX, color) is None:
                return InvalidPayloadErrorResponse("invalid hexadecimal color")
            user_sport.color = color
        if is_active is not None:
            user_sport.is_active = is_active
        if stopped_speed_threshold:
            user_sport.stopped_speed_threshold = stopped_speed_threshold

        if default_equipment_ids is not None:
            existing_default_equipments = user_sport.default_equipments.all()
            default_equipments = handle_equipments(
                default_equipment_ids,
                auth_user,
                sport_id,
                existing_default_equipments,
            )
            if default_equipments:
                db.session.execute(
                    insert(UserSportPreferenceEquipment)
                    .values(
                        [
                            {
                                "equipment_id": equipment.id,
                                "sport_id": user_sport.sport_id,
                                "user_id": auth_user.id,
                            }
                            for equipment in default_equipments
                        ]
                    )
                    .on_conflict_do_nothing()
                )

                equipments_to_remove = set(existing_default_equipments) - set(
                    default_equipments
                )
                db.session.query(UserSportPreferenceEquipment).filter(
                    UserSportPreferenceEquipment.c.user_id == auth_user.id,
                    (
                        UserSportPreferenceEquipment.c.sport_id
                        == user_sport.sport_id
                    ),
                    UserSportPreferenceEquipment.c.equipment_id.in_(
                        [e.id for e in equipments_to_remove]
                    ),
                ).delete()

            elif existing_default_equipments:
                db.session.query(UserSportPreferenceEquipment).filter(
                    UserSportPreferenceEquipment.c.user_id == auth_user.id,
                    UserSportPreferenceEquipment.c.sport_id
                    == user_sport.sport_id,
                ).delete()
        db.session.commit()

        return {
            "status": "success",
            "message": "user sport preferences updated",
            "data": user_sport.serialize(),
        }

    # handler errors
    except InvalidEquipmentsException as e:
        return InvalidPayloadErrorResponse(str(e))
    except InvalidEquipmentException as e:
        return EquipmentInvalidPayloadErrorResponse(
            equipment_id=e.equipment_id, message=e.message, status=e.status
        )
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/profile/edit/notifications", methods=["POST"])
@require_auth(scopes=["profile:write"])
def edit_user_notifications_preferences(
    auth_user: User,
) -> Union[Dict, HttpResponse]:
    """
    Edit authenticated user preferences for UI notifications.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/profile/edit/preferences HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "data": {
          "accepted_privacy_policy": true,
          "analysis_visibility": "private",
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "followers": 0,
          "following": 0,
          "hide_profile_in_users_directory": true,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "manually_approves_followers": false,
          "map_visibility": "private",
          "nb_sports": 3,
          "nb_workouts": 6,
          "notification_preferences": {
            "comment_like": true,
            "follow": true,
            "follow_request": true,
            "follow_request_approved": true,
            "mention": false,
            "workout_comment": false,
            "workout_like": false
          }
          "picture": false,
          "records": [
            {
              "id": 9,
              "record_type": "AS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 10,
              "record_type": "FD",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 13,
              "record_type": "HA",
              "sport_id": 1,
              "user": "Sam",
              "value": 43.97,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 11,
              "record_type": "LD",
              "sport_id": 1,
              "user": "sam",
              "value": "1:01:00",
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            },
            {
              "id": 12,
              "record_type": "MS",
              "sport_id": 1,
              "user": "sam",
              "value": 18,
              "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
              "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
            }
          ],
          "segments_creation_event": "manual",
          "sports_list": [
              1,
              4,
              6
          ],
          "start_elevation_at_zero": false,
          "timezone": "Europe/Paris",
          "total_ascent": 720.35,
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "use_dark_mode": null,
          "use_raw_gpx_speed": false,
          "username": "sam",
          "weekm": false,
          "workouts_visibility": "private"
        },
        "status": "success"
      }

    :<json boolean account_creation: notification for user registration
           (only for user with administration rights)
    :<json boolean comment_like: notification for comment likes
    :<json boolean follow: notification for follow
    :<json boolean follow_request: notification for follow requests
    :<json boolean follow_request_approved: notification for follow request
           approval
    :<json boolean mention: notification for mention
    :<json boolean workout_comment: notification for comments on workout
    :<json boolean workout_like: notification for workout likes

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user preferences updated``
    :statuscode 400:
        - ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    preferences_data = request.get_json()
    mandatory_data = {
        "comment_like",
        "follow",
        "follow_request",
        "follow_request_approved",
        "mention",
        "workout_comment",
        "workout_like",
    }
    if not preferences_data or not preferences_data.keys() >= mandatory_data:
        return InvalidPayloadErrorResponse()
    if (
        auth_user.role >= UserRole.ADMIN.value
        and "account_creation" not in preferences_data
    ):
        return InvalidPayloadErrorResponse()

    auth_user.update_preferences(preferences_data)
    db.session.commit()

    return {
        "data": auth_user.serialize(current_user=auth_user, light=False),
        "status": "success",
    }


@auth_blueprint.route(
    "/auth/profile/reset/sports/<sport_id>", methods=["DELETE"]
)
@require_auth(scopes=["profile:write"])
def reset_user_sport_preferences(
    auth_user: User, sport_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Reset authenticated user preferences for a given sport.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/auth/profile/reset/sports/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 OK
      Content-Type: application/json

    :param string sport_id: sport id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: user preferences deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``sport does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    sport = Sport.query.filter_by(id=sport_id).first()
    if not sport:
        return NotFoundErrorResponse("sport does not exist")

    try:
        user_sport = UserSportPreference.query.filter_by(
            user_id=auth_user.id,
            sport_id=sport_id,
        ).first()
        if user_sport:
            db.session.delete(user_sport)
            db.session.commit()
        return {"status": "no content"}, 204

    # handler errors
    except (exc.IntegrityError, exc.OperationalError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/picture", methods=["POST"])
@require_auth(scopes=["profile:write"], allow_suspended_user=True)
def edit_picture(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Update authenticated user picture.

    Suspended user can access this endpoint.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/picture HTTP/1.1
      Content-Type: multipart/form-data

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "user picture updated",
        "status": "success"
      }

    :form file: image file (allowed extensions: .jpg, .png, .gif)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user picture updated``
    :statuscode 400:
        - ``invalid payload``
        - ``no file part``
        - ``no selected file``
        - ``file extension not allowed``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 413: ``error during picture update: file size exceeds 1.0MB``
    :statuscode 500: ``error during picture update``
    """
    try:
        response_object = get_error_response_if_file_is_invalid(
            "picture", request
        )
    except RequestEntityTooLarge as e:
        appLog.error(e)
        return PayloadTooLargeErrorResponse(
            file_type="picture",
            file_size=request.content_length,
            max_size=current_app.config["MAX_CONTENT_LENGTH"],
        )
    if response_object:
        return response_object

    file = request.files["file"]
    filename = secure_filename(file.filename)  # type: ignore
    dirpath = os.path.join(
        current_app.config["UPLOAD_FOLDER"], "pictures", str(auth_user.id)
    )
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    absolute_picture_path = os.path.join(dirpath, filename)
    relative_picture_path = os.path.join(
        "pictures", str(auth_user.id), filename
    )

    try:
        if auth_user.picture is not None:
            old_picture_path = get_absolute_file_path(auth_user.picture)
            if os.path.isfile(get_absolute_file_path(old_picture_path)):
                os.remove(old_picture_path)
        file.save(absolute_picture_path)
        auth_user.picture = relative_picture_path
        db.session.commit()
        return {
            "status": "success",
            "message": "user picture updated",
        }

    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            e, message="error during picture update", status="fail", db=db
        )


@auth_blueprint.route("/auth/picture", methods=["DELETE"])
@require_auth(scopes=["profile:write"], allow_suspended_user=True)
def del_picture(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete authenticated user picture.

    Suspended user can access this endpoint.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/auth/picture HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: picture deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 500: ``error during picture deletion``

    """
    if not auth_user.picture:
        return {"status": "no content"}, 204

    try:
        picture_path = get_absolute_file_path(auth_user.picture)
        if os.path.isfile(picture_path):
            os.remove(picture_path)
        auth_user.picture = None
        db.session.commit()
        return {"status": "no content"}, 204
    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            e, message="error during picture deletion", status="fail", db=db
        )


@auth_blueprint.route("/auth/password/reset-request", methods=["POST"])
def request_password_reset() -> Union[Dict, HttpResponse]:
    """
    Handle password reset request.

    If email sending is disabled, this endpoint is not available.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/password/reset-request HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "password reset request processed",
        "status": "success"
      }

    :<json string email: user email

    :statuscode 200: ``password reset request processed``
    :statuscode 400: ``invalid payload``
    :statuscode 404: ``the requested URL was not found on the server``

    """
    if not current_app.config["CAN_SEND_EMAILS"]:
        return NotFoundErrorResponse(NOT_FOUND_MESSAGE)

    post_data = request.get_json()
    if not post_data or post_data.get("email") is None:
        return InvalidPayloadErrorResponse()
    email = post_data.get("email")

    user = User.query.filter(User.email == email).first()
    if user:
        password_reset_token = user.encode_password_reset_token(user.id)
        fittrackee_url = current_app.config["UI_URL"]
        user_language = get_language(user.language)
        email_data = {
            "expiration_delay": get_readable_duration(
                current_app.config["PASSWORD_TOKEN_EXPIRATION_SECONDS"],
                user_language,
            ),
            "username": user.username,
            "password_reset_url": (
                f"{fittrackee_url}/password-reset?token={password_reset_token}"
            ),
            "fittrackee_url": fittrackee_url,
            "operating_system": request.user_agent.platform,  # type: ignore
            "browser_name": request.user_agent.browser,  # type: ignore
        }
        user_data = {
            "language": user_language,
            "email": user.email,
        }
        send_email.send(
            user_data, email_data, template="password_reset_request"
        )
    return {
        "status": "success",
        "message": "password reset request processed",
    }


@auth_blueprint.route("/auth/password/update", methods=["POST"])
def update_password() -> Union[Dict, HttpResponse]:
    """
    Update user password after password reset request.

    It sends emails if sending is enabled.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/password/update HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "password updated",
        "status": "success"
      }

    :<json string password: password (8 characters required)
    :<json string token: password reset token

    :statuscode 200: ``password updated``
    :statuscode 400: ``invalid payload``
    :statuscode 401: ``invalid token, please request a new token``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    post_data = request.get_json()
    if (
        not post_data
        or post_data.get("password") is None
        or post_data.get("token") is None
    ):
        return InvalidPayloadErrorResponse()
    password = post_data.get("password")
    token = post_data.get("token")

    try:
        user_id = decode_user_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return UnauthorizedErrorResponse()

    message = check_password(password)
    if message != "":
        return InvalidPayloadErrorResponse(message)

    user = User.query.filter(User.id == user_id).first()
    if not user:
        return UnauthorizedErrorResponse()
    try:
        user.password = user.generate_password_hash(password)
        db.session.commit()

        if current_app.config["CAN_SEND_EMAILS"]:
            send_email.send(
                user_data={
                    "language": get_language(user.language),
                    "email": user.email,
                },
                email_data={
                    "username": user.username,
                    "fittrackee_url": current_app.config["UI_URL"],
                    "operating_system": request.user_agent.platform,
                    "browser_name": request.user_agent.browser,
                },
                template="password_change",
            )

        return {
            "status": "success",
            "message": "password updated",
        }
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/email/update", methods=["POST"])
def update_email() -> Union[Dict, HttpResponse]:
    """
    Update user email after confirmation.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/email/update HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "email updated",
        "status": "success"
      }

    :<json string token: password reset token

    :statuscode 200: ``email updated``
    :statuscode 400: ``invalid payload``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    post_data = request.get_json()
    if not post_data or post_data.get("token") is None:
        return InvalidPayloadErrorResponse()
    token = post_data.get("token")

    try:
        user = User.query.filter_by(confirmation_token=token).first()

        if not user:
            return InvalidPayloadErrorResponse()

        user.email = user.email_to_confirm
        user.email_to_confirm = None
        user.confirmation_token = None

        db.session.commit()

        response = {
            "status": "success",
            "message": "email updated",
        }

        return response

    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/account/confirm", methods=["POST"])
def confirm_account() -> Union[Dict, HttpResponse]:
    """
    Activate user account after registration.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/account/confirm HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "auth_token": "JSON Web Token",
        "message": "account confirmation successful",
        "status": "success"
      }

    :<json string token: confirmation token

    :statuscode 200: ``account confirmation successful``
    :statuscode 400: ``invalid payload``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    post_data = request.get_json()
    if not post_data or post_data.get("token") is None:
        return InvalidPayloadErrorResponse()
    token = post_data.get("token")

    try:
        user = User.query.filter_by(confirmation_token=token).first()

        if not user:
            return InvalidPayloadErrorResponse()

        user.is_active = True
        user.confirmation_token = None

        db.session.commit()

        # generate auth token
        auth_token = user.encode_auth_token(user.id)

        response = {
            "status": "success",
            "message": "account confirmation successful",
            "auth_token": auth_token,
        }
        return response

    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/account/resend-confirmation", methods=["POST"])
def resend_account_confirmation_email() -> Union[Dict, HttpResponse]:
    """
    Resend email with instructions to confirm account.

    If email sending is disabled, this endpoint is not available.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/account/resend-confirmation HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "confirmation email resent",
        "status": "success"
      }

    :<json string email: user email

    :statuscode 200: ``confirmation email resent``
    :statuscode 400: ``invalid payload``
    :statuscode 404: ``the requested URL was not found on the server``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    if not current_app.config["CAN_SEND_EMAILS"]:
        return NotFoundErrorResponse(NOT_FOUND_MESSAGE)

    post_data = request.get_json()
    if not post_data or post_data.get("email") is None:
        return InvalidPayloadErrorResponse()
    email = post_data.get("email")

    try:
        user = User.query.filter_by(email=email, is_active=False).first()
        if user:
            user.confirmation_token = secrets.token_urlsafe(30)
            db.session.commit()

            send_account_confirmation_email(user)

        response = {
            "status": "success",
            "message": "confirmation email resent",
        }
        return response
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/logout", methods=["POST"])
@require_auth(allow_suspended_user=True)
def logout_user(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    User logout.
    If a valid token is provided, it will be blacklisted.

    Suspended user can access this endpoint.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/logout HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - successful logout:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "successfully logged out",
        "status": "success"
      }

    - error on logout:

    .. sourcecode:: http

      HTTP/1.1 401 UNAUTHORIZED
      Content-Type: application/json

      {
        "message": "provide a valid auth token",
        "status": "error"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``successfully logged out``
    :statuscode 401:
      - ``provide a valid auth token``
      - ``The access token provided is expired, revoked, malformed, or invalid
        for other reasons.``
    :statuscode 500: ``error on token blacklist``

    """
    auth_token = request.headers.get("Authorization", "").split(" ")[1]
    try:
        db.session.add(BlacklistedToken(token=auth_token))
        db.session.commit()
    except Exception:
        return {
            "status": "error",
            "message": "error on token blacklist",
        }, 500

    return {
        "status": "success",
        "message": "successfully logged out",
    }, 200


@auth_blueprint.route("/auth/account/privacy-policy", methods=["POST"])
@require_auth(allow_suspended_user=True)
def accept_privacy_policy(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    The authenticated user accepts the privacy policy.

    Suspended user can access this endpoint.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/account/privacy-policy HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success"
      }

    :<json boolean accepted_policy: ``true`` if user accepted privacy policy

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400: ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    post_data = request.get_json()
    if not post_data or not post_data.get("accepted_policy"):
        return InvalidPayloadErrorResponse()

    try:
        if post_data.get("accepted_policy") is True:
            auth_user.accepted_policy_date = datetime.now(timezone.utc)
            db.session.commit()
            return {"status": "success"}
        else:
            return InvalidPayloadErrorResponse()
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/account/export/request", methods=["POST"])
@require_auth(allow_suspended_user=True)
def request_user_data_export(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Request a data export for authenticated user.

    Suspended user can access this endpoint.

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/account/export/request HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "request": {
            "created_at": "Wed, 01 Mar 2023 12:31:17 GMT",
            "status": "in_progress",
            "file_name": null,
            "file_size": null
        }
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``ongoing request exists``
        - ``completed request already exists``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    existing_export_request = UserTask.query.filter_by(
        task_type="user_data_export", user_id=auth_user.id
    ).first()
    if existing_export_request:
        if not existing_export_request.completed:
            return InvalidPayloadErrorResponse("ongoing request exists")

        export_expiration = current_app.config["DATA_EXPORT_EXPIRATION"]
        if existing_export_request.created_at > (
            datetime.now(timezone.utc) - timedelta(hours=export_expiration)
        ):
            return InvalidPayloadErrorResponse(
                "completed request already exists"
            )

    try:
        if existing_export_request:
            db.session.delete(existing_export_request)
            db.session.flush()
        export_request = UserTask(
            user_id=auth_user.id, task_type="user_data_export"
        )
        db.session.add(export_request)
        db.session.commit()

        export_data.send(task_id=export_request.id)

        return {
            "status": "success",
            "request": export_request.serialize(current_user=auth_user),
        }
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/account/export", methods=["GET"])
@require_auth(allow_suspended_user=True)
def get_user_data_export(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Get a data export info for authenticated user if a request exists.

    It returns:

    - export creation date
    - export status (``in_progress``, ``successful`` and ``errored``)
    - file name and size (in bytes) when export is successful

    Suspended user can access this endpoint.

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/account/export HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - if a request exists:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "request": {
            "created_at": "Wed, 01 Mar 2023 12:31:17 GMT",
            "status": "successful",
            "file_name": "archive_rgjsR3fHt295ywNQr5Yp.zip",
            "file_size": 924
        }
      }

    - if no request:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "request": null
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    """
    export_request = UserTask.query.filter_by(
        user_id=auth_user.id, task_type="user_data_export"
    ).first()
    return {
        "status": "success",
        "request": export_request.serialize(current_user=auth_user)
        if export_request
        else None,
    }


@auth_blueprint.route(
    "/auth/account/export/<string:file_name>", methods=["GET"]
)
@require_auth(allow_suspended_user=True)
def download_data_export(
    auth_user: User, file_name: str
) -> Union[Response, HttpResponse]:
    """
    Download a data export archive.

    Suspended user can access this endpoint.

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/account/export/download/archive_rgjsR3fHr5Yp.zip HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/x-gzip

    :param string file_name: filename

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``file not found``
    """
    export_request = UserTask.query.filter_by(
        user_id=auth_user.id, task_type="user_data_export"
    ).first()
    if (
        not export_request
        or not export_request.completed
        or export_request.file_path.split("/")[-1] != file_name
    ):
        return DataNotFoundErrorResponse(
            data_type="archive", message="file not found"
        )

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        export_request.file_path,
        mimetype="application/zip",
        as_attachment=True,
    )


@auth_blueprint.route("/auth/blocked-users", methods=["GET"])
@require_auth(scopes=["profile:read"])
def get_blocked_users(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Get blocked users by authenticated user

    **Scope**: ``profile:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/auth/blocked-users HTTP/1.1

    - with parameters:

    .. sourcecode:: http

      GET /api/auth/blocked-users?page=1
        HTTP/1.1

    **Example responses**:

    - with blocked users:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "blocked_users": [
            {
              "blocked": true,
              "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_followed_by": "false",
              "nb_workouts": 1,
              "picture": false,
              "role": "user",
              "suspended_at": null,
              "username": "Sam"
            }
          ],
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 1,
            "total": 1
          },
          "status": "success"
        }

    - no blocked users:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "blocked_users": [],
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 0,
            "total": 0
          },
          "status": "success"
        }

    :query integer page: page if using pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    """
    params = request.args.copy()
    try:
        page = int(params.get("page", 1))
    except ValueError:
        page = 1

    paginated_relations = (
        User.query.join(BlockedUser, User.id == BlockedUser.user_id)
        .filter(BlockedUser.by_user_id == auth_user.id)
        .order_by(BlockedUser.created_at.desc())
        .paginate(page=page, per_page=BLOCKED_USERS_PER_PAGE, error_out=False)
    )
    return {
        "status": "success",
        "blocked_users": [
            user.serialize(current_user=auth_user)
            for user in paginated_relations.items
        ],
        "pagination": {
            "has_next": paginated_relations.has_next,
            "has_prev": paginated_relations.has_prev,
            "page": paginated_relations.page,
            "pages": paginated_relations.pages,
            "total": paginated_relations.total,
        },
    }


@auth_blueprint.route("/auth/account/suspension", methods=["GET"])
@require_auth(scopes=["profile:read"], allow_suspended_user=True)
def get_user_suspension(
    auth_user: User,
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Get suspension if exists for authenticated user.

    Suspended user can access this endpoint.

    **Scope**: ``profile:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/account/suspension HTTP/1.1

    **Example responses**:

    - suspension exists:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "status": "success",
          "user_suspension": {
            "action_type": "user_suspension",
            "appeal": null,
            "comment": null,
            "created_at": "Wed, 04 Dec 2024 10:45:13 GMT",
            "id": "mmy3qPL3vcFuKJGfFBnCJV",
            "reason": "<SUSPENSION REASON>",
            "workout": null
          }
        }

    - no suspension:

    .. sourcecode:: http

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

        {
          "status": "not found",
          "message": "user account is not suspended"
        }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``user account is not suspended``
    """
    if auth_user.suspended_at is None or auth_user.suspension_action is None:
        return NotFoundErrorResponse("user account is not suspended")

    return {
        "status": "success",
        "user_suspension": auth_user.suspension_action.serialize(auth_user),
    }, 200


@auth_blueprint.route(
    "/auth/account/suspension/appeal",
    methods=["POST"],
)
@require_auth(scopes=["profile:write"], allow_suspended_user=True)
def appeal_user_suspension(
    auth_user: User,
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Appeal suspension for authenticated user.

    Suspended user can access this endpoint.

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/account/suspension/appeal HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "status": "success"
        }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :<json string text: text explaining appeal

    :statuscode 201: appeal for suspension created
    :statuscode 400:
        - ``no text provided``
        - ``you can appeal only once``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``user account is not suspended``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    if auth_user.suspended_at is None or auth_user.suspension_action is None:
        return NotFoundErrorResponse("user account is not suspended")

    text = request.get_json().get("text")
    if not text:
        return InvalidPayloadErrorResponse("no text provided")

    try:
        appeal = ReportActionAppeal(
            action_id=auth_user.suspension_action.id,
            user_id=auth_user.id,
            text=text,
        )
        db.session.add(appeal)
        db.session.commit()
        return {"status": "success"}, 201

    except exc.IntegrityError:
        return InvalidPayloadErrorResponse("you can appeal only once")
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route(
    "/auth/account/sanctions/<string:action_short_id>", methods=["GET"]
)
@require_auth(scopes=["profile:read"], allow_suspended_user=True)
def get_user_sanction(
    auth_user: User, action_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Get sanction for authenticated user.

    Suspended user can access this endpoint.

    **Scope**: ``profile:read``

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/account/sanctions/mmy3qPL3vcFuKJGfFBnCJV HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 SUCCESS
      Content-Type: application/json

        {
          "sanction": {
            "action_type": "user_suspension",
            "appeal": {
              "approved": null,
              "created_at": "Wed, 04 Dec 2024 10:49:00 GMT",
              "id": "7pDujhCVHyA4hv29JZQNgg",
              "reason": null,
              "text": "<APPEAL TEXT>",
              "updated_at": null
            },
            "comment": null,
            "created_at": "Wed, 04 Dec 2024 10:45:13 GMT",
            "id": "mmy3qPL3vcFuKJGfFBnCJV",
            "reason": "<SANCTION REASON>",
            "workout": null
          },
          "status": "success"
        }

    :param string action_short_id: suspension id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``no sanction found``
    """
    sanction = ReportAction.query.filter_by(
        uuid=decode_short_id(action_short_id), user_id=auth_user.id
    ).first()

    if not sanction:
        return NotFoundErrorResponse("no sanction found")

    return {
        "status": "success",
        "sanction": sanction.serialize(current_user=auth_user, full=True),
    }, 200


@auth_blueprint.route(
    "/auth/account/sanctions/<string:action_short_id>/appeal",
    methods=["POST"],
)
@require_auth(scopes=["profile:write"])
def appeal_user_sanction(
    auth_user: User, action_short_id: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Appeal a sanction

    **Scope**: ``profile:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/account/sanctions/6dxczvMrhkAR72shUz9Pwd/appeal HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

        {
          "status": "success"
        }

    :param string action_short_id: sanction id

    :<json string text: text explaining appeal

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 201: appeal created
    :statuscode 400:
        - ``no text provided``
        - ``you can appeal only once``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404: ``no sanction found``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    sanction = ReportAction.query.filter_by(
        uuid=decode_short_id(action_short_id), user_id=auth_user.id
    ).first()

    if not sanction:
        return NotFoundErrorResponse("no sanction found")

    if sanction.report.object_type == "comment" and not sanction.comment_id:
        return InvalidPayloadErrorResponse("comment has been deleted")

    if sanction.report.object_type == "workout" and not sanction.workout_id:
        return InvalidPayloadErrorResponse("workout has been deleted")

    text = request.get_json().get("text")
    if not text:
        return InvalidPayloadErrorResponse("no text provided")

    try:
        appeal = ReportActionAppeal(
            action_id=sanction.id,
            user_id=auth_user.id,
            text=text,
        )
        db.session.add(appeal)
        db.session.commit()
        return {"status": "success"}, 201

    except exc.IntegrityError:
        return InvalidPayloadErrorResponse("you can appeal only once")
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route("/auth/timezones", methods=["GET"])
def get_timezones() -> Tuple[Dict, int]:
    """
    Returns list of available time zones

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/timezones HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "timezones": [
          "Africa/Abidjan",
          "Africa/Accra",
          "Africa/Algiers",
          "Africa/Bissau",
          "Africa/Cairo",
          "...",
          "Pacific/Tahiti",
          "Pacific/Tarawa",
          "Pacific/Tongatapu",
          "Pacific/Wake",
          "Pacific/Wallis",
        ],
        "status": "success"
      }

    :statuscode 200: ``success``
    """
    return {"timezones": TIMEZONES, "status": "success"}, 200

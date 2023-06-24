import datetime
import os
import re
import secrets
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
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from fittrackee import appLog, db
from fittrackee.emails.tasks import (
    account_confirmation_email,
    email_updated_to_current_address,
    email_updated_to_new_address,
    password_change_email,
    reset_password_email,
)
from fittrackee.files import get_absolute_file_path
from fittrackee.oauth2.server import require_auth
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    PayloadTooLargeErrorResponse,
    UnauthorizedErrorResponse,
    get_error_response_if_file_is_invalid,
    handle_error_and_return_response,
)
from fittrackee.utils import get_readable_duration
from fittrackee.workouts.models import Sport

from .exceptions import UserControlsException, UserCreationException
from .models import BlacklistedToken, User, UserDataExport, UserSportPreference
from .tasks import export_data
from .utils.admin import UserManagerService
from .utils.controls import check_password, is_valid_email
from .utils.language import get_language
from .utils.token import decode_user_token

auth_blueprint = Blueprint('auth', __name__)

HEX_COLOR_REGEX = regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
NOT_FOUND_MESSAGE = 'the requested URL was not found on the server'


def send_account_confirmation_email(user: User) -> None:
    if current_app.config['CAN_SEND_EMAILS']:
        ui_url = current_app.config['UI_URL']
        email_data = {
            'username': user.username,
            'fittrackee_url': ui_url,
            'operating_system': request.user_agent.platform,  # type: ignore  # noqa
            'browser_name': request.user_agent.browser,  # type: ignore
            'account_confirmation_url': (
                f'{ui_url}/account-confirmation'
                f'?token={user.confirmation_token}'
            ),
        }
        user_data = {
            'language': get_language(user.language),
            'email': user.email,
        }
        account_confirmation_email.send(user_data, email_data)


@auth_blueprint.route('/auth/register', methods=['POST'])
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
    if not current_app.config.get('is_registration_enabled'):
        return ForbiddenErrorResponse('error, registration is disabled')

    post_data = request.get_json()
    if (
        not post_data
        or post_data.get('username') is None
        or post_data.get('email') is None
        or post_data.get('password') is None
        or post_data.get('accepted_policy') is None
    ):
        return InvalidPayloadErrorResponse()

    accepted_policy = post_data.get('accepted_policy') is True
    if not accepted_policy:
        return InvalidPayloadErrorResponse(
            'sorry, you must agree privacy policy to register'
        )

    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    language = get_language(post_data.get('language'))

    try:
        user_manager_service = UserManagerService(username=username)
        new_user, _ = user_manager_service.create_user(email, password)
        # if a user exists with same email address (returned new_user is None),
        # no error is returned since a user has to confirm his email to
        # activate his account
        if new_user:
            new_user.language = language
            new_user.accepted_policy_date = datetime.datetime.utcnow()
            db.session.add(new_user)
            db.session.commit()

            send_account_confirmation_email(new_user)

        return {'status': 'success'}, 200
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


@auth_blueprint.route('/auth/login', methods=['POST'])
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
    email = post_data.get('email', '')
    password = post_data.get('password')
    try:
        user = User.query.filter(
            func.lower(User.email) == func.lower(email),
            User.is_active == True,  # noqa
        ).first()
        if user and user.check_password(password):
            # generate auth token
            auth_token = user.encode_auth_token(user.id)
            return {
                'status': 'success',
                'message': 'successfully logged in',
                'auth_token': auth_token,
            }
        return UnauthorizedErrorResponse('invalid credentials')
    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/profile', methods=['GET'])
@require_auth(scopes=['profile:read'])
def get_authenticated_user_profile(
    auth_user: User,
) -> Union[Dict, HttpResponse]:
    """
    Get authenticated user info (profile, account, preferences).

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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "nb_sports": 3,
          "nb_workouts": 6,
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
          "use_raw_gpx_speed": false,
          "username": "sam",
          "weekm": false
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
    return {'status': 'success', 'data': auth_user.serialize(auth_user)}


@auth_blueprint.route('/auth/profile/edit', methods=['POST'])
@require_auth(scopes=['profile:write'])
def edit_user(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Edit authenticated user profile.

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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "nb_sports": 3,
          "nb_workouts": 6,
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
          "use_raw_gpx_speed": false,
          "username": "sam"
          "weekm": true,
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
        'first_name',
        'last_name',
        'bio',
        'birth_date',
        'location',
    }
    if not post_data or not post_data.keys() >= user_mandatory_data:
        return InvalidPayloadErrorResponse()

    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    bio = post_data.get('bio')
    birth_date = post_data.get('birth_date')
    location = post_data.get('location')

    try:
        auth_user.first_name = first_name
        auth_user.last_name = last_name
        auth_user.bio = bio
        auth_user.location = location
        auth_user.birth_date = (
            datetime.datetime.strptime(birth_date, '%Y-%m-%d')
            if birth_date
            else None
        )
        db.session.commit()

        return {
            'status': 'success',
            'message': 'user profile updated',
            'data': auth_user.serialize(auth_user),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/profile/edit/account', methods=['PATCH'])
@require_auth(scopes=['profile:write'])
def update_user_account(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Update authenticated user email and password.

    It sends emails if sending is enabled:

    - Password change
    - Email change:

      - one to the current address to inform user
      - another one to the new address to confirm it.

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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "dd/MM/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "nb_sports": 3,
          "nb_workouts": 6,
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
          "use_raw_gpx_speed": false,
          "username": "sam"
          "weekm": true,
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
    email_to_confirm = data.get('email')
    if not email_to_confirm:
        return InvalidPayloadErrorResponse('email is missing')
    current_password = data.get('password')
    if not current_password:
        return InvalidPayloadErrorResponse('current password is missing')
    if not auth_user.check_password(current_password):
        return UnauthorizedErrorResponse('invalid credentials')

    new_password = data.get('new_password')
    error_messages = ''
    try:
        if email_to_confirm != auth_user.email:
            if is_valid_email(email_to_confirm):
                if current_app.config['CAN_SEND_EMAILS']:
                    auth_user.email_to_confirm = email_to_confirm
                    auth_user.confirmation_token = secrets.token_urlsafe(30)
                else:
                    auth_user.email = email_to_confirm
                    auth_user.confirmation_token = None
            else:
                error_messages = 'email: valid email must be provided\n'

        if new_password is not None:
            error_messages += check_password(new_password)
            if error_messages == '':
                hashed_password = auth_user.generate_password_hash(
                    new_password
                )
                auth_user.password = hashed_password

        if error_messages != '':
            return InvalidPayloadErrorResponse(error_messages)

        db.session.commit()

        if current_app.config['CAN_SEND_EMAILS']:
            ui_url = current_app.config['UI_URL']
            user_data = {
                'language': get_language(auth_user.language),
                'email': auth_user.email,
            }
            data = {
                'username': auth_user.username,
                'fittrackee_url': ui_url,
                'operating_system': request.user_agent.platform,
                'browser_name': request.user_agent.browser,
            }

            if new_password is not None:
                password_change_email.send(user_data, data)

            if (
                auth_user.email_to_confirm is not None
                and auth_user.email_to_confirm != auth_user.email
            ):
                email_data = {
                    **data,
                    **{'new_email_address': email_to_confirm},
                }
                email_updated_to_current_address.send(user_data, email_data)

                email_data = {
                    **data,
                    **{
                        'email_confirmation_url': (
                            f'{ui_url}/email-update'
                            f'?token={auth_user.confirmation_token}'
                        )
                    },
                }
                user_data = {
                    **user_data,
                    **{'email': auth_user.email_to_confirm},
                }
                email_updated_to_new_address.send(user_data, email_data)

        return {
            'status': 'success',
            'message': 'user account updated',
            'data': auth_user.serialize(auth_user),
        }

    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/profile/edit/preferences', methods=['POST'])
@require_auth(scopes=['profile:write'])
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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "date_format": "MM/dd/yyyy",
          "display_ascent": true,
          "email": "sam@example.com",
          "email_to_confirm": null,
          "first_name": null,
          "imperial_units": false,
          "is_active": true,
          "language": "en",
          "last_name": null,
          "location": null,
          "nb_sports": 3,
          "nb_workouts": 6,
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
          "use_raw_gpx_speed": true,
          "username": "sam"
          "weekm": true,
        },
        "message": "user preferences updated",
        "status": "success"
      }

    :<json string date_format: the format used to display dates in the app
    :<json boolean display_ascent: display highest ascent records and total
    :<json boolean imperial_units: display distance in imperial units
    :<json string language: language preferences
    :<json boolean start_elevation_at_zero: do elevation plots start at zero?
    :<json string timezone: user time zone
    :<json boolean use_raw_gpx_speed: Use unfiltered gpx to calculate speeds
    :<json boolean weekm: does week start on Monday?

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
        'date_format',
        'display_ascent',
        'imperial_units',
        'language',
        'start_elevation_at_zero',
        'timezone',
        'use_raw_gpx_speed',
        'weekm',
    }
    if not post_data or not post_data.keys() >= user_mandatory_data:
        return InvalidPayloadErrorResponse()

    date_format = post_data.get('date_format')
    display_ascent = post_data.get('display_ascent')
    imperial_units = post_data.get('imperial_units')
    language = get_language(post_data.get('language'))
    start_elevation_at_zero = post_data.get('start_elevation_at_zero')
    use_raw_gpx_speed = post_data.get('use_raw_gpx_speed')
    timezone = post_data.get('timezone')
    weekm = post_data.get('weekm')

    try:
        auth_user.date_format = date_format
        auth_user.display_ascent = display_ascent
        auth_user.imperial_units = imperial_units
        auth_user.language = language
        auth_user.start_elevation_at_zero = start_elevation_at_zero
        auth_user.timezone = timezone
        auth_user.use_raw_gpx_speed = use_raw_gpx_speed
        auth_user.weekm = weekm
        db.session.commit()

        return {
            'status': 'success',
            'message': 'user preferences updated',
            'data': auth_user.serialize(auth_user),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/profile/edit/sports', methods=['POST'])
@require_auth(scopes=['profile:write'])
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
          "is_active": true,
          "sport_id": 1,
          "stopped_speed_threshold": 1,
          "user_id": 1
        },
        "message": "user sport preferences updated",
        "status": "success"
      }

    :<json string color: valid hexadecimal color
    :<json boolean is_active: is sport available when adding a workout
    :<json float stopped_speed_threshold: stopped speed threshold used by gpxpy

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``user sport preferences updated``
    :statuscode 400:
        - ``invalid payload``
        - ``invalid hexadecimal color``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 404: ``sport does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    post_data = request.get_json()
    if (
        not post_data
        or 'sport_id' not in post_data
        or len(post_data.keys()) == 1
    ):
        return InvalidPayloadErrorResponse()

    sport_id = post_data.get('sport_id')
    sport = Sport.query.filter_by(id=sport_id).first()
    if not sport:
        return NotFoundErrorResponse('sport does not exist')

    color = post_data.get('color')
    is_active = post_data.get('is_active')
    stopped_speed_threshold = post_data.get('stopped_speed_threshold')

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
                return InvalidPayloadErrorResponse('invalid hexadecimal color')
            user_sport.color = color
        if is_active is not None:
            user_sport.is_active = is_active
        if stopped_speed_threshold:
            user_sport.stopped_speed_threshold = stopped_speed_threshold
        db.session.commit()

        return {
            'status': 'success',
            'message': 'user sport preferences updated',
            'data': user_sport.serialize(),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route(
    '/auth/profile/reset/sports/<sport_id>', methods=['DELETE']
)
@require_auth(scopes=['profile:write'])
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
    :statuscode 404: ``sport does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    sport = Sport.query.filter_by(id=sport_id).first()
    if not sport:
        return NotFoundErrorResponse('sport does not exist')

    try:
        user_sport = UserSportPreference.query.filter_by(
            user_id=auth_user.id,
            sport_id=sport_id,
        ).first()
        if user_sport:
            db.session.delete(user_sport)
            db.session.commit()
        return {'status': 'no content'}, 204

    # handler errors
    except (exc.IntegrityError, exc.OperationalError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/picture', methods=['POST'])
@require_auth(scopes=['profile:write'])
def edit_picture(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Update authenticated user picture.

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
            'picture', request
        )
    except RequestEntityTooLarge as e:
        appLog.error(e)
        return PayloadTooLargeErrorResponse(
            file_type='picture',
            file_size=request.content_length,
            max_size=current_app.config['MAX_CONTENT_LENGTH'],
        )
    if response_object:
        return response_object

    file = request.files['file']
    filename = secure_filename(file.filename)  # type: ignore
    dirpath = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'pictures', str(auth_user.id)
    )
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    absolute_picture_path = os.path.join(dirpath, filename)
    relative_picture_path = os.path.join(
        'pictures', str(auth_user.id), filename
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
            'status': 'success',
            'message': 'user picture updated',
        }

    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            e, message='error during picture update', status='fail', db=db
        )


@auth_blueprint.route('/auth/picture', methods=['DELETE'])
@require_auth(scopes=['profile:write'])
def del_picture(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete authenticated user picture.

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
    try:
        picture_path = get_absolute_file_path(auth_user.picture)
        if os.path.isfile(picture_path):
            os.remove(picture_path)
        auth_user.picture = None
        db.session.commit()
        return {'status': 'no content'}, 204
    except (exc.IntegrityError, ValueError) as e:
        return handle_error_and_return_response(
            e, message='error during picture deletion', status='fail', db=db
        )


@auth_blueprint.route('/auth/password/reset-request', methods=['POST'])
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
    if not current_app.config['CAN_SEND_EMAILS']:
        return NotFoundErrorResponse(NOT_FOUND_MESSAGE)

    post_data = request.get_json()
    if not post_data or post_data.get('email') is None:
        return InvalidPayloadErrorResponse()
    email = post_data.get('email')

    user = User.query.filter(User.email == email).first()
    if user:
        password_reset_token = user.encode_password_reset_token(user.id)
        ui_url = current_app.config['UI_URL']
        user_language = get_language(user.language)
        email_data = {
            'expiration_delay': get_readable_duration(
                current_app.config['PASSWORD_TOKEN_EXPIRATION_SECONDS'],
                user_language,
            ),
            'username': user.username,
            'password_reset_url': (
                f'{ui_url}/password-reset?token={password_reset_token}'  # noqa
            ),
            'fittrackee_url': ui_url,
            'operating_system': request.user_agent.platform,  # type: ignore
            'browser_name': request.user_agent.browser,  # type: ignore
        }
        user_data = {
            'language': user_language,
            'email': user.email,
        }
        reset_password_email.send(user_data, email_data)
    return {
        'status': 'success',
        'message': 'password reset request processed',
    }


@auth_blueprint.route('/auth/password/update', methods=['POST'])
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
        or post_data.get('password') is None
        or post_data.get('token') is None
    ):
        return InvalidPayloadErrorResponse()
    password = post_data.get('password')
    token = post_data.get('token')

    try:
        user_id = decode_user_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return UnauthorizedErrorResponse()

    message = check_password(password)
    if message != '':
        return InvalidPayloadErrorResponse(message)

    user = User.query.filter(User.id == user_id).first()
    if not user:
        return UnauthorizedErrorResponse()
    try:
        user.password = user.generate_password_hash(password)
        db.session.commit()

        if current_app.config['CAN_SEND_EMAILS']:
            password_change_email.send(
                {
                    'language': get_language(user.language),
                    'email': user.email,
                },
                {
                    'username': user.username,
                    'fittrackee_url': current_app.config['UI_URL'],
                    'operating_system': request.user_agent.platform,
                    'browser_name': request.user_agent.browser,
                },
            )

        return {
            'status': 'success',
            'message': 'password updated',
        }
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/email/update', methods=['POST'])
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
    if not post_data or post_data.get('token') is None:
        return InvalidPayloadErrorResponse()
    token = post_data.get('token')

    try:
        user = User.query.filter_by(confirmation_token=token).first()

        if not user:
            return InvalidPayloadErrorResponse()

        user.email = user.email_to_confirm
        user.email_to_confirm = None
        user.confirmation_token = None

        db.session.commit()

        response = {
            'status': 'success',
            'message': 'email updated',
        }

        return response

    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/account/confirm', methods=['POST'])
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
    if not post_data or post_data.get('token') is None:
        return InvalidPayloadErrorResponse()
    token = post_data.get('token')

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
            'status': 'success',
            'message': 'account confirmation successful',
            'auth_token': auth_token,
        }
        return response

    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/account/resend-confirmation', methods=['POST'])
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
    if not current_app.config['CAN_SEND_EMAILS']:
        return NotFoundErrorResponse(NOT_FOUND_MESSAGE)

    post_data = request.get_json()
    if not post_data or post_data.get('email') is None:
        return InvalidPayloadErrorResponse()
    email = post_data.get('email')

    try:
        user = User.query.filter_by(email=email, is_active=False).first()
        if user:
            user.confirmation_token = secrets.token_urlsafe(30)
            db.session.commit()

            send_account_confirmation_email(user)

        response = {
            'status': 'success',
            'message': 'confirmation email resent',
        }
        return response
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/logout', methods=['POST'])
@require_auth()
def logout_user(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    User logout.
    If a valid token is provided, it will be blacklisted.

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
    auth_token = request.headers.get('Authorization', '').split(' ')[1]
    try:
        db.session.add(BlacklistedToken(token=auth_token))
        db.session.commit()
    except Exception:
        return {
            'status': 'error',
            'message': 'error on token blacklist',
        }, 500

    return {
        'status': 'success',
        'message': 'successfully logged out',
    }, 200


@auth_blueprint.route('/auth/account/privacy-policy', methods=['POST'])
@require_auth()
def accept_privacy_policy(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    The authenticated user accepts the privacy policy.

    **Example request**:

    .. sourcecode:: http

      POST /auth/account/privacy-policy HTTP/1.1
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
    if not post_data or not post_data.get('accepted_policy'):
        return InvalidPayloadErrorResponse()

    try:
        if post_data.get('accepted_policy') is True:
            auth_user.accepted_policy_date = datetime.datetime.utcnow()
            db.session.commit()
            return {"status": "success"}
        else:
            return InvalidPayloadErrorResponse()
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/account/export/request', methods=['POST'])
@require_auth()
def request_user_data_export(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Request a data export for authenticated user.

    **Example request**:

    .. sourcecode:: http

      POST /auth/account/export/request HTTP/1.1
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
    existing_export_request = UserDataExport.query.filter_by(
        user_id=auth_user.id
    ).first()
    if existing_export_request:
        if not existing_export_request.completed:
            return InvalidPayloadErrorResponse("ongoing request exists")

        export_expiration = current_app.config["DATA_EXPORT_EXPIRATION"]
        if existing_export_request.created_at > (
            datetime.datetime.utcnow()
            - datetime.timedelta(hours=export_expiration)
        ):
            return InvalidPayloadErrorResponse(
                "completed request already exists"
            )

    try:
        if existing_export_request:
            db.session.delete(existing_export_request)
            db.session.flush()
        export_request = UserDataExport(user_id=auth_user.id)
        db.session.add(export_request)
        db.session.commit()

        export_data.send(export_request_id=export_request.id)

        return {"status": "success", "request": export_request.serialize()}
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/account/export', methods=['GET'])
@require_auth()
def get_user_data_export(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    Get a data export info for authenticated user if a request exists.

    It returns:

    - export creation date
    - export status (``in_progress``, ``successful`` and ``errored``)
    - file name and size (in bytes) when export is successful

    **Example request**:

    .. sourcecode:: http

      GET /auth/account/export HTTP/1.1
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
    export_request = UserDataExport.query.filter_by(
        user_id=auth_user.id
    ).first()
    return {
        "status": "success",
        "request": export_request.serialize() if export_request else None,
    }


@auth_blueprint.route(
    '/auth/account/export/<string:file_name>', methods=['GET']
)
@require_auth()
def download_data_export(
    auth_user: User, file_name: str
) -> Union[Response, HttpResponse]:
    """
    Download a data export archive

    **Example request**:

    .. sourcecode:: http

      GET /auth/account/export/download/archive_rgjsR3fHr5Yp.zip HTTP/1.1
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
    export_request = UserDataExport.query.filter_by(
        user_id=auth_user.id
    ).first()
    if (
        not export_request
        or not export_request.completed
        or export_request.file_name != file_name
    ):
        return DataNotFoundErrorResponse(
            data_type="archive", message="file not found"
        )

    return send_from_directory(
        f"{current_app.config['UPLOAD_FOLDER']}/exports/{auth_user.id}",
        export_request.file_name,
        mimetype='application/zip',
        as_attachment=True,
    )

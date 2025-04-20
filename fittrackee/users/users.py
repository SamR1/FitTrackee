import os
import shutil
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from flask import Blueprint, current_app, request, send_file
from sqlalchemy import and_, asc, desc, exc, func, nullslast, or_

from fittrackee import appLog, db, limiter
from fittrackee.dates import get_readable_duration
from fittrackee.emails.tasks import send_email
from fittrackee.equipments.models import Equipment
from fittrackee.files import get_absolute_file_path
from fittrackee.oauth2.server import require_auth
from fittrackee.reports.models import ReportAction
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Record, Workout, WorkoutSegment

from .exceptions import (
    BlockUserException,
    FollowRequestAlreadyRejectedError,
    InvalidEmailException,
    InvalidUserRole,
    NotExistingFollowRequestError,
    OwnerException,
    UserNotFoundException,
)
from .models import FollowRequest, User, UserSportPreference, UserTask
from .roles import UserRole
from .users_service import UserManagerService
from .utils.language import get_language

if TYPE_CHECKING:
    from sqlalchemy.sql.expression import (
        BinaryExpression,
        ColumnElement,
        UnaryExpression,
    )

users_blueprint = Blueprint("users", __name__)

ACTIONS_PER_PAGE = 5
USERS_PER_PAGE = 10
EMPTY_USERS_RESPONSE = {
    "status": "success",
    "data": {"users": []},
    "pagination": {
        "has_next": False,
        "has_prev": False,
        "page": 1,
        "pages": 0,
        "total": 0,
    },
}
WORKOUTS_PER_PAGE = 5


def _get_value_depending_on_user_rights(
    params: Dict, key: str, auth_user: Optional[User]
) -> str:
    value = params.get(key, "false").lower()
    if not auth_user or not auth_user.has_admin_rights:
        value = "false"
    return value


def get_users_list(auth_user: User) -> Dict:
    params = request.args.copy()

    query = params.get("q")
    page = int(params.get("page", 1))
    per_page = int(params.get("per_page", USERS_PER_PAGE))
    if per_page > 50:
        per_page = 50
    column = params.get("order_by", "username")
    user_column = getattr(User, column)
    order = params.get("order", "asc")
    order_clauses: List["UnaryExpression"] = [
        asc(user_column) if order == "asc" else desc(user_column)
    ]
    if column != "username":
        order_clauses.append(User.username.asc())
    if column == "suspended_at":
        order_clauses = [nullslast(order_clauses[0])]
    with_inactive = _get_value_depending_on_user_rights(
        params, "with_inactive", auth_user
    )
    with_hidden_users = _get_value_depending_on_user_rights(
        params, "with_hidden", auth_user
    )
    with_suspended_users = _get_value_depending_on_user_rights(
        params, "with_suspended", auth_user
    )
    with_following = params.get("with_following", "false").lower()
    following_user_ids = (
        auth_user.get_following_user_ids() if with_following == "true" else []
    )

    filters: List[Union["ColumnElement", "BinaryExpression"]] = []
    if query:
        filters.append(User.username.ilike("%" + query + "%"))
    if with_inactive != "true":
        filters.append(User.is_active == True)  # noqa
    if with_hidden_users != "true":
        filters.append(
            (
                or_(
                    User.hide_profile_in_users_directory == False,  # noqa
                    and_(
                        User.id.in_(following_user_ids),
                        User.hide_profile_in_users_directory == True,  # noqa
                    ),
                )
            ),
        )
    if with_suspended_users != "true":
        filters.append(User.suspended_at == None)  # noqa
    users_pagination = (
        User.query.filter(*filters)
        .order_by(*order_clauses)
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    users = users_pagination.items
    return {
        "status": "success",
        "data": {
            "users": [user.serialize(current_user=auth_user) for user in users]
        },
        "pagination": {
            "has_next": users_pagination.has_next,
            "has_prev": users_pagination.has_prev,
            "page": users_pagination.page,
            "pages": users_pagination.pages,
            "total": users_pagination.total,
        },
    }


@users_blueprint.route("/users", methods=["GET"])
@require_auth(scopes=["users:read"])
def get_users(auth_user: User) -> Dict:
    """
    Get all users.
    If authenticated user has admin rights, users email is returned.

    It returns user preferences only for authenticated user.

    **Scope**: ``users:read``

    **Example request**:

    - without parameters:

    .. sourcecode:: http

      GET /api/users HTTP/1.1
      Content-Type: application/json

    - with some query parameters:

    .. sourcecode:: http

      GET /api/users?order_by=workouts_count&par_page=5  HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "users": [
            {
              "admin": true,
              "bio": null,
              "birth_date": null,
              "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
              "email": "admin@example.com",
              "first_name": null,
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_followed_by": "false",
              "last_name": null,
              "location": null,
              "map_visibility": "private",
              "nb_sports": 3,
              "nb_workouts": 6,
              "picture": false,
              "records": [
                {
                  "id": 9,
                  "record_type": "AS",
                  "sport_id": 1,
                  "user": "admin",
                  "value": 18,
                  "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                  "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
                },
                {
                  "id": 10,
                  "record_type": "FD",
                  "sport_id": 1,
                  "user": "admin",
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
                  "user": "admin",
                  "value": "1:01:00",
                  "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                  "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
                },
                {
                  "id": 12,
                  "record_type": "MS",
                  "sport_id": 1,
                  "user": "admin",
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
              "total_distance": 67.895,
              "total_duration": "6:50:27",
              "username": "admin",
              "workouts_visibility": "private"
            },
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Sat, 20 Jul 2019 11:27:03 GMT",
              "email": "sam@example.com",
              "first_name": null,
              "followers": 0,
              "following": 0,
              "follows": "false",
              "is_followed_by": "false",
              "last_name": null,
              "location": null,
              "map_visibility": "private",
              "nb_sports": 0,
              "nb_workouts": 0,
              "picture": false,
              "records": [],
              "sports_list": [],
              "total_distance": 0,
              "total_duration": "0:00:00",
              "username": "sam",
              "workouts_visibility": "private"
            }
          ]
        },
        "status": "success"
      }

    :query integer page: page if using pagination (default: 1)
    :query integer per_page: number of users per page (default: 10, max: 50)
    :query string q: query on user name
    :query string order: sorting order: ``asc``, ``desc`` (default: ``asc``)
    :query string order_by: sorting criteria: ``username``, ``created_at``,
                            ``workouts_count``, ``role``, ``is_active``
                            (default: ``username``)
    :query boolean with_following: returns hidden users followed by user if
           true
    :query boolean with_hidden_users: returns hidden users if ``true`` (only if
           authenticated user has administration rights - for users
           administration)
    :query boolean with_inactive: returns inactive users if ``true`` (only if
           authenticated user has administration rights - for users
           administration)
    :query boolean with_suspended: returns suspended users if ``true`` (only if
           authenticated user has administration rights - for users
           administration)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``

    """
    return get_users_list(auth_user)


@users_blueprint.route("/users/<user_name>", methods=["GET"])
@require_auth(scopes=["users:read"], optional_auth_user=True)
def get_single_user(
    auth_user: Optional[User], user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get single user details.
    If a user is authenticated, it returns relationships.
    If authenticated user has admin rights, user email is returned.

    It returns user preferences only for authenticated user.

    **Scope**: ``users:read`` for Oauth 2.0 client

    **Example request**:

    .. sourcecode:: http

      GET /api/users/admin HTTP/1.1
      Content-Type: application/json

    **Example response**:

    - when a user is authenticated:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": [
          {
            "admin": true,
            "bio": null,
            "birth_date": null,
            "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
            "email": "admin@example.com",
            "first_name": null,
            "followers": 0,
            "following": 0,
            "follows": "false",
            "is_followed_by": "false",
            "last_name": null,
            "location": null,
            "map_visibility": "private",
            "nb_sports": 3,
            "nb_workouts": 6,
            "picture": false,
            "records": [
              {
                "id": 9,
                "record_type": "AS",
                "sport_id": 1,
                "user": "admin",
                "value": 18,
                "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
              },
              {
                "id": 10,
                "record_type": "FD",
                "sport_id": 1,
                "user": "admin",
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
                "user": "admin",
                "value": "1:01:00",
                "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
              },
              {
                "id": 12,
                "record_type": "MS",
                "sport_id": 1,
                "user": "admin",
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
            "total_distance": 67.895,
            "total_duration": "6:50:27",
            "username": "admin",
            "workouts_visibility": "private"
          }
        ],
        "status": "success"
      }

    - when no authentication:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": [
          {
            "admin": true,
            "bio": null,
            "birth_date": null,
            "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
            "email": "admin@example.com",
            "first_name": null,
            "followers": 0,
            "following": 0,
            "follows": "false",
            "is_followed_by": "false",
            "last_name": null,
            "location": null,
            "map_visibility": "private",
            "nb_workouts": 6,
            "picture": false,
            "username": "admin",
            "workouts_visibility": "private"
          }
        ],
        "status": "success"
      }

    :param integer user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token if user is authenticated

    :statuscode 200: ``success``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``
    """
    try:
        user = User.query.filter(
            func.lower(User.username) == func.lower(user_name),
        ).first()
        if user:
            if (
                not auth_user or not auth_user.has_admin_rights
            ) and not user.is_active:
                return UserNotFoundErrorResponse()
            return {
                "status": "success",
                "data": {
                    "users": [
                        user.serialize(current_user=auth_user, light=False)
                    ]
                },
            }
    except (ValueError, UserNotFoundException):
        pass
    return UserNotFoundErrorResponse()


@users_blueprint.route("/users/<user_name>/picture", methods=["GET"])
@limiter.exempt
def get_picture(user_name: str) -> Any:
    """get user picture

    **Example request**:

    .. sourcecode:: http

      GET /api/users/admin/picture HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: image/jpeg

    :param integer user_name: user name

    :statuscode 200: ``success``
    :statuscode 404:
        - ``user does not exist``
        - ``No picture.``

    """
    try:
        user = User.query.filter(
            func.lower(User.username) == func.lower(user_name),
        ).first()
        if not user:
            return UserNotFoundErrorResponse()
        if user.picture is not None:
            picture_path = get_absolute_file_path(user.picture)
            return send_file(picture_path)
    except UserNotFoundException:
        return UserNotFoundErrorResponse()
    except Exception:  # nosec
        pass
    return NotFoundErrorResponse("No picture.")


@users_blueprint.route("/users/<user_name>", methods=["PATCH"])
@require_auth(scopes=["users:write"], role=UserRole.ADMIN)
def update_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Update user account.

    - add/remove admin rights (regardless user account status)
    - reset password (and send email to update user password,
      if sending enabled)
    - update user email (and send email to new user email, if sending enabled)
    - activate account for an inactive user
    - deactivate account after report.

    **Scope**: ``users:write``

    **Minimum role**: Administrator

    **Example request**:

    .. sourcecode:: http

      PATCH /api/users/<user_name> HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": [
          {
            "admin": true,
            "bio": null,
            "birth_date": null,
            "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
            "email": "admin@example.com",
            "first_name": null,
            "followers": 0,
            "following": 0,
            "follows": "false",
            "is_followed_by": "false",
            "last_name": null,
            "location": null,
            "map_visibility": "private",
            "nb_workouts": 6,
            "nb_sports": 3,
            "picture": false,
            "records": [
              {
                "id": 9,
                "record_type": "AS",
                "sport_id": 1,
                "user": "admin",
                "value": 18,
                "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
              },
              {
                "id": 10,
                "record_type": "FD",
                "sport_id": 1,
                "user": "admin",
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
                "user": "admin",
                "value": "1:01:00",
                "workout_date": "Sun, 07 Jul 2019 08:00:00 GMT",
                "workout_id": "hvYBqYBRa7wwXpaStWR4V2"
              },
              {
                "id": 12,
                "record_type": "MS",
                "sport_id": 1,
                "user": "admin",
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
            "total_distance": 67.895,
            "total_duration": "6:50:27",
            "username": "admin",
            "workouts_visibility": "private"
          }
        ],
        "status": "success"
      }

    :param string user_name: user name

    :<json boolean activate: (de-)activate user account
    :<json boolean role: user role (``user``, ``admin``, ``moderator``).
                   ``owner`` can only be set via **CLI**.
    :<json boolean new_email: new user email
    :<json boolean reset_password: reset user password

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: ``success``
    :statuscode 400:
        - ``invalid payload``
        - ``invalid role``
        - ``valid email must be provided``
        - ``new email must be different than current email``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``
    """
    user_data = request.get_json()
    if not user_data:
        return InvalidPayloadErrorResponse()

    activate = user_data.get("activate")
    if activate is False and user_name == auth_user.username:
        return ForbiddenErrorResponse()

    role = user_data.get("role")
    if role == "owner":
        return InvalidPayloadErrorResponse(
            "'owner' can not be set via API, please user CLI instead"
        )

    try:
        reset_password = user_data.get("reset_password", False)
        new_email = user_data.get("new_email")
        user_manager_service = UserManagerService(
            username=user_name, moderator_id=auth_user.id
        )
        user, _, _, _ = user_manager_service.update(
            role=role,
            activate=user_data.get("activate"),
            reset_password=reset_password,
            new_email=new_email,
            with_confirmation=current_app.config["CAN_SEND_EMAILS"],
            raise_error_on_owner=True,
        )

        if current_app.config["CAN_SEND_EMAILS"]:
            user_language = get_language(user.language)
            fittrackee_url = current_app.config["UI_URL"]
            if reset_password:
                user_data = {
                    "language": user_language,
                    "email": user.email,
                }
                send_email.send(
                    user_data,
                    email_data={
                        "username": user.username,
                        "fittrackee_url": fittrackee_url,
                    },
                    template="password_change",
                )
                password_reset_token = user.encode_password_reset_token(
                    user.id
                )
                send_email.send(
                    user_data,
                    email_data={
                        "expiration_delay": get_readable_duration(
                            current_app.config[
                                "PASSWORD_TOKEN_EXPIRATION_SECONDS"
                            ],
                            user_language,
                        ),
                        "username": user.username,
                        "password_reset_url": (
                            f"{fittrackee_url}/password-reset?"
                            f"token={password_reset_token}"
                        ),
                        "fittrackee_url": fittrackee_url,
                    },
                    template="password_reset_request",
                )

            if new_email:
                user_data = {
                    "language": user_language,
                    "email": user.email_to_confirm,
                }
                email_data = {
                    "username": user.username,
                    "fittrackee_url": fittrackee_url,
                    "email_confirmation_url": (
                        f"{fittrackee_url}/email-update"
                        f"?token={user.confirmation_token}"
                    ),
                }
                send_email.send(
                    user_data, email_data, template="email_update_to_new_email"
                )

        return {
            "status": "success",
            "data": {
                "users": [user.serialize(current_user=auth_user, light=False)]
            },
        }
    except UserNotFoundException:
        return UserNotFoundErrorResponse()
    except (InvalidEmailException, InvalidUserRole, OwnerException) as e:
        return InvalidPayloadErrorResponse(str(e))
    except (TypeError, exc.StatementError) as e:
        return handle_error_and_return_response(e, db=db)


@users_blueprint.route("/users/<user_name>", methods=["DELETE"])
@require_auth(scopes=["users:write"], allow_suspended_user=True)
def delete_user(
    auth_user: User, user_name: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete a user account.

    A user can only delete his own account.

    A user with admin rights can delete all accounts except his account if
    he is the only user with admin rights.
    Only owner can delete his own account.

    Suspended user can access this endpoint.

    **Scope**: ``users:write``

    **Example request**:

    .. sourcecode:: http

      DELETE /api/users/john_doe HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 204 NO CONTENT
      Content-Type: application/json

    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 204: user account deleted
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you can not delete your account, no other user has admin rights``
    :statuscode 404:
        - ``user does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    try:
        user = User.query.filter(
            func.lower(User.username) == func.lower(user_name),
        ).first()
        if not user:
            return UserNotFoundErrorResponse()
        if user.id != auth_user.id and user.role == UserRole.OWNER.value:
            return ForbiddenErrorResponse("you can not delete owner account")

        if user.id != auth_user.id and not auth_user.has_admin_rights:
            return ForbiddenErrorResponse()
        if (
            user.has_admin_rights is True
            and User.query.filter(User.role >= UserRole.ADMIN.value).count()
            == 1
        ):
            return ForbiddenErrorResponse(
                "you can not delete your account, "
                "no other user has admin rights"
            )

        db.session.query(UserSportPreference).filter(
            UserSportPreference.user_id == user.id
        ).delete()
        db.session.query(Record).filter(Record.user_id == user.id).delete()
        # delete all equipment associated with this user
        db.session.query(Equipment).filter(
            Equipment.user_id == user.id
        ).delete()
        db.session.query(WorkoutSegment).filter(
            WorkoutSegment.workout_id == Workout.id, Workout.user_id == user.id
        ).delete(synchronize_session=False)
        db.session.query(Workout).filter(Workout.user_id == user.id).delete()
        db.session.query(UserTask).filter(UserTask.user_id == user.id).delete()
        db.session.flush()
        user_picture = user.picture
        db.session.delete(user)
        db.session.commit()
        if user_picture:
            picture_path = get_absolute_file_path(user.picture)
            if os.path.isfile(picture_path):
                os.remove(picture_path)
        shutil.rmtree(
            get_absolute_file_path(f"exports/{user.id}"),
            ignore_errors=True,
        )
        shutil.rmtree(
            get_absolute_file_path(f"workouts/{user.id}"),
            ignore_errors=True,
        )
        shutil.rmtree(
            get_absolute_file_path(f"pictures/{user.id}"),
            ignore_errors=True,
        )
        return {"status": "no content"}, 204
    except (
        exc.IntegrityError,
        exc.OperationalError,
        ValueError,
        OSError,
    ) as e:
        return handle_error_and_return_response(e, db=db)


@users_blueprint.route("/users/<user_name>/follow", methods=["POST"])
@require_auth(scopes=["follow:write"])
def follow_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Send a follow request to a user.

    **Scope**: ``follow:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/users/john_doe/follow HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "message": "Follow request to user 'john_doe' is sent.",
      }


    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    successful_response_dict = {
        "status": "success",
        "message": f"Follow request to user '{user_name}' is sent.",
    }

    target_user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not target_user:
        appLog.error(
            f"Error when following a user: user {user_name} not found"
        )
        return UserNotFoundErrorResponse()

    if auth_user.is_blocked_by(target_user):
        return InvalidPayloadErrorResponse("you can not follow this user")

    try:
        auth_user.send_follow_request_to(target_user)
    except FollowRequestAlreadyRejectedError:
        return ForbiddenErrorResponse()
    return successful_response_dict


@users_blueprint.route("/users/<user_name>/unfollow", methods=["POST"])
@require_auth(scopes=["follow:write"])
def unfollow_user(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Unfollow a user.

    **Scope**: ``follow:write``

    **Example request**:

    .. sourcecode:: http

      POST /api/users/john_doe/unfollow HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success",
        "message": "Undo for a follow request to user 'john_doe' is sent.",
      }


    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``
    :statuscode 500: ``error, please try again or contact the administrator``

    """
    successful_response_dict = {
        "status": "success",
        "message": f"Undo for a follow request to user '{user_name}' is sent.",
    }

    target_user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not target_user:
        appLog.error(
            f"Error when following a user: user {user_name} not found"
        )
        return UserNotFoundErrorResponse()

    try:
        auth_user.unfollows(target_user)
    except NotExistingFollowRequestError:
        return NotFoundErrorResponse(message="relationship does not exist")
    return successful_response_dict


def get_user_relationships(
    auth_user: User, user_name: str, relation: str
) -> Union[Dict, HttpResponse]:
    params = request.args.copy()
    try:
        page = int(params.get("page", 1))
    except ValueError:
        page = 1

    user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not user:
        return UserNotFoundErrorResponse()

    relations_object = (
        user.followers if relation == "followers" else user.following
    )

    paginated_relations = relations_object.order_by(
        FollowRequest.updated_at.desc()
    ).paginate(page=page, per_page=USERS_PER_PAGE, error_out=False)

    return {
        "status": "success",
        "data": {
            relation: [
                user.serialize(current_user=auth_user)
                for user in paginated_relations.items
            ]
        },
        "pagination": {
            "has_next": paginated_relations.has_next,
            "has_prev": paginated_relations.has_prev,
            "page": paginated_relations.page,
            "pages": paginated_relations.pages,
            "total": paginated_relations.total,
        },
    }


@users_blueprint.route("/users/<user_name>/followers", methods=["GET"])
@require_auth(scopes=["follow:read"])
def get_followers(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get user followers.
    If the authenticated user has admin rights, it returns following users with
    additional field 'email'

    **Scope**: ``follow:read``

    **Example request**:

    - without parameters

    .. sourcecode:: http

      GET /api/users/sam/followers HTTP/1.1
      Content-Type: application/json

    - with page parameter

    .. sourcecode:: http

      GET /api/users/sam/followers?page=1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "followers": [
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Thu, 02 Dec 2021 17:50:48 GMT",
              "first_name": null,
              "followers": 1,
              "following": 1,
              "follows": "true",
              "is_followed_by": "false",
              "last_name": null,
              "location": null,
              "map_visibility": "followers_only",
              "nb_sports": 0,
              "nb_workouts": 0,
              "picture": false,
              "records": [],
              "sports_list": [],
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "username": "JohnDoe",
              "workouts_visibility": "followers_only"
            }
          ]
        },
        "pagination": {
          "has_next": false,
          "has_prev": false,
          "page": 1,
          "pages": 1,
          "total": 1
        },
        "status": "success"
      }

    :param string user_name: user name

    :query integer page: page if using pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``

    """
    return get_user_relationships(auth_user, user_name, "followers")


@users_blueprint.route("/users/<user_name>/following", methods=["GET"])
@require_auth(scopes=["follow:read"])
def get_following(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get user following.
    If the authenticate user has admin rights, it returns following users with
    additional field 'email'

    **Scope**: ``follow:read``

    **Example request**:

    - without parameters

    .. sourcecode:: http

      GET /api/users/sam/following HTTP/1.1
      Content-Type: application/json

    - with page parameter

    .. sourcecode:: http

      GET /api/users/sam/following?page=1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "following": [
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Thu, 02 Dec 2021 17:50:48 GMT",
              "first_name": null,
              "followers": 1,
              "following": 1,
              "follows": "false",
              "is_followed_by": "true",
              "last_name": null,
              "location": null,
              "map_visibility": "followers_only",
              "nb_sports": 0,
              "nb_workouts": 0,
              "picture": false,
              "records": [],
              "sports_list": [],
              "total_distance": 0.0,
              "total_duration": "0:00:00",
              "username": "JohnDoe",
              "workouts_visibility": "followers_only"
            }
          ]
        },
        "pagination": {
          "has_next": false,
          "has_prev": false,
          "page": 1,
          "pages": 1,
          "total": 1
        },
        "status": "success"
      }

    :param string user_name: user name

    :query integer page: page if using pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user does not exist``

    """
    return get_user_relationships(auth_user, user_name, "following")


@users_blueprint.route("/users/<user_name>/block", methods=["POST"])
@require_auth(scopes=["users:write"])
def block_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Block a user

    **Scope**: ``users:write``

    **Example request**:

    .. sourcecode:: http

      GET /api/users/sam/block HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success"
      }

    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400:
        - ``invalid payload``
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user not found``
    """
    target_user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not target_user:
        appLog.error(f"Error: user {user_name} not found")
        return UserNotFoundErrorResponse()

    try:
        auth_user.blocks_user(target_user)
        # delete follow request is exists (approved or pending)
        FollowRequest.query.filter_by(
            follower_user_id=target_user.id, followed_user_id=auth_user.id
        ).delete()
        db.session.commit()

    except BlockUserException:
        return InvalidPayloadErrorResponse()

    return {"status": "success"}


@users_blueprint.route("/users/<user_name>/unblock", methods=["POST"])
@require_auth(scopes=["users:write"])
def unblock_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Unblock a user

    **Scope**: ``users:write``

    **Example request**:

    .. sourcecode:: http

      GET /api/users/sam/unblock HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "success"
      }

    :param string user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
        - ``you do not have permissions, your account is suspended``
    :statuscode 404:
        - ``user not found``

    """
    target_user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not target_user:
        appLog.error(f"Error: user {user_name} not found")
        return UserNotFoundErrorResponse()

    auth_user.unblocks_user(target_user)

    return {"status": "success"}


@users_blueprint.route("/users/<user_name>/sanctions", methods=["GET"])
@require_auth(scopes=["users:read"], allow_suspended_user=True)
def get_user_sanctions(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get user sanctions.

    It returns sanctions only if:
    - user name is authenticated user username
    - user has moderation rights.

    Suspended user can access this endpoint.

    **Scope**: ``users:read``

    **Example requests**:

    - without parameters:

    .. sourcecode:: http

      GET /api/users/Sam/sanctions HTTP/1.1

    - with parameters:

    .. sourcecode:: http

      GET /api/users/Sam/sanctions?page=2 HTTP/1.1

    **Example responses**:

    - if sanctions exist (response with moderation rights)

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "sanctions": [
              {
                "action_type": "workout_suspension",
                "appeal": {
                  "approved": null,
                  "created_at": "Wed, 04 Dec 2024 11:00:04 GMT",
                  "id": "2ULe2hWhSnYCS2VHbsikB9",
                  "moderator": null,
                  "reason": null,
                  "text": "<APPEAL TEXT>",
                  "updated_at": null,
                  "user": {
                    "blocked": false,
                    "created_at": "Wed, 04 Dec 2024 09:07:06 GMT",
                    "email": "sam@example.com",
                    "followers": 0,
                    "following": 0,
                    "follows": false,
                    "is_active": true,
                    "is_followed_by": false,
                    "nb_workouts": 1,
                    "picture": false,
                    "role": "user",
                    "suspended_at": null,
                    "username": "Sam"
                  }
                },
                "created_at": "Wed, 04 Dec 2024 10:59:45 GMT",
                "id": "6dxczvMrhkAR72shUz9Pwd",
                "moderator": {
                  "blocked": false,
                  "created_at": "Wed, 01 Mar 2023 12:31:17 GMT",
                  "email": "admin@example.com",
                  "followers": 0,
                  "following": 0,
                  "follows": "false",
                  "is_active": true,
                  "is_followed_by": "false",
                  "nb_workouts": 0,
                  "picture": true,
                  "role": "admin",
                  "suspended_at": null,
                  "username": "admin"
                },
                "reason": "<SUSPENSION REASON>",
                "report_id": 2,
                "user": {
                  "blocked": false,
                  "created_at": "Sun, 01 Dec 2024 17:27:49 GMT",
                  "email": "sam@example.com",
                  "followers": 0,
                  "following": 0,
                  "follows": "false",
                  "is_active": true,
                  "is_followed_by": "false",
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                }
              }
            ]
          },
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 1,
            "total": 1
          },
          "status": "success"
        }

    - if sanctions exist (response for authenticated user)

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "sanctions": [
              {
                "action_type": "workout_suspension",
                "appeal": {
                  "approved": null,
                  "created_at": "Wed, 04 Dec 2024 16:50:55 GMT",
                  "id": "kcj6hdGQqPKaaKQmfQj8Jv",
                  "reason": null,
                  "text": "<APPEAL TEXT>",
                  "updated_at": null
                },
                "created_at": "Wed, 04 Dec 2024 16:50:44 GMT",
                "id": "6nvxvAyoh9Zkr8RMXhu54T",
                "reason": "<SUSPENSION REASON>"
              }
            ]
          },
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 1,
            "total": 1
          },
          "status": "success"
        }

    - no sanctions

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "sanctions": []
          },
          "pagination": {
            "has_next": false,
            "has_prev": false,
            "page": 1,
            "pages": 0,
            "total": 0
          },
          "status": "success"
        }

    :param string user_name: user name

    :query integer page: page if using pagination (default: 1)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    :statuscode 404:
        - ``user not found``

    """
    user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not user:
        appLog.error(f"Error: user {user_name} not found")
        return UserNotFoundErrorResponse()

    if user.id != auth_user.id and not auth_user.has_moderator_rights:
        return ForbiddenErrorResponse()

    params = request.args.copy()
    page = int(params.get("page", 1))

    paginated_sanctions = (
        ReportAction.query.filter(
            ReportAction.user_id == user.id,
            ReportAction.action_type.not_in(
                [
                    "comment_unsuspension",
                    "user_unsuspension",
                    "user_warning_lifting",
                    "workout_unsuspension",
                ]
            ),
        )
        .order_by(ReportAction.created_at.desc())
        .paginate(page=page, per_page=ACTIONS_PER_PAGE, error_out=False)
    )

    return {
        "status": "success",
        "data": {
            "sanctions": [
                sanctions.serialize(current_user=auth_user, full=False)
                for sanctions in paginated_sanctions.items
            ]
        },
        "pagination": {
            "has_next": paginated_sanctions.has_next,
            "has_prev": paginated_sanctions.has_prev,
            "page": paginated_sanctions.page,
            "pages": paginated_sanctions.pages,
            "total": paginated_sanctions.total,
        },
    }


@users_blueprint.route("/users/<user_name>/workouts", methods=["GET"])
@require_auth(scopes=["workouts:read"], optional_auth_user=True)
def get_user_latest_workouts(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get user last 5 visible workouts.

    **Scope**: ``workouts:read``

    **Example request**:

      GET /api/users/Sam/workouts HTTP/1.1

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "data": {
            "workouts": [
              {
                "ascent": null,
                "ave_speed": 10.0,
                "bounds": [],
                "creation_date": "Sun, 14 Jul 2019 13:51:01 GMT",
                "descent": null,
                "description": null,
                "distance": 10.0,
                "duration": "0:17:04",
                "equipments": [],
                "id": "kjxavSTUrJvoAh2wvCeGEF",
                "liked": false,
                "likes_count": 0,
                "map": null,
                "map_visibility": "private",
                "max_alt": null,
                "max_speed": 10.0,
                "min_alt": null,
                "modification_date": null,
                "moving": "0:17:04",
                "next_workout": 3,
                "notes": null,
                "pauses": null,
                "previous_workout": null,
                "records": [
                  {
                    "id": 4,
                    "record_type": "MS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
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
                    "id": 3,
                    "record_type": "LD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": "0:17:04",
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 2,
                    "record_type": "FD",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  },
                  {
                    "id": 1,
                    "record_type": "AS",
                    "sport_id": 1,
                    "user": "admin",
                    "value": 10.0,
                    "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                    "workout_id": "kjxavSTUrJvoAh2wvCeGEF"
                  }
                ],
                "segments": [],
                "sport_id": 1,
                "suspended": false,
                "suspended_at": null,
                "title": null,
                "user": {
                  "created_at": "Sun, 31 Dec 2017 09:00:00 GMT",
                  "followers": 0,
                  "following": 0,
                  "nb_workouts": 1,
                  "picture": false,
                  "role": "user",
                  "suspended_at": null,
                  "username": "Sam"
                },
                "weather_end": null,
                "weather_start": null,
                "with_gpx": false,
                "workout_date": "Mon, 01 Jan 2018 00:00:00 GMT",
                "workout_visibility": "private"
              }
            ]
          },
          "status": "success"
        }

    :param string user_name: user name


    :reqheader Authorization: OAuth 2.0 Bearer Token if user is authenticated

    :statuscode 200: success
    :statuscode 401:
        - ``provide a valid auth token``
        - ``signature expired, please log in again``
        - ``invalid token, please log in again``
    :statuscode 403:
        - ``you do not have permissions``
    :statuscode 404:
        - ``user not found``
    """
    user = User.query.filter(
        func.lower(User.username) == func.lower(user_name),
    ).first()
    if not user:
        appLog.error(f"Error: user {user_name} not found")
        return UserNotFoundErrorResponse()
    if user.suspended_at:
        return {"status": "success", "data": {"workouts": []}}

    workouts_query = Workout.query.filter(
        Workout.suspended_at == None,  # noqa
        Workout.user_id == user.id,
    )
    if not auth_user or (
        auth_user.id != user.id
        and auth_user.id not in user.get_followers_user_ids()
    ):
        workouts_query = workouts_query.filter(
            Workout.workout_visibility == VisibilityLevel.PUBLIC
        )
    elif auth_user.id in user.get_followers_user_ids():
        workouts_query = workouts_query.filter(
            Workout.workout_visibility.in_(
                [VisibilityLevel.PUBLIC, VisibilityLevel.FOLLOWERS]
            )
        )
    workouts = (
        workouts_query.order_by(Workout.workout_date.desc())
        .limit(WORKOUTS_PER_PAGE)
        .all()
    )
    return {
        "status": "success",
        "data": {
            "workouts": [
                workout.serialize(user=auth_user) for workout in workouts
            ]
        },
    }

import os
import shutil
from typing import Any, Dict, Tuple, Union

from flask import Blueprint, current_app, request, send_file
from sqlalchemy import exc

from fittrackee import db
from fittrackee.emails.tasks import (
    email_updated_to_new_address,
    password_change_email,
    reset_password_email,
)
from fittrackee.files import get_absolute_file_path
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.utils import get_readable_duration
from fittrackee.workouts.models import Record, Workout, WorkoutSegment

from .auth import get_language
from .decorators import authenticate, authenticate_as_admin
from .exceptions import InvalidEmailException, UserNotFoundException
from .models import User, UserSportPreference
from .utils.admin import UserManagerService

users_blueprint = Blueprint('users', __name__)

USER_PER_PAGE = 10


@users_blueprint.route('/users', methods=['GET'])
@authenticate_as_admin
def get_users(auth_user: User) -> Dict:
    """
    Get all users (regardless their account status), if authenticated user
    has admin rights

    It returns user preferences only for authenticated user.

    **Example request**:

    - without parameters

    .. sourcecode:: http

      GET /api/users HTTP/1.1
      Content-Type: application/json

    - with some query parameters

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
              "is_admin": true,
              "imperial_units": false,
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
              "timezone": "Europe/Paris",
              "total_distance": 67.895,
              "total_duration": "6:50:27",
              "username": "admin",
              "weekm": false
            },
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Sat, 20 Jul 2019 11:27:03 GMT",
              "email": "sam@example.com",
              "first_name": null,
              "is_admin": false,
              "language": "fr",
              "last_name": null,
              "location": null,
              "nb_sports": 0,
              "nb_workouts": 0,
              "picture": false,
              "records": [],
              "sports_list": [],
              "timezone": "Europe/Paris",
              "total_distance": 0,
              "total_duration": "0:00:00",
              "username": "sam"
            }
          ]
        },
        "status": "success"
      }

    :query integer page: page if using pagination (default: 1)
    :query integer per_page: number of users per page (default: 10, max: 50)
    :query string q: query on user name
    :query string order_by: sorting criteria (``username``, ``created_at``,
                            ``workouts_count``, ``admin``, ``is_active``)
    :query string order: sorting order (default: ``asc``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again

    """
    params = request.args.copy()
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', USER_PER_PAGE))
    if per_page > 50:
        per_page = 50
    order_by = params.get('order_by')
    order = params.get('order', 'asc')
    query = params.get('q')
    users_pagination = (
        User.query.filter(
            User.username.ilike('%' + query + '%') if query else True,
        )
        .order_by(
            User.workouts_count.asc()  # type: ignore
            if order_by == 'workouts_count' and order == 'asc'
            else True,
            User.workouts_count.desc()  # type: ignore
            if order_by == 'workouts_count' and order == 'desc'
            else True,
            User.username.asc()
            if order_by == 'username' and order == 'asc'
            else True,
            User.username.desc()
            if order_by == 'username' and order == 'desc'
            else True,
            User.created_at.asc()
            if order_by == 'created_at' and order == 'asc'
            else True,
            User.created_at.desc()
            if order_by == 'created_at' and order == 'desc'
            else True,
            User.admin.asc()
            if order_by == 'admin' and order == 'asc'
            else True,
            User.admin.desc()
            if order_by == 'admin' and order == 'desc'
            else True,
            User.is_active.asc()
            if order_by == 'is_active' and order == 'asc'
            else True,
            User.is_active.desc()
            if order_by == 'is_active' and order == 'desc'
            else True,
        )
        .paginate(page, per_page, False)
    )
    users = users_pagination.items
    return {
        'status': 'success',
        'data': {'users': [user.serialize(auth_user) for user in users]},
        'pagination': {
            'has_next': users_pagination.has_next,
            'has_prev': users_pagination.has_prev,
            'page': users_pagination.page,
            'pages': users_pagination.pages,
            'total': users_pagination.total,
        },
    }


@users_blueprint.route('/users/<user_name>', methods=['GET'])
@authenticate
def get_single_user(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get single user details. Only user with admin rights can get other users
    details.

    It returns user preferences only for authenticated user.

    **Example request**:

    .. sourcecode:: http

      GET /api/users/admin HTTP/1.1
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
            "imperial_units": false,
            "is_admin": true,
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
            "timezone": "Europe/Paris",
            "total_distance": 67.895,
            "total_duration": "6:50:27",
            "username": "admin"
          }
        ],
        "status": "success"
      }

    :param integer user_name: user name

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404:
        - user does not exist
    """
    if user_name != auth_user.username and not auth_user.admin:
        return ForbiddenErrorResponse()

    try:
        user = User.query.filter_by(username=user_name).first()
        if user:
            return {
                'status': 'success',
                'data': {'users': [user.serialize(auth_user)]},
            }
    except ValueError:
        pass
    return UserNotFoundErrorResponse()


@users_blueprint.route('/users/<user_name>/picture', methods=['GET'])
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

    :statuscode 200: success
    :statuscode 404:
        - user does not exist
        - No picture.

    """
    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return UserNotFoundErrorResponse()
        if user.picture is not None:
            picture_path = get_absolute_file_path(user.picture)
            return send_file(picture_path)
    except Exception:  # nosec
        pass
    return NotFoundErrorResponse('No picture.')


@users_blueprint.route('/users/<user_name>', methods=['PATCH'])
@authenticate_as_admin
def update_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Update user account

    - add/remove admin rights (regardless user account status)
    - reset password (and send email to update user password,
      if sending enabled)
    - update user email (and send email to new user email, if sending enabled)
    - activate account for an inactive user

    Only user with admin rights can modify another user

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
            "imperial_units": false,
            "is_active": true,
            "language": "en",
            "last_name": null,
            "location": null,
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
            "timezone": "Europe/Paris",
            "total_distance": 67.895,
            "total_duration": "6:50:27",
            "username": "admin"
          }
        ],
        "status": "success"
      }

    :param string user_name: user name

    :<json boolean activate: activate user account
    :<json boolean admin: does the user have administrator rights
    :<json boolean new_email: new user email
    :<json boolean reset_password: reset user password

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 400:
        - invalid payload
        - valid email must be provided
        - new email must be different than curent email
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403: you do not have permissions
    :statuscode 404:
        - user does not exist
    :statuscode 500:
    """
    user_data = request.get_json()
    if not user_data:
        return InvalidPayloadErrorResponse()

    try:
        reset_password = user_data.get('reset_password', False)
        new_email = user_data.get('new_email')
        user_manager_service = UserManagerService(username=user_name)
        user, _, _ = user_manager_service.update(
            is_admin=user_data.get('admin'),
            activate=user_data.get('activate', False),
            reset_password=reset_password,
            new_email=new_email,
            with_confirmation=current_app.config['CAN_SEND_EMAILS'],
        )

        if current_app.config['CAN_SEND_EMAILS']:
            user_language = get_language(user.language)
            ui_url = current_app.config['UI_URL']
            if reset_password:
                user_data = {
                    'language': user_language,
                    'email': user.email,
                }
                password_change_email.send(
                    user_data,
                    {
                        'username': user.username,
                        'fittrackee_url': ui_url,
                    },
                )
                password_reset_token = user.encode_password_reset_token(
                    user.id
                )
                reset_password_email.send(
                    user_data,
                    {
                        'expiration_delay': get_readable_duration(
                            current_app.config[
                                'PASSWORD_TOKEN_EXPIRATION_SECONDS'
                            ],
                            user_language,
                        ),
                        'username': user.username,
                        'password_reset_url': (
                            f'{ui_url}/password-reset?'
                            f'token={password_reset_token}'
                        ),
                        'fittrackee_url': ui_url,
                    },
                )

            if new_email:
                user_data = {
                    'language': user_language,
                    'email': user.email_to_confirm,
                }
                email_data = {
                    'username': user.username,
                    'fittrackee_url': ui_url,
                    'email_confirmation_url': (
                        f'{ui_url}/email-update'
                        f'?token={user.confirmation_token}'
                    ),
                }
                email_updated_to_new_address.send(user_data, email_data)

        return {
            'status': 'success',
            'data': {'users': [user.serialize(auth_user)]},
        }
    except UserNotFoundException:
        return UserNotFoundErrorResponse()
    except InvalidEmailException as e:
        return InvalidPayloadErrorResponse(str(e))
    except exc.StatementError as e:
        return handle_error_and_return_response(e, db=db)


@users_blueprint.route('/users/<user_name>', methods=['DELETE'])
@authenticate
def delete_user(
    auth_user: User, user_name: str
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    Delete a user account

    A user can only delete his own account

    An admin can delete all accounts except his account if he's the only
    one admin

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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403:
        - you do not have permissions
        - you can not delete your account, no other user has admin rights
    :statuscode 404:
        - user does not exist
    :statuscode 500: error, please try again or contact the administrator

    """
    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return UserNotFoundErrorResponse()

        if user.id != auth_user.id and not auth_user.admin:
            return ForbiddenErrorResponse()
        if (
            user.admin is True
            and User.query.filter_by(admin=True).count() == 1
        ):
            return ForbiddenErrorResponse(
                'you can not delete your account, '
                'no other user has admin rights'
            )

        db.session.query(UserSportPreference).filter(
            UserSportPreference.user_id == user.id
        ).delete()
        db.session.query(Record).filter(Record.user_id == user.id).delete()
        db.session.query(WorkoutSegment).filter(
            WorkoutSegment.workout_id == Workout.id, Workout.user_id == user.id
        ).delete(synchronize_session=False)
        db.session.query(Workout).filter(Workout.user_id == user.id).delete()
        db.session.flush()
        user_picture = user.picture
        db.session.delete(user)
        db.session.commit()
        if user_picture:
            picture_path = get_absolute_file_path(user.picture)
            if os.path.isfile(picture_path):
                os.remove(picture_path)
        shutil.rmtree(
            get_absolute_file_path(f'workouts/{user.id}'),
            ignore_errors=True,
        )
        shutil.rmtree(
            get_absolute_file_path(f'pictures/{user.id}'),
            ignore_errors=True,
        )
        return {'status': 'no content'}, 204
    except (
        exc.IntegrityError,
        exc.OperationalError,
        ValueError,
        OSError,
    ) as e:
        return handle_error_and_return_response(e, db=db)

import os
import shutil
from typing import Any, Dict, Optional, Tuple, Union

import click
from flask import Blueprint, request, send_file
from sqlalchemy import exc

from fittrackee import appLog, db
from fittrackee.federation.decorators import federation_required
from fittrackee.federation.exceptions import (
    ActorNotFoundException,
    DomainNotFoundException,
)
from fittrackee.federation.models import Domain
from fittrackee.federation.utils_user import get_user_from_username
from fittrackee.files import get_absolute_file_path
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    UserNotFoundErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.workouts.models import Record, Workout, WorkoutSegment

from .decorators import (
    authenticate,
    authenticate_as_admin,
    get_auth_user_if_authenticated,
)
from .exceptions import (
    FollowRequestAlreadyRejectedError,
    UserNotFoundException,
)
from .models import FollowRequest, User, UserSportPreference
from .utils.admin import set_admin_rights

users_blueprint = Blueprint('users', __name__)

USERS_PER_PAGE = 10


@users_blueprint.cli.command('set-admin')
@click.argument('username')
def set_admin(username: str) -> None:
    """Set admin rights for given user"""
    try:
        set_admin_rights(username)
        print(f"User '{username}' updated.")
    except UserNotFoundException:
        print(f"User '{username}' not found.")


def get_users_list(auth_user: User, remote: bool = False) -> Dict:
    params = request.args.copy()
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', USERS_PER_PAGE))
    if per_page > 50:
        per_page = 50
    order_by = params.get('order_by', 'username')
    order = params.get('order', 'asc')
    query = params.get('q')
    users_pagination = (
        User.query.filter(
            User.username.like('%' + query + '%') if query else True,
            User.is_remote == remote,
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


@users_blueprint.route('/users', methods=['GET'])
@authenticate
def get_users(auth_user: User) -> Dict:
    """
    Get all users (it returns only local users if federation is enabled).
    If authenticated user has admin rights, users email is returned.

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
              "followers": 0,
              "following": 0,
              "is_remote": false,
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
              "is_remote": false,
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
    :query string order_by: sorting criteria (``username``, ``created_at``,
                            ``workouts_count``, ``admin``,
                            default: ``username``)
    :query string order: sorting order (``asc``, ``desc``, default: ``asc``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again

    """
    return get_users_list(auth_user)


@users_blueprint.route('/users/remote', methods=['GET'])
@federation_required
@authenticate
def get_remote_users(
    auth_user: User,
    app_domain: Domain,
) -> Dict:
    """
    Get all remote users (only if federation is enabled)

    **Example request**:

    - without parameters

    .. sourcecode:: http

      GET /api/users/remote HTTP/1.1
      Content-Type: application/json

    - with some query parameters

    .. sourcecode:: http

      GET /api/users/remote?order_by=username  HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "users": [
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Sat, 20 Jul 2019 11:27:03 GMT",
              "first_name": null,
              "followers": 0,
              "following": 0,
              "is_remote": true,
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
    :query string order_by: sorting criteria (``username``, ``created_at``,
                            ``workouts_count``, ``admin``,
                            default: ``username``)
    :query string order: sorting order (``asc``, ``desc``, default: ``asc``)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403: Error. Federation is disabled for this instance.

    """
    return get_users_list(auth_user, remote=True)


@users_blueprint.route('/users/<user_name>', methods=['GET'])
@get_auth_user_if_authenticated
def get_single_user(
    auth_user: Optional[User], user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get single user details.
    If authenticated user has admin rights, user email is returned.

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
            "is_remote": false,
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
            "is_remote": false,
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

    :statuscode 200: success
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404:
        - user does not exist
    """
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
    except Exception:
        pass
    return NotFoundErrorResponse('No picture.')


@users_blueprint.route('/users/<user_name>', methods=['PATCH'])
@authenticate_as_admin
def update_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Update user to add admin rights

    Only user with admin rights can modify another user

    **Example request**:

    .. sourcecode:: http

      PATCH api/users/<user_name> HTTP/1.1
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
            "is_remote": false,
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

    :<json boolean admin: does the user have administrator rights

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
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
    if not user_data or user_data.get('admin') is None:
        return InvalidPayloadErrorResponse()

    try:
        user = User.query.filter_by(username=user_name).first()
        if not user:
            return UserNotFoundErrorResponse()

        user.admin = user_data['admin']
        db.session.commit()
        return {
            'status': 'success',
            'data': {'users': [user.serialize(auth_user)]},
        }
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
        db.session.delete(user.actor)
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


@users_blueprint.route('/users/<user_name>/follow', methods=['POST'])
@authenticate
def follow_user(auth_user: User, user_name: str) -> Union[Dict, HttpResponse]:
    """
    Send a follow request to a user.
    If federation is enabled, it sends a follow request to remote instance
    if the targeted user is a remote user.

    **Example request**:

    - follow local user

    .. sourcecode:: http

      POST /api/users/john_doe/follow HTTP/1.1
      Content-Type: application/json

    - follow remote user

    .. sourcecode:: http

      POST /api/users/sam@remote-instance.net/follow HTTP/1.1
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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403:
        - you do not have permissions
    :statuscode 404:
        - user does not exist
    :statuscode 500: error, please try again or contact the administrator

    """
    successful_response_dict = {
        'status': 'success',
        'message': f"Follow request to user '{user_name}' is sent.",
    }

    try:
        target_user = get_user_from_username(user_name)
    except (
        ActorNotFoundException,
        DomainNotFoundException,
        UserNotFoundException,
    ) as e:
        appLog.error(f'Error when following a user: {e}')
        return UserNotFoundErrorResponse()

    try:
        auth_user.send_follow_request_to(target_user)
    except FollowRequestAlreadyRejectedError:
        return ForbiddenErrorResponse()
    return successful_response_dict


def get_user_relationships(
    auth_user: User, user_name: str, relation: str
) -> Union[Dict, HttpResponse]:
    params = request.args.copy()
    try:
        page = int(params.get('page', 1))
    except ValueError:
        page = 1

    user = User.query.filter_by(username=user_name).first()
    if not user:
        return UserNotFoundErrorResponse()

    relations_object = (
        user.followers if relation == 'followers' else user.following
    )

    paginated_relations = relations_object.order_by(
        FollowRequest.updated_at.desc()
    ).paginate(page, USERS_PER_PAGE, False)

    return {
        'status': 'success',
        'data': {
            relation: [
                user.serialize(auth_user) for user in paginated_relations.items
            ]
        },
        'pagination': {
            'has_next': paginated_relations.has_next,
            'has_prev': paginated_relations.has_prev,
            'page': paginated_relations.page,
            'pages': paginated_relations.pages,
            'total': paginated_relations.total,
        },
    }


@users_blueprint.route('/users/<user_name>/followers', methods=['GET'])
@authenticate
def get_followers(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get user followers.
    If the authenticated user has admin rights, it returns following users with
    additional field 'email'

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
              "is_remote": false,
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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403:
        - you do not have permissions
    :statuscode 404:
        - user does not exist

    """
    return get_user_relationships(auth_user, user_name, 'followers')


@users_blueprint.route('/users/<user_name>/following', methods=['GET'])
@authenticate
def get_following(
    auth_user: User, user_name: str
) -> Union[Dict, HttpResponse]:
    """
    Get user following.
    If the authenticate user has admin rights, it returns following users with
    additional field 'email'

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
              "is_remote": false,
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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 403:
        - you do not have permissions
    :statuscode 404:
        - user does not exist

    """
    return get_user_relationships(auth_user, user_name, 'following')

from flask import Blueprint, jsonify, send_file

from ..activities.utils_files import get_absolute_file_path
from .models import User
from .utils import authenticate

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=['GET'])
@authenticate
def get_users(auth_user_id):
    """
    Get all users

    **Example request**:

    .. sourcecode:: http

      GET /api/users HTTP/1.1
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
              "id": 1,
              "last_name": null,
              "location": null,
              "nb_activities": 6,
              "nb_sports": 3,
              "picture": false,
              "timezone": "Europe/Paris",
              "total_distance": 67.895,
              "total_duration": "6:50:27",
              "username": "admin"
            },
            {
              "admin": false,
              "bio": null,
              "birth_date": null,
              "created_at": "Sat, 20 Jul 2019 11:27:03 GMT",
              "email": "sam@example.com",
              "first_name": null,
              "id": 2,
              "last_name": null,
              "location": null,
              "nb_activities": 0,
              "nb_sports": 0,
              "picture": false,
              "timezone": "Europe/Paris",
              "total_distance": 0,
              "total_duration": "0:00:00",
              "username": "sam"
            }
          ]
        },
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.

    """
    users = User.query.all()
    response_object = {
        'status': 'success',
        'data': {'users': [user.serialize() for user in users]},
    }
    return jsonify(response_object), 200


@users_blueprint.route('/users/<user_id>', methods=['GET'])
@authenticate
def get_single_user(auth_user_id, user_id):
    """
    Get single user details

    **Example request**:

    .. sourcecode:: http

      GET /api/users/1 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "data": {
          "admin": true,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "email": "admin@example.com",
          "first_name": null,
          "id": 1,
          "last_name": null,
          "location": null,
          "nb_activities": 6,
          "nb_sports": 3,
          "picture": false,
          "timezone": "Europe/Paris",
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "username": "admin"
        },
        "status": "success"
      }

    :param integer auth_user_id: authenticate user id (from JSON Web Token)
    :param integer user_id: user id

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success
    :statuscode 401:
        - Provide a valid auth token.
        - Signature expired. Please log in again.
        - Invalid token. Please log in again.
    :statuscode 404:
        - User does not exist.
    """

    response_object = {'status': 'fail', 'message': 'User does not exist.'}
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {'status': 'success', 'data': user.serialize()}
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@users_blueprint.route('/users/<user_id>/picture', methods=['GET'])
def get_picture(user_id):
    """ get user picture

    **Example request**:

    .. sourcecode:: http

      GET /api/users/1/picture HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: image/jpeg

    :param integer user_id: user id

    :statuscode 200: success
    :statuscode 404:
        - User does not exist.
        - No picture.

    """
    response_object = {'status': 'not found', 'message': 'No picture.'}
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            response_object = {
                'status': 'fail',
                'message': 'User does not exist.',
            }
            return jsonify(response_object), 404
        if user.picture is not None:
            picture_path = get_absolute_file_path(user.picture)
            return send_file(picture_path)
        return jsonify(response_object), 404
    except Exception:
        return jsonify(response_object), 404


@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    """ health check endpoint

    **Example request**:

    .. sourcecode:: http

      GET /api/ping HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "pong!",
        "status": "success"
      }

    :statuscode 200: success

    """
    return jsonify({'status': 'success', 'message': 'pong!'})

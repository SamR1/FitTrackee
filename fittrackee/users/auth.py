import datetime
import os
import re
from typing import Dict, Tuple, Union

import jwt
from flask import Blueprint, current_app, request
from sqlalchemy import exc, func, or_
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from fittrackee import appLog, bcrypt, db
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    NotFoundErrorResponse,
    PayloadTooLargeErrorResponse,
    UnauthorizedErrorResponse,
    handle_error_and_return_response,
)
from fittrackee.tasks import reset_password_email
from fittrackee.utils import get_readable_duration, verify_extension_and_size
from fittrackee.workouts.models import Sport
from fittrackee.workouts.utils_files import get_absolute_file_path

from .decorators import authenticate
from .models import User, UserSportPreference
from .utils import check_passwords, register_controls
from .utils_token import decode_user_token

auth_blueprint = Blueprint('auth', __name__)

HEX_COLOR_REGEX = regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"


@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user() -> Union[Tuple[Dict, int], HttpResponse]:
    """
    register a user

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/register HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - successful registration

    .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Content-Type: application/json

      {
        "auth_token": "JSON Web Token",
        "message": "successfully registered",
        "status": "success"
      }

    - error on registration

    .. sourcecode:: http

      HTTP/1.1 400 BAD REQUEST
      Content-Type: application/json

      {
        "message": "Errors: email: valid email must be provided\\n",
        "status": "error"
      }

    :<json string username: user name (3 to 12 characters required)
    :<json string email: user email
    :<json string password: password (8 characters required)
    :<json string password_conf: password confirmation

    :statuscode 201: successfully registered
    :statuscode 400:
        - invalid payload
        - sorry, that user already exists
        - Errors:
            - username: 3 to 12 characters required
            - email: valid email must be provided
            - password: password and password confirmation don't match
            - password: 8 characters required
    :statuscode 403:
        error, registration is disabled
    :statuscode 500:
        error, please try again or contact the administrator

    """
    if not current_app.config.get('is_registration_enabled'):
        return ForbiddenErrorResponse('error, registration is disabled')

    # get post data
    post_data = request.get_json()
    if (
        not post_data
        or post_data.get('username') is None
        or post_data.get('email') is None
        or post_data.get('password') is None
        or post_data.get('password_conf') is None
    ):
        return InvalidPayloadErrorResponse()
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    password_conf = post_data.get('password_conf')

    try:
        ret = register_controls(username, email, password, password_conf)
    except TypeError as e:
        return handle_error_and_return_response(e, db=db)

    if ret != '':
        return InvalidPayloadErrorResponse(ret)

    try:
        # check for existing user
        user = User.query.filter(
            or_(
                func.lower(User.username) == func.lower(username),
                func.lower(User.email) == func.lower(email),
            )
        ).first()
        if user:
            return InvalidPayloadErrorResponse(
                'sorry, that user already exists'
            )

        # add new user to db
        new_user = User(username=username, email=email, password=password)
        new_user.timezone = 'Europe/Paris'
        db.session.add(new_user)
        db.session.commit()
        # generate auth token
        auth_token = new_user.encode_auth_token(new_user.id)
        return {
            'status': 'success',
            'message': 'successfully registered',
            'auth_token': auth_token,
        }, 201
    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user() -> Union[Dict, HttpResponse]:
    """
    user login

    **Example request**:

    .. sourcecode:: http

      POST /api/auth/login HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - successful login

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

      HTTP/1.1 404 NOT FOUND
      Content-Type: application/json

      {
        "message": "invalid credentials",
        "status": "error"
      }

    :<json string email: user email
    :<json string password_conf: password confirmation

    :statuscode 200: successfully logged in
    :statuscode 400: invalid payload
    :statuscode 401: invalid credentials
    :statuscode 500: error, please try again or contact the administrator

    """
    # get post data
    post_data = request.get_json()
    if not post_data:
        return InvalidPayloadErrorResponse()
    email = post_data.get('email', '')
    password = post_data.get('password')
    try:
        # check for existing user
        user = User.query.filter(
            func.lower(User.email) == func.lower(email)
        ).first()
        if user and bcrypt.check_password_hash(user.password, password):
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


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout_user(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    user logout

    **Example request**:

    .. sourcecode:: http

      GET /api/auth/logout HTTP/1.1
      Content-Type: application/json

    **Example responses**:

    - successful logout

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "message": "successfully logged out",
        "status": "success"
      }

    - error on login

    .. sourcecode:: http

      HTTP/1.1 401 UNAUTHORIZED
      Content-Type: application/json

      {
        "message": "provide a valid auth token",
        "status": "error"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: successfully logged out
    :statuscode 401: provide a valid auth token

    """
    # get auth token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return UnauthorizedErrorResponse('provide a valid auth token')

    auth_token = auth_header.split(' ')[1]
    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
        return UnauthorizedErrorResponse(resp)

    return {
        'status': 'success',
        'message': 'successfully logged out',
    }


@auth_blueprint.route('/auth/profile', methods=['GET'])
@authenticate
def get_authenticated_user_profile(
    auth_user: User,
) -> Union[Dict, HttpResponse]:
    """
    get authenticated user info

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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "email": "sam@example.com",
          "first_name": null,
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
          "timezone": "Europe/Paris",
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "username": "sam",
          "weekm": false
        },
        "status": "success"
      }

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: success.
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again

    """
    return {'status': 'success', 'data': auth_user.serialize()}


@auth_blueprint.route('/auth/profile/edit', methods=['POST'])
@authenticate
def edit_user(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    edit authenticated user

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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "email": "sam@example.com",
          "first_name": null,
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
          "timezone": "Europe/Paris",
          "total_distance": 67.895,
          "total_duration": "6:50:27",
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
    :<json string password: user password
    :<json string password_conf: user password confirmation

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: user profile updated
    :statuscode 400:
        - invalid payload
        - password: password and password confirmation don't match
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 500: error, please try again or contact the administrator

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
    password = post_data.get('password')
    password_conf = post_data.get('password_conf')

    if password is not None and password != '':
        message = check_passwords(password, password_conf)
        if message != '':
            return InvalidPayloadErrorResponse(message)
        password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

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
        if password is not None and password != '':
            auth_user.password = password
        db.session.commit()

        return {
            'status': 'success',
            'message': 'user profile updated',
            'data': auth_user.serialize(),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/profile/edit/preferences', methods=['POST'])
@authenticate
def edit_user_preferences(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    edit authenticated user preferences

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
          "admin": false,
          "bio": null,
          "birth_date": null,
          "created_at": "Sun, 14 Jul 2019 14:09:58 GMT",
          "email": "sam@example.com",
          "first_name": null,
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
          "timezone": "Europe/Paris",
          "total_distance": 67.895,
          "total_duration": "6:50:27",
          "username": "sam"
          "weekm": true,
        },
        "message": "user preferences updated",
        "status": "success"
      }

    :<json string timezone: user time zone
    :<json string weekm: does week start on Monday?
    :<json string language: language preferences

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :statuscode 200: user preferences updated
    :statuscode 400:
        - invalid payload
        - password: password and password confirmation don't match
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 500: error, please try again or contact the administrator

    """
    # get post data
    post_data = request.get_json()
    user_mandatory_data = {
        'imperial_units',
        'language',
        'timezone',
        'weekm',
    }
    if not post_data or not post_data.keys() >= user_mandatory_data:
        return InvalidPayloadErrorResponse()

    imperial_units = post_data.get('imperial_units')
    language = post_data.get('language')
    timezone = post_data.get('timezone')
    weekm = post_data.get('weekm')

    try:
        auth_user.imperial_units = imperial_units
        auth_user.language = language
        auth_user.timezone = timezone
        auth_user.weekm = weekm
        db.session.commit()

        return {
            'status': 'success',
            'message': 'user preferences updated',
            'data': auth_user.serialize(),
        }

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)


@auth_blueprint.route('/auth/profile/edit/sports', methods=['POST'])
@authenticate
def edit_user_sport_preferences(
    auth_user: User,
) -> Union[Dict, HttpResponse]:
    """
    edit authenticated user sport preferences

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

    :statuscode 200: user preferences updated
    :statuscode 400:
        - invalid payload
        - invalid hexadecimal color
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404:
        - sport does not exist
    :statuscode 500: error, please try again or contact the administrator

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
@authenticate
def reset_user_sport_preferences(
    auth_user: User, sport_id: int
) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    reset authenticated user preferences for a given sport

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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 404:
        - sport does not exist
    :statuscode 500: error, please try again or contact the administrator

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
@authenticate
def edit_picture(auth_user: User) -> Union[Dict, HttpResponse]:
    """
    update authenticated user picture

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

    :statuscode 200: user picture updated
    :statuscode 400:
        - invalid payload
        - no file part
        - no selected file
        - file extension not allowed
    :statuscode 401:
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 413: error during picture update: file size exceeds 1.0MB
    :statuscode 500: error during picture update

    """
    try:
        response_object = verify_extension_and_size('picture', request)
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
@authenticate
def del_picture(auth_user: User) -> Union[Tuple[Dict, int], HttpResponse]:
    """
    delete authenticated user picture

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
        - provide a valid auth token
        - signature expired, please log in again
        - invalid token, please log in again
    :statuscode 500: error during picture deletion

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
    handle password reset request

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

    :statuscode 200: password reset request processed
    :statuscode 400: invalid payload

    """
    post_data = request.get_json()
    if not post_data or post_data.get('email') is None:
        return InvalidPayloadErrorResponse()
    email = post_data.get('email')

    user = User.query.filter(User.email == email).first()
    if user:
        password_reset_token = user.encode_password_reset_token(user.id)
        ui_url = current_app.config['UI_URL']
        user_language = 'en' if user.language is None else user.language
        email_data = {
            'expiration_delay': get_readable_duration(
                current_app.config['PASSWORD_TOKEN_EXPIRATION_SECONDS'],
                user_language,
            ),
            'username': user.username,
            'password_reset_url': (
                f'{ui_url}/password-reset?token={password_reset_token}'  # noqa
            ),
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
    update user password

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
    :<json string password_conf: password confirmation
    :<json string token: password reset token

    :statuscode 200: password updated
    :statuscode 400: invalid payload
    :statuscode 401: invalid token, please request a new token
    :statuscode 500: error, please try again or contact the administrator

    """
    post_data = request.get_json()
    if (
        not post_data
        or post_data.get('password') is None
        or post_data.get('password_conf') is None
        or post_data.get('token') is None
    ):
        return InvalidPayloadErrorResponse()
    password = post_data.get('password')
    password_conf = post_data.get('password_conf')
    token = post_data.get('token')

    try:
        user_id = decode_user_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return UnauthorizedErrorResponse()

    message = check_passwords(password, password_conf)
    if message != '':
        return InvalidPayloadErrorResponse(message)

    user = User.query.filter(User.id == user_id).first()
    if not user:
        return UnauthorizedErrorResponse()
    try:
        user.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        db.session.commit()
        return {
            'status': 'success',
            'message': 'password updated',
        }
    except (exc.OperationalError, ValueError) as e:
        return handle_error_and_return_response(e, db=db)

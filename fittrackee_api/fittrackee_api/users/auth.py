import datetime
import os

from fittrackee_api import appLog, bcrypt, db
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import exc, or_
from werkzeug.utils import secure_filename

from ..activities.utils_files import get_absolute_file_path
from .models import User
from .utils import authenticate, register_controls, verify_extension

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user():
    """ register a user """
    # get post data
    post_data = request.get_json()
    if not post_data or post_data.get('username') is None \
            or post_data.get('email') is None \
            or post_data.get('password') is None \
            or post_data.get('password_conf') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    password_conf = post_data.get('password_conf')

    try:
        ret = register_controls(username, email, password, password_conf)
    except TypeError as e:
        db.session.rollback()
        appLog.error(e)

        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        return jsonify(response_object), 500
    if ret != '':
        response_object = {
            'status': 'error',
            'message': 'Errors: ' + ret
        }
        return jsonify(response_object), 400

    try:
        # check for existing user
        user = User.query.filter(
            or_(User.username == username, User.email == email)).first()
        if not user:
            # add new user to db
            new_user = User(
                username=username,
                email=email,
                password=password
            )
            new_user.timezone = 'Europe/Paris'
            db.session.add(new_user)
            db.session.commit()
            # generate auth token
            auth_token = new_user.encode_auth_token(new_user.id)
            response_object = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'error',
                'message': 'Sorry. That user already exists.'
            }
            return jsonify(response_object), 400
    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)

        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user():
    """ user login """
    # get post data
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        # check for existing user
        user = User.query.filter(User.email == email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # generate auth token
            auth_token = user.encode_auth_token(user.id)
            response_object = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token.decode()
            }
            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'error',
                'message': 'Invalid credentials.'
            }
            return jsonify(response_object), 404
    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/logout', methods=['GET'])
@authenticate
def logout_user(user_id):
    """ user logout """
    # get auth token
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
        resp = User.decode_auth_token(auth_token)
        if not isinstance(user_id, str):
            response_object = {
                'status': 'success',
                'message': 'Successfully logged out.'
            }
            return jsonify(response_object), 200
        else:
            response_object = {
                'status': 'error',
                'message': resp
            }
            return jsonify(response_object), 401
    else:
        response_object = {
            'status': 'error',
            'message': 'Provide a valid auth token.'
        }
        return jsonify(response_object), 401


@auth_blueprint.route('/auth/profile', methods=['GET'])
@authenticate
def get_user_status(user_id):
    """ get authenticated user info """
    user = User.query.filter_by(id=user_id).first()
    response_object = {
        'status': 'success',
        'data': user.serialize()
    }
    return jsonify(response_object), 200


@auth_blueprint.route('/auth/profile/edit', methods=['POST'])
@authenticate
def edit_user(user_id):
    """ edit authenticated user """
    # get post data
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    bio = post_data.get('bio')
    birth_date = post_data.get('birth_date')
    location = post_data.get('location')
    password = post_data.get('password')
    password_conf = post_data.get('password_conf')
    timezone = post_data.get('timezone')

    if password is not None and password != '':
        if password_conf != password:
            response_object = {
                'status': 'error',
                'message': 'Password and password confirmation don\'t match.\n'
            }
            return jsonify(response_object), 400
        else:
            password = bcrypt.generate_password_hash(
                password, current_app.config.get('BCRYPT_LOG_ROUNDS')
            ).decode()

    try:
        user = User.query.filter_by(id=user_id).first()
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.location = location
        user.birth_date = (
            datetime.datetime.strptime(birth_date, '%Y-%m-%d')
            if birth_date
            else None
        )
        if password is not None and password != '':
            user.password = password
        user.timezone = timezone
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': 'User profile updated.'
        }
        return jsonify(response_object), 200

    # handler errors
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/picture', methods=['POST'])
@authenticate
def edit_picture(user_id):
    """ update authenticated user picture """
    code = 400
    response_object = verify_extension('picture', request)
    if response_object['status'] != 'success':
        return jsonify(response_object), code

    file = request.files['file']
    filename = secure_filename(file.filename)
    dirpath = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'pictures',
        str(user_id)
    )
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    absolute_picture_path = os.path.join(dirpath, filename)
    relative_picture_path = os.path.join(
        'pictures',
        str(user_id),
        filename
    )

    try:
        user = User.query.filter_by(id=user_id).first()
        if user.picture is not None:
            old_picture_path = get_absolute_file_path(user.picture)
            if os.path.isfile(get_absolute_file_path(old_picture_path)):
                os.remove(old_picture_path)
        file.save(absolute_picture_path)
        user.picture = relative_picture_path
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': 'User picture updated.'
        }
        return jsonify(response_object), 200

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'fail',
            'message': 'Error during picture update.'
        }
        return jsonify(response_object), 500


@auth_blueprint.route('/auth/picture', methods=['DELETE'])
@authenticate
def del_picture(user_id):
    """ delete authenticated user picture """
    try:
        user = User.query.filter_by(id=user_id).first()
        picture_path = get_absolute_file_path(user.picture)
        if os.path.isfile(picture_path):
            os.remove(picture_path)
        user.picture = None
        db.session.commit()

        response_object = {
            'status': 'no content'
        }
        return jsonify(response_object), 204

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'fail',
            'message': 'Error during picture deletion.'
        }
        return jsonify(response_object), 500

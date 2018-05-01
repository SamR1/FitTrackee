import datetime
import os

from flask import Blueprint, current_app, jsonify, request
from mpwo_api import appLog, bcrypt, db
from sqlalchemy import exc, or_
from werkzeug.utils import secure_filename

from .models import User
from .utils import authenticate, register_controls, verify_extension

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user():
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

    ret = register_controls(username, email, password, password_conf)
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
        return jsonify(response_object), 400


@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user():
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
        return jsonify(response_object), 403


@auth_blueprint.route('/auth/profile', methods=['GET'])
@authenticate
def get_user_status(user_id):
    user = User.query.filter_by(id=user_id).first()
    response_object = {
        'status': 'success',
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at,
            'admin': user.admin,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'location': user.location,
            'birth_date': user.birth_date,
            'picture': True if user.picture else False,
        }
    }
    return jsonify(response_object), 200


@auth_blueprint.route('/auth/profile/edit', methods=['POST'])
@authenticate
def edit_user(user_id):
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
            datetime.datetime.strptime(birth_date, '%d/%m/%Y')
            if birth_date
            else None
        )
        if password is not None and password != '':
            user.password = password
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
    filepath = os.path.join(dirpath, filename)

    try:
        user = User.query.filter_by(id=user_id).first()
        if user.picture is not None and os.path.isfile(user.picture):
            os.remove(user.picture)
        file.save(filepath)
        user.picture = filepath
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
    try:
        user = User.query.filter_by(id=user_id).first()
        if os.path.isfile(user.picture):
            os.remove(user.picture)
        user.picture = None
        db.session.commit()

        response_object = {
            'status': 'success',
            'message': 'User picture delete.'
        }
        return jsonify(response_object), 200

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'fail',
            'message': 'Error during picture deletion.'
        }
        return jsonify(response_object), 500

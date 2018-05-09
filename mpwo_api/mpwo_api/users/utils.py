import re
from functools import wraps

from flask import current_app, jsonify, request

from .models import User


def is_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.admin


def is_valid_email(email):
    mail_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(mail_pattern, email) is not None


def register_controls(username, email, password, password_conf):
    ret = ''
    if not 2 < len(username) < 13:
        ret += 'Username: 3 to 12 characters required.\n'
    if not is_valid_email(email):
        ret += 'Valid email must be provided.\n'
    if password != password_conf:
        ret += 'Password and password confirmation don\'t match.\n'
    if len(password) < 8:
        ret += 'Password: 8 characters required.\n'
    return ret


def verify_extension(file_type, req):
    response_object = {'status': 'success'}

    if 'file' not in req.files:
        response_object = {'status': 'fail', 'message': 'No file part.'}
        return response_object

    file = req.files['file']
    if file.filename == '':
        response_object = {'status': 'fail', 'message': 'No selected file.'}
        return response_object

    allowed_extensions = (
        'ACTIVITY_ALLOWED_EXTENSIONS'
        if file_type == 'activity'
        else 'PICTURE_ALLOWED_EXTENSIONS'
    )

    if not ('.' in file.filename and
            file.filename.rsplit('.', 1)[1].lower() in
            current_app.config.get(allowed_extensions)):
        response_object = {
            'status': 'fail',
            'message': 'File extension not allowed.'
        }

    return response_object


def verify_user(current_request, verify_admin):
    response_object = {
        'status': 'error',
        'message': 'Something went wrong. Please contact us.'
    }
    code = 401
    auth_header = current_request.headers.get('Authorization')
    if not auth_header:
        response_object['message'] = 'Provide a valid auth token.'
        code = 403
        return response_object, code, None
    auth_token = auth_header.split(" ")[1]
    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
        response_object['message'] = resp
        return response_object, code, None
    user = User.query.filter_by(id=resp).first()
    if not user:
        return response_object, code, None
    if verify_admin and not is_admin(resp):
        response_object['message'] = 'You do not have permissions.'
        return response_object, code, None
    return None, None, resp


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_admin = False
        response_object, code, resp = verify_user(request, verify_admin)
        if response_object:
            return jsonify(response_object), code
        return f(resp, *args, **kwargs)

    return decorated_function


def authenticate_as_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_admin = True
        response_object, code, resp = verify_user(request, verify_admin)
        if response_object:
            return jsonify(response_object), code
        return f(resp, *args, **kwargs)

    return decorated_function

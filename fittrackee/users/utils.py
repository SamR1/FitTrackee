import re
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Union

import humanize
from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    InvalidPayloadErrorResponse,
    PayloadTooLargeErrorResponse,
    UnauthorizedErrorResponse,
)
from flask import Request, current_app, request

from .models import User


def is_admin(user_id: int) -> bool:
    """
    Return if user has admin rights
    """
    user = User.query.filter_by(id=user_id).first()
    return user.admin


def is_valid_email(email: str) -> bool:
    """
    Return if email format is valid
    """
    mail_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(mail_pattern, email) is not None


def check_passwords(password: str, password_conf: str) -> str:
    """
    Verify if password and password confirmation are the same and have
    more than 8 characters

    If not, it returns not empty string
    """
    ret = ''
    if password_conf != password:
        ret = 'Password and password confirmation don\'t match.\n'
    if len(password) < 8:
        ret += 'Password: 8 characters required.\n'
    return ret


def register_controls(
    username: str, email: str, password: str, password_conf: str
) -> str:
    """
    Verify if user name, email and passwords are valid

    If not, it returns not empty string
    """
    ret = ''
    if not 2 < len(username) < 13:
        ret += 'Username: 3 to 12 characters required.\n'
    if not is_valid_email(email):
        ret += 'Valid email must be provided.\n'
    ret += check_passwords(password, password_conf)
    return ret


def verify_extension_and_size(
    file_type: str, req: Request
) -> Optional[HttpResponse]:
    """
    Return error Response if file is invalid
    """
    if 'file' not in req.files:
        return InvalidPayloadErrorResponse('No file part.', 'fail')

    file = req.files['file']
    if file.filename == '':
        return InvalidPayloadErrorResponse('No selected file.', 'fail')

    allowed_extensions = (
        'ACTIVITY_ALLOWED_EXTENSIONS'
        if file_type == 'activity'
        else 'PICTURE_ALLOWED_EXTENSIONS'
    )

    file_extension = (
        file.filename.rsplit('.', 1)[1].lower()
        if '.' in file.filename
        else None
    )
    max_file_size = current_app.config['max_single_file_size']

    if not (
        file_extension
        and file_extension in current_app.config[allowed_extensions]
    ):
        return InvalidPayloadErrorResponse(
            'File extension not allowed.', 'fail'
        )

    if file_extension != 'zip' and req.content_length > max_file_size:
        return PayloadTooLargeErrorResponse(
            'Error during picture update, file size exceeds '
            f'{display_readable_file_size(max_file_size)}.'
        )

    return None


def verify_user(
    current_request: Request, verify_admin: bool
) -> Tuple[Optional[HttpResponse], Optional[int]]:
    """
    Return user id, if the provided token is valid and if user has admin
    rights if 'verify_admin' is True
    """
    default_message = 'Provide a valid auth token.'
    auth_header = current_request.headers.get('Authorization')
    if not auth_header:
        return UnauthorizedErrorResponse(default_message), None
    auth_token = auth_header.split(' ')[1]
    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
        return UnauthorizedErrorResponse(resp), None
    user = User.query.filter_by(id=resp).first()
    if not user:
        return UnauthorizedErrorResponse(default_message), None
    if verify_admin and not is_admin(resp):
        return ForbiddenErrorResponse(), None
    return None, resp


def authenticate(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(
        *args: Any, **kwargs: Any
    ) -> Union[Callable, HttpResponse]:
        verify_admin = False
        response_object, resp = verify_user(request, verify_admin)
        if response_object:
            return response_object
        return f(resp, *args, **kwargs)

    return decorated_function


def authenticate_as_admin(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(
        *args: Any, **kwargs: Any
    ) -> Union[Callable, HttpResponse]:
        verify_admin = True
        response_object, resp = verify_user(request, verify_admin)
        if response_object:
            return response_object
        return f(resp, *args, **kwargs)

    return decorated_function


def can_view_activity(
    auth_user_id: int, activity_user_id: int
) -> Optional[HttpResponse]:
    """
    Return error response if user has no right to view activity
    """
    if auth_user_id != activity_user_id:
        return ForbiddenErrorResponse()
    return None


def display_readable_file_size(size_in_bytes: Union[float, int]) -> str:
    """
    Return readable file size from size in bytes
    """
    if size_in_bytes == 0:
        return '0 bytes'
    if size_in_bytes == 1:
        return '1 byte'
    for unit in [' bytes', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_in_bytes) < 1024.0:
            return f'{size_in_bytes:3.1f}{unit}'
        size_in_bytes /= 1024.0
    return f'{size_in_bytes} bytes'


def get_readable_duration(duration: int, locale: Optional[str] = 'en') -> str:
    """
    Return readable and localized duration from duration in seconds
    """
    if locale is not None and locale != 'en':
        _t = humanize.i18n.activate(locale)  # noqa
    readable_duration = humanize.naturaldelta(timedelta(seconds=duration))
    if locale is not None and locale != 'en':
        humanize.i18n.deactivate()
    return readable_duration

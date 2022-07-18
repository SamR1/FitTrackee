import re
from typing import Optional, Tuple

from flask import Request

from fittrackee.responses import (
    ForbiddenErrorResponse,
    HttpResponse,
    UnauthorizedErrorResponse,
)

from ..models import User


def is_valid_email(email: str) -> bool:
    """
    Return if email format is valid
    """
    if not email:
        return False
    mail_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(mail_pattern, email) is not None


def check_password(password: str) -> str:
    """
    Verify if password have more than 8 characters
    If not, it returns error message
    """
    if len(password) < 8:
        return 'password: 8 characters required\n'
    return ''


def check_username(username: str) -> str:
    """
    Return if username is valid
    If not, it returns error messages
    """
    ret = ''
    if not (2 < len(username) < 31):
        ret += 'username: 3 to 30 characters required\n'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        ret += (
            'username: only alphanumeric characters and the '
            'underscore character "_" allowed\n'
        )
    return ret


def register_controls(username: str, email: str, password: str) -> str:
    """
    Verify if username, email and passwords are valid
    If not, it returns error messages
    """
    ret = check_username(username)
    if not is_valid_email(email):
        ret += 'email: valid email must be provided\n'
    ret += check_password(password)
    return ret


def verify_user(
    current_request: Request, verify_admin: bool
) -> Tuple[Optional[HttpResponse], Optional[User]]:
    """
    Return authenticated user if
    - the provided token is valid
    - the user account is active
    - the user has admin rights if 'verify_admin' is True

    If not, it returns Error Response
    """
    default_message = 'provide a valid auth token'
    auth_header = current_request.headers.get('Authorization')
    if not auth_header:
        return UnauthorizedErrorResponse(default_message), None
    auth_token = auth_header.split(' ')[1]
    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
        return UnauthorizedErrorResponse(resp), None
    user = User.query.filter_by(id=resp).first()
    if not user or not user.is_active:
        return UnauthorizedErrorResponse(default_message), None
    if verify_admin and not user.admin:
        return ForbiddenErrorResponse(), None
    return None, user

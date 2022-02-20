from functools import wraps
from typing import Any, Callable, Optional, Union

from flask import Request, request

from fittrackee.responses import HttpResponse
from fittrackee.users.models import User

from .utils.controls import verify_user


def verify_auth_user(
    f: Callable, verify_admin: bool, *args: Any, **kwargs: Any
) -> Union[Callable, HttpResponse]:
    response_object, user = verify_user(request, verify_admin=verify_admin)
    if response_object:
        return response_object
    return f(user, *args, **kwargs)


def authenticate(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(
        *args: Any, **kwargs: Any
    ) -> Union[Callable, HttpResponse]:
        verify_admin = False
        return verify_auth_user(f, verify_admin, *args, **kwargs)

    return decorated_function


def authenticate_as_admin(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(
        *args: Any, **kwargs: Any
    ) -> Union[Callable, HttpResponse]:
        verify_admin = True
        return verify_auth_user(f, verify_admin, *args, **kwargs)

    return decorated_function


def get_auth_user(
    current_request: Request,
) -> Optional[User]:
    """
    Return user if a user is authenticated
    """
    user = None
    auth_header = current_request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(' ')[1]
        resp = User.decode_auth_token(auth_token)
        if isinstance(resp, int):
            user = User.query.filter_by(id=resp).first()
    return user


def get_auth_user_if_authenticated(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(
        *args: Any, **kwargs: Any
    ) -> Union[Callable, HttpResponse]:
        user = get_auth_user(request)
        return f(user, *args, **kwargs)

    return decorated_function

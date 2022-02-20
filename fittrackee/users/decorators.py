from functools import wraps
from typing import Any, Callable, Union

from flask import request

from fittrackee.responses import HttpResponse

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

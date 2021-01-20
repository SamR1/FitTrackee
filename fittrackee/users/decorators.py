from functools import wraps
from typing import Any, Callable, Union

from flask import request

from fittrackee.responses import HttpResponse

from .utils import verify_user


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

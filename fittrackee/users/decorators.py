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
        response_object, user = verify_user(request, verify_admin=False)
        if response_object:
            return response_object
        return f(user, *args, **kwargs)

    return decorated_function


def authenticate_as_admin(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(
        *args: Any, **kwargs: Any
    ) -> Union[Callable, HttpResponse]:
        response_object, user = verify_user(request, verify_admin=True)
        if response_object:
            return response_object
        return f(user, *args, **kwargs)

    return decorated_function

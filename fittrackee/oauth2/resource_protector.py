from functools import wraps
from typing import Any, Callable, List, Union

from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2 import OAuth2Error
from authlib.oauth2.rfc6749.errors import MissingAuthorizationError
from flask import current_app, request
from werkzeug.exceptions import RequestEntityTooLarge

from fittrackee.responses import (
    ForbiddenErrorResponse,
    PayloadTooLargeErrorResponse,
    UnauthorizedErrorResponse,
)
from fittrackee.users.models import User


class CustomResourceProtector(ResourceProtector):
    def __call__(
        self,
        scopes: Union[str, List, None] = None,
        as_admin: bool = False,
    ) -> Callable:
        def wrapper(f: Callable) -> Callable:
            @wraps(f)
            def decorated(*args: Any, **kwargs: Any) -> Callable:
                auth_user = None
                auth_header = request.headers.get('Authorization')
                if not auth_header:
                    return UnauthorizedErrorResponse(
                        'provide a valid auth token'
                    )

                # First-party application (Fittrackee front-end)
                # in this case, scopes will be ignored
                auth_token = auth_header.split(' ')[1]
                resp = User.decode_auth_token(auth_token)
                if isinstance(resp, int):
                    auth_user = User.query.filter_by(id=resp).first()

                # Third-party applications
                if not auth_user:
                    current_token = None
                    try:
                        current_token = self.acquire_token(scopes)
                    except MissingAuthorizationError as error:
                        self.raise_error_response(error)
                    except OAuth2Error as error:
                        self.raise_error_response(error)
                    except RequestEntityTooLarge:
                        file_type = ''
                        if request.endpoint in [
                            'auth.edit_picture',
                            'workouts.post_workout',
                        ]:
                            file_type = (
                                'picture'
                                if request.endpoint == 'auth.edit_picture'
                                else 'workout'
                            )
                        return PayloadTooLargeErrorResponse(
                            file_type=file_type,
                            file_size=request.content_length,
                            max_size=current_app.config['MAX_CONTENT_LENGTH'],
                        )
                    auth_user = (
                        None if current_token is None else current_token.user
                    )

                if not auth_user or not auth_user.is_active:
                    return UnauthorizedErrorResponse(
                        'provide a valid auth token'
                    )
                if as_admin and not auth_user.admin:
                    return ForbiddenErrorResponse()
                return f(auth_user, *args, **kwargs)

            return decorated

        return wrapper

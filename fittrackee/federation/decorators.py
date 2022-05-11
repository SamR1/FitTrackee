from functools import wraps
from typing import Any, Callable

from flask import current_app

from fittrackee import appLog
from fittrackee.federation.exceptions import FederationDisabledException
from fittrackee.responses import (
    DisabledFederationErrorResponse,
    InternalServerErrorResponse,
    UserNotFoundErrorResponse,
)

from .models import Actor, Domain


def federation_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Callable:
        if not current_app.config['federation_enabled']:
            raise FederationDisabledException()
        return f(*args, **kwargs)

    return decorated_function


def federation_required_for_route(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Callable:
        if not current_app.config['federation_enabled']:
            return DisabledFederationErrorResponse()
        app_domain = Domain.query.filter_by(
            name=current_app.config['AP_DOMAIN']
        ).first()
        if not app_domain:
            appLog.error('Local domain does not exist.')
            return InternalServerErrorResponse()
        return f(app_domain, *args, **kwargs)

    return decorated_function


def get_local_actor_from_username(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Callable:
        app_domain = args[0]
        preferred_username = kwargs.get('preferred_username')
        if not preferred_username:
            return UserNotFoundErrorResponse()
        actor = Actor.query.filter_by(
            preferred_username=preferred_username,
            domain_id=app_domain.id,
        ).first()
        if not actor:
            return UserNotFoundErrorResponse()
        return f(actor, *args, **kwargs)

    return decorated_function

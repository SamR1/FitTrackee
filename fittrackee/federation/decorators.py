from functools import wraps
from typing import Any, Callable

from flask import current_app

from fittrackee import appLog
from fittrackee.responses import (
    DisabledFederationErrorResponse,
    InternalServerErrorResponse,
)

from .models import Domain


def federation_required(f: Callable) -> Callable:
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

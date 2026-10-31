from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

import jwt
from flask import current_app
from flask_jwt_extended import (
    create_access_token,
    get_current_user,
    get_jwt,
    verify_jwt_in_request,
)

from fittrackee.utils import clean

from ..exceptions import InvalidJWT

if TYPE_CHECKING:
    from fittrackee.users.models import User


def get_user_token(user_id: int) -> str:
    token = create_access_token(
        identity=str(user_id), additional_claims={"type": "auth"}
    )
    return token


def check_auth_token(optional_auth_user: bool) -> Optional["User"]:
    auth_user = None
    try:
        verify_jwt_in_request(optional=optional_auth_user)
        auth_user = get_current_user()
    except jwt.DecodeError:
        pass
    if auth_user:
        payload = get_jwt()
        if payload["type"] != "auth":
            raise InvalidJWT()
    return auth_user


def get_password_reset_token(
    user_id: int, type_claim: str = "password_reset"
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "exp": (
            now
            + timedelta(
                seconds=current_app.config["PASSWORD_TOKEN_EXPIRATION_SECONDS"]
            )
        ),
        "iat": now,
        "jti": str(uuid4()),
        "sub": str(user_id),
        "type": type_claim,
    }
    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def decode_password_reset_token(auth_token: str) -> dict:
    payload = jwt.decode(
        auth_token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"],
    )
    if payload.get("type") != "password_reset":
        raise InvalidJWT()
    return payload


def clean_blacklisted_tokens(days: int) -> int:
    """
    Delete blacklisted tokens expired for more than provided number of days
    """
    sql = """
        DELETE FROM blacklisted_tokens
        WHERE blacklisted_tokens.expired_at < :limit;
    """
    return clean(sql, days)

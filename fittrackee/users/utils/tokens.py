from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from flask import current_app
from flask_jwt_extended import create_access_token

from fittrackee.utils import clean

from ..exceptions import InvalidJWTClaim


def get_user_token(user_id: int) -> str:
    token = create_access_token(
        identity=str(user_id), additional_claims={"type": "auth"}
    )
    return token


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
        raise InvalidJWTClaim("invalid token, please request a new token")
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

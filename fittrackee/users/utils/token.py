from datetime import datetime, timedelta
from typing import Optional

import jwt
from flask import current_app

from fittrackee.utils import clean


def get_user_token(
    user_id: int, password_reset: Optional[bool] = False
) -> str:
    """
    Return authentication token for a given user.
    Token expiration time depends on token type (authentication or password
    reset)
    """
    expiration_days: float = (
        0.0 if password_reset else current_app.config['TOKEN_EXPIRATION_DAYS']
    )
    expiration_seconds: float = (
        current_app.config['PASSWORD_TOKEN_EXPIRATION_SECONDS']
        if password_reset
        else current_app.config['TOKEN_EXPIRATION_SECONDS']
    )
    now = datetime.utcnow()
    payload = {
        'exp': now
        + timedelta(days=expiration_days, seconds=expiration_seconds),
        'iat': now,
        'sub': user_id,
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256',
    )


def decode_user_token(auth_token: str) -> int:
    """
    Return user id from token
    """
    payload = jwt.decode(
        auth_token,
        current_app.config['SECRET_KEY'],
        algorithms=['HS256'],
    )
    return payload['sub']


def clean_blacklisted_tokens(days: int) -> int:
    """
    Delete blacklisted tokens expired for more than provided number of days
    """
    sql = """
        DELETE FROM blacklisted_tokens
        WHERE blacklisted_tokens.expired_at < %(limit)s;
    """
    return clean(sql, days)

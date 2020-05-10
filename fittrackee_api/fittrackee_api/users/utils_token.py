from datetime import datetime, timedelta

import jwt
from flask import current_app


def get_user_token(user_id, password_reset=False):
    expiration_days = (
        0
        if password_reset
        else current_app.config.get('TOKEN_EXPIRATION_DAYS')
    )
    expiration_seconds = (
        current_app.config.get('PASSWORD_TOKEN_EXPIRATION_SECONDS')
        if password_reset
        else current_app.config.get('TOKEN_EXPIRATION_SECONDS')
    )
    payload = {
        'exp': datetime.utcnow()
        + timedelta(days=expiration_days, seconds=expiration_seconds),
        'iat': datetime.utcnow(),
        'sub': user_id,
    }
    return jwt.encode(
        payload, current_app.config.get('SECRET_KEY'), algorithm='HS256',
    )


def decode_user_token(auth_token):
    payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
    return payload['sub']

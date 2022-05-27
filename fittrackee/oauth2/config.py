from authlib.oauth2.rfc7636 import CodeChallenge
from flask import Flask

from .grants import AuthorizationCodeGrant, RefreshTokenGrant
from .server import authorization_server


def config_oauth(app: Flask) -> None:
    authorization_server.init_app(app)

    # supported grants
    authorization_server.register_grant(
        AuthorizationCodeGrant, [CodeChallenge(required=True)]
    )
    authorization_server.register_grant(RefreshTokenGrant)

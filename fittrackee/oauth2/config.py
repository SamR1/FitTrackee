from authlib.integrations.sqla_oauth2 import (
    create_bearer_token_validator,
    create_revocation_endpoint,
)
from authlib.oauth2.rfc7636 import CodeChallenge
from flask import Flask

from fittrackee import db

from .grants import AuthorizationCodeGrant, OAuth2Token, RefreshTokenGrant
from .server import authorization_server, require_auth


def config_oauth(app: Flask) -> None:
    authorization_server.init_app(app)

    # supported grants
    authorization_server.register_grant(
        AuthorizationCodeGrant, [CodeChallenge(required=True)]
    )
    authorization_server.register_grant(RefreshTokenGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    revocation_cls.CLIENT_AUTH_METHODS = ['client_secret_post']
    authorization_server.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_auth.register_token_validator(bearer_cls())

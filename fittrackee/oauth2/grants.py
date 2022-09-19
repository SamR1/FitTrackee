import time
from typing import Optional

from authlib.oauth2 import OAuth2Request
from authlib.oauth2.rfc6749 import grants

from fittrackee import db
from fittrackee.users.models import User

from .models import OAuth2AuthorizationCode, OAuth2Client, OAuth2Token


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_post']

    def save_authorization_code(
        self, code: str, request: OAuth2Request
    ) -> OAuth2AuthorizationCode:
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        db.session.add(auth_code)
        db.session.commit()
        return auth_code

    def query_authorization_code(
        self, code: str, client: OAuth2Client
    ) -> Optional[OAuth2AuthorizationCode]:
        auth_code = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id
        ).first()
        if auth_code and not auth_code.is_expired():
            return auth_code
        return None

    def delete_authorization_code(
        self, authorization_code: OAuth2AuthorizationCode
    ) -> None:
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(
        self, authorization_code: OAuth2AuthorizationCode
    ) -> User:
        return User.query.get(authorization_code.user_id)


class RefreshTokenGrant(grants.RefreshTokenGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_post']
    INCLUDE_NEW_REFRESH_TOKEN = True

    def authenticate_refresh_token(self, refresh_token: str) -> Optional[str]:
        token = OAuth2Token.query.filter_by(
            refresh_token=refresh_token
        ).first()
        if token and token.is_refresh_token_active():
            return token
        return None

    def authenticate_user(self, credential: OAuth2Token) -> User:
        return User.query.get(credential.user_id)

    def revoke_old_credential(self, credential: OAuth2Token) -> None:
        credential.access_token_revoked_at = time.time()
        db.session.commit()

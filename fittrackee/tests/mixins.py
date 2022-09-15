import json
import time
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs

from flask import Flask
from flask.testing import FlaskClient
from urllib3.util import parse_url
from werkzeug.test import TestResponse

from fittrackee import db
from fittrackee.oauth2.client import create_oauth2_client
from fittrackee.oauth2.models import OAuth2Client, OAuth2Token
from fittrackee.users.models import User

from .custom_asserts import (
    assert_errored_response,
    assert_oauth_errored_response,
)
from .utils import (
    TEST_OAUTH_CLIENT_METADATA,
    random_email,
    random_int,
    random_string,
)


class RandomMixin:
    @staticmethod
    def random_string(
        length: Optional[int] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> str:
        return random_string(length, prefix, suffix)

    @staticmethod
    def random_domain() -> str:
        return random_string(prefix='https://', suffix='com')

    @staticmethod
    def random_email() -> str:
        return random_email()

    @staticmethod
    def random_int(min_val: int = 0, max_val: int = 999999) -> int:
        return random_int(min_val, max_val)


class OAuth2Mixin(RandomMixin):
    @staticmethod
    def create_oauth2_client(
        user: User,
        metadata: Optional[Dict] = None,
        scope: Optional[str] = None,
    ) -> OAuth2Client:
        client_metadata = (
            TEST_OAUTH_CLIENT_METADATA if metadata is None else metadata
        )
        if scope is not None:
            client_metadata['scope'] = scope
        oauth_client = create_oauth2_client(client_metadata, user)
        db.session.add(oauth_client)
        db.session.commit()
        return oauth_client

    def create_oauth2_token(
        self,
        oauth_client: OAuth2Client,
        issued_at: Optional[int] = None,
        access_token_revoked_at: Optional[int] = 0,
        expires_in: Optional[int] = 1000,
    ) -> OAuth2Token:
        issued_at = issued_at if issued_at else int(time.time())
        token = OAuth2Token(
            client_id=oauth_client.client_id,
            access_token=self.random_string(),
            refresh_token=self.random_string(),
            issued_at=issued_at,
            access_token_revoked_at=access_token_revoked_at,
            expires_in=expires_in,
        )
        db.session.add(token)
        db.session.commit()
        return token


class ApiTestCaseMixin(OAuth2Mixin, RandomMixin):
    @staticmethod
    def get_test_client_and_auth_token(
        app: Flask, user_email: str
    ) -> Tuple[FlaskClient, str]:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(
                    email=user_email,
                    password='12345678',
                )
            ),
            content_type='application/json',
        )
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        return client, auth_token

    @staticmethod
    def authorize_client(
        client: FlaskClient,
        oauth_client: OAuth2Client,
        auth_token: str,
        scope: Optional[str] = None,
        code_challenge: Optional[Dict] = None,
    ) -> Union[List[str], str]:
        if code_challenge is None:
            code_challenge = {}
        response = client.post(
            '/api/oauth/authorize',
            data={
                'client_id': oauth_client.client_id,
                'confirm': True,
                'response_type': 'code',
                'scope': 'read' if not scope else scope,
                **code_challenge,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )
        data = json.loads(response.data.decode())
        parsed_url = parse_url(data['redirect_url'])
        code = parse_qs(parsed_url.query).get('code', '')
        return code

    def create_oauth2_client_and_issue_token(
        self, app: Flask, user: User, scope: Optional[str] = None
    ) -> Tuple[FlaskClient, OAuth2Client, str, str]:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user.email
        )
        oauth_client = self.create_oauth2_client(user, scope=scope)
        code = self.authorize_client(
            client, oauth_client, auth_token, scope=scope
        )
        response = client.post(
            '/api/oauth/token',
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )
        data = json.loads(response.data.decode())
        return client, oauth_client, data.get('access_token'), auth_token

    @staticmethod
    def assert_400(
        response: TestResponse,
        error_message: Optional[str] = 'invalid payload',
        status: Optional[str] = 'error',
    ) -> Dict:
        return assert_errored_response(
            response, 400, error_message=error_message, status=status
        )

    @staticmethod
    def assert_401(
        response: TestResponse,
        error_message: Optional[str] = 'provide a valid auth token',
    ) -> Dict:
        return assert_errored_response(
            response, 401, error_message=error_message
        )

    @staticmethod
    def assert_403(
        response: TestResponse,
        error_message: Optional[str] = 'you do not have permissions',
    ) -> Dict:
        return assert_errored_response(response, 403, error_message)

    @staticmethod
    def assert_404(response: TestResponse) -> Dict:
        return assert_errored_response(response, 404, status='not found')

    @staticmethod
    def assert_404_with_entity(response: TestResponse, entity: str) -> Dict:
        error_message = f'{entity} does not exist'
        return assert_errored_response(
            response, 404, error_message=error_message, status='not found'
        )

    @staticmethod
    def assert_404_with_message(
        response: TestResponse, error_message: str
    ) -> Dict:
        return assert_errored_response(
            response, 404, error_message=error_message, status='not found'
        )

    @staticmethod
    def assert_413(
        response: TestResponse,
        error_message: Optional[str] = None,
        match: Optional[str] = None,
    ) -> Dict:
        return assert_errored_response(
            response,
            413,
            error_message=error_message,
            status='fail',
            match=match,
        )

    @staticmethod
    def assert_500(
        response: TestResponse,
        error_message: Optional[str] = (
            'error, please try again or contact the administrator'
        ),
        status: Optional[str] = 'error',
    ) -> Dict:
        return assert_errored_response(
            response, 500, error_message=error_message, status=status
        )

    @staticmethod
    def assert_unsupported_grant_type(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response, 400, error='unsupported_grant_type'
        )

    @staticmethod
    def assert_invalid_client(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response,
            400,
            error='invalid_client',
        )

    @staticmethod
    def assert_invalid_request(
        response: TestResponse, error_description: Optional[str] = None
    ) -> Dict:
        return assert_oauth_errored_response(
            response,
            400,
            error='invalid_request',
            error_description=error_description,
        )

    @staticmethod
    def assert_invalid_token(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response,
            401,
            error='invalid_token',
            error_description=(
                'The access token provided is expired, revoked, malformed, '
                'or invalid for other reasons.'
            ),
        )

    @staticmethod
    def assert_insufficient_scope(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response,
            403,
            error='insufficient_scope',
            error_description=(
                'The request requires higher privileges than provided by '
                'the access token.'
            ),
        )

    @staticmethod
    def assert_not_insufficient_scope_error(response: TestResponse) -> None:
        assert response.status_code != 403

    def assert_response_scope(
        self, response: TestResponse, can_access: bool
    ) -> None:
        if can_access:
            self.assert_not_insufficient_scope_error(response)
        else:
            self.assert_insufficient_scope(response)


class CallArgsMixin:
    """call args are returned differently between Python 3.7 and 3.7+"""

    @staticmethod
    def get_args(call_args: Tuple) -> Tuple:
        if len(call_args) == 2:
            args, _ = call_args
        else:
            _, args, _ = call_args
        return args

    @staticmethod
    def get_kwargs(call_args: Tuple) -> Dict:
        if len(call_args) == 2:
            _, kwargs = call_args
        else:
            _, _, kwargs = call_args
        return kwargs

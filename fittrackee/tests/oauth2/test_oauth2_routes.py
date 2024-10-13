import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from unittest.mock import patch

import pytest
from authlib.common.security import generate_token
from authlib.oauth2.rfc7636 import create_s256_code_challenge
from flask import Flask
from werkzeug.test import TestResponse

from fittrackee.oauth2.models import (
    OAuth2AuthorizationCode,
    OAuth2Client,
    OAuth2Token,
)
from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import TEST_OAUTH_CLIENT_METADATA


class TestOAuthClientCreation(ApiTestCaseMixin):
    route = '/api/oauth/apps'

    def test_it_returns_error_when_no_user_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=json.dumps(TEST_OAUTH_CLIENT_METADATA),
            content_type='application/json',
        )

        self.assert_401(response)

    def test_it_returns_error_when_no_metadata_provided(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=json.dumps(dict()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, error_message='OAuth2 client metadata missing'
        )

    @pytest.mark.parametrize(
        'missing_key',
        [
            'client_name',
            'client_uri',
            'redirect_uris',
            'scope',
        ],
    )
    def test_it_returns_error_when_metadata_key_is_missing(
        self, app: Flask, user_1: User, missing_key: str
    ) -> None:
        metadata = TEST_OAUTH_CLIENT_METADATA.copy()
        del metadata[missing_key]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=json.dumps(metadata),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response,
            error_message=(
                f'OAuth2 client metadata missing keys: {missing_key}'
            ),
        )

    def test_it_returns_error_when_scope_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        invalid_scope = self.random_string()
        metadata: Dict = {
            **TEST_OAUTH_CLIENT_METADATA,
            'scope': invalid_scope,
        }
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=json.dumps(metadata),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response,
            error_message='OAuth2 client invalid scopes',
        )

    def test_it_creates_oauth_client(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=json.dumps(TEST_OAUTH_CLIENT_METADATA),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 201
        oauth_client = OAuth2Client.query.first()
        assert oauth_client is not None

    def test_suspended_user_can_not_create_oauth_client(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            self.route,
            data=json.dumps(TEST_OAUTH_CLIENT_METADATA),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_serialized_oauth_client(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client_id = self.random_string()
        client_secret = self.random_string()
        with patch(
            'fittrackee.oauth2.client.gen_salt',
            side_effect=[client_id, client_secret],
        ):
            response = client.post(
                self.route,
                data=json.dumps(TEST_OAUTH_CLIENT_METADATA),
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        data = json.loads(response.data.decode())
        assert data['data']['client']['client_id'] == client_id
        assert data['data']['client']['client_secret'] == client_secret
        assert data['data']['client']['id'] is not None
        assert (
            data['data']['client']['name']
            == TEST_OAUTH_CLIENT_METADATA['client_name']
        )
        assert (
            data['data']['client']['redirect_uris']
            == TEST_OAUTH_CLIENT_METADATA['redirect_uris']
        )
        assert (
            data['data']['client']['website']
            == TEST_OAUTH_CLIENT_METADATA['client_uri']
        )

    @pytest.mark.parametrize(
        'input_key,expected_value',
        [
            ('grant_types', ['authorization_code', 'refresh_token']),
            ('response_types', ['code']),
            ('token_endpoint_auth_method', 'client_secret_post'),
        ],
    )
    def test_it_always_creates_oauth_client_with_authorization_grant(
        self,
        app: Flask,
        user_1: User,
        input_key: str,
        expected_value: Union[List, str],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            self.route,
            data=json.dumps(
                {**TEST_OAUTH_CLIENT_METADATA, input_key: self.random_string()}
            ),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        oauth_client = OAuth2Client.query.first()
        assert getattr(oauth_client, input_key) == expected_value


class TestOAuthClientAuthorization(ApiTestCaseMixin):
    route = '/api/oauth/authorize'

    def test_it_returns_error_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                'confirm': True,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_401(response)

    def test_it_returns_error_when_user_is_suspended(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        user_1.suspended_at = datetime.utcnow()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                'confirm': True,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        self.assert_403(response)

    def test_it_returns_error_when_client_id_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data={'response_type': 'code'},
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        self.assert_400(response, error_message='invalid payload')

    def test_it_returns_error_when_response_type_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)

        response = client.post(
            self.route,
            data={'client_id': oauth_client.client_id},
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        self.assert_400(response, error_message='invalid payload')

    def test_it_returns_error_when_response_type_is_not_code(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': self.random_string(),
                'confirm': True,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        self.assert_400(response, error_message='invalid payload')

    @pytest.mark.parametrize(
        'input_confirmation', [{'confirm': True}, {'confirm': 'true'}]
    )
    def test_it_creates_authorization_code(
        self, app: Flask, user_1: User, input_confirmation: Dict
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)

        client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                **input_confirmation,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        code = OAuth2AuthorizationCode.query.filter_by(
            client_id=oauth_client.client_id
        ).first()
        assert code is not None

    @pytest.mark.parametrize('input_confirmation', [{}, {'confirm': False}])
    def test_it_does_not_create_authorization_code_when_no_confirmation(
        self, app: Flask, user_1: User, input_confirmation: Dict
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)

        client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                **input_confirmation,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        code = OAuth2AuthorizationCode.query.filter_by(
            client_id=oauth_client.client_id
        ).first()
        assert code is None

    def test_it_returns_redirect_url_with_code(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                'confirm': True,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        code = OAuth2AuthorizationCode.query.filter_by(
            client_id=oauth_client.client_id
        ).first()

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['redirect_url'] == (
            f'{oauth_client.get_default_redirect_uri()}?code={code.code}'
        )

    @pytest.mark.parametrize(
        'input_confirmation', [{}, {'confirm': False}, {'confirm': 'false'}]
    )
    def test_it_returns_error_when_no_confirmation(
        self, app: Flask, user_1: User, input_confirmation: Dict
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                **input_confirmation,
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        self.assert_400(
            response,
            error_message=(
                'The resource owner or authorization server denied the request'
            ),
        )


class TestOAuthClientAuthorizationWithCodeChallenge(ApiTestCaseMixin):
    route = '/api/oauth/authorize'

    def test_it_returns_error_when_code_challenge_method_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        code_verifier = generate_token(48)
        code_challenge = create_s256_code_challenge(code_verifier)

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                'confirm': 'true',
                'code_challenge': code_challenge,
                'code_challenge_method': self.random_string(),
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        self.assert_400(response, 'Unsupported "code_challenge_method"')

    def test_it_creates_authorization_code(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        code_verifier = generate_token(48)
        code_challenge = create_s256_code_challenge(code_verifier)

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'response_type': 'code',
                'confirm': 'true',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256',
            },
            headers=dict(
                Authorization=f'Bearer {auth_token}',
                content_type='multipart/form-data',
            ),
        )

        code = OAuth2AuthorizationCode.query.filter_by(
            client_id=oauth_client.client_id
        ).first()
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['redirect_url'] == (
            f'{oauth_client.get_default_redirect_uri()}?code={code.code}'
        )


class OAuthIssueTokenTestCase(ApiTestCaseMixin):
    def create_authorized_oauth_client(
        self, app: Flask, user_1: User, code_challenge: Optional[Dict] = None
    ) -> Tuple[OAuth2Client, Union[List[str], str]]:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        code = self.authorize_client(
            client, oauth_client, auth_token, code_challenge=code_challenge
        )
        return oauth_client, code

    @staticmethod
    def assert_token_is_returned(response: TestResponse) -> Dict:
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data.get('access_token') is not None
        assert data.get('expires_in') == 60  # test config
        assert data.get('refresh_token') is not None
        assert data.get('token_type') == 'Bearer'
        return data


class TestOAuthIssueAccessToken(OAuthIssueTokenTestCase):
    route = '/api/oauth/token'

    def test_it_returns_error_when_form_is_empty(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            self.route,
            data=dict(data='{}'),
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_unsupported_grant_type(response)

    def test_it_returns_error_when_client_id_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, code = self.create_authorized_oauth_client(app, user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': self.random_string(),
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_invalid_client(response)

    def test_it_returns_error_when_client_secret_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, code = self.create_authorized_oauth_client(app, user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': self.random_string(),
                'grant_type': 'authorization_code',
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_invalid_client(response)

    def test_it_returns_error_when_client_not_authorized(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': self.random_string(),
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_invalid_grant(response)

    def test_it_returns_error_when_grant_type_is_not_authorization_code(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, code = self.create_authorized_oauth_client(app, user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': self.random_string(),
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_unsupported_grant_type(response)

    def test_it_returns_error_when_code_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, _ = self.create_authorized_oauth_client(app, user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': self.random_string(),
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_invalid_grant(response)

    def test_it_returns_access_token(self, app: Flask, user_1: User) -> None:
        oauth_client, code = self.create_authorized_oauth_client(app, user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_token_is_returned(response)

    def test_it_returns_access_token_when_user_is_suspended(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, code = self.create_authorized_oauth_client(app, user_1)
        client = app.test_client()
        user_1.suspended_at = datetime.utcnow()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_token_is_returned(response)


class TestOAuthIssueAccessTokenWithCodeChallenge(OAuthIssueTokenTestCase):
    route = '/api/oauth/token'

    def test_it_returns_error_when_grant_type_is_not_authorization_code(
        self, app: Flask, user_1: User
    ) -> None:
        code_verifier = generate_token(48)
        oauth_client, code = self.create_authorized_oauth_client(
            app,
            user_1,
            code_challenge={
                'code_challenge': create_s256_code_challenge(code_verifier),
                'code_challenge_method': 'S256',
            },
        )
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': self.random_string(),
                'code': code,
                'code_verifier': code_verifier,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_unsupported_grant_type(response)

    def test_it_raises_error_when_code_verifier_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        code_verifier = generate_token(48)
        code_challenge = create_s256_code_challenge(code_verifier)
        oauth_client, code = self.create_authorized_oauth_client(
            app,
            user_1,
            {
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256',
            },
        )
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'code_verifier': self.random_string(),
            },
            headers=dict(content_type='multipart/form-data'),
        )
        self.assert_invalid_request(response, 'Invalid "code_verifier"')

    def test_it_returns_access_token(self, app: Flask, user_1: User) -> None:
        code_verifier = generate_token(48)
        oauth_client, code = self.create_authorized_oauth_client(
            app,
            user_1,
            code_challenge={
                'code_challenge': create_s256_code_challenge(code_verifier),
                'code_challenge_method': 'S256',
            },
        )
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
                'code_verifier': code_verifier,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_token_is_returned(response)


class TestOAuthIssueRefreshToken(OAuthIssueTokenTestCase):
    route = '/api/oauth/token'

    def generate_token(
        self, app: Flask, user_1: User
    ) -> Tuple[OAuth2Client, Dict]:
        oauth_client, code = self.create_authorized_oauth_client(app, user_1)
        response = app.test_client().post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'authorization_code',
                'code': code,
            },
            headers=dict(content_type='multipart/form-data'),
        )
        return oauth_client, json.loads(response.data.decode())

    def test_it_returns_new_token_when_grant_is_refresh_token(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, token = self.generate_token(app, user_1)
        client = app.test_client()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
            },
            headers=dict(content_type='multipart/form-data'),
        )

        data = self.assert_token_is_returned(response)
        assert data['access_token'] != token['access_token']
        new_token = OAuth2Token.query.filter_by(
            access_token=token['access_token']
        ).first()
        assert new_token is not None

    def test_it_returns_new_token_when_grant_is_refresh_token_and_user_is_suspended(  # noqa
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client, token = self.generate_token(app, user_1)
        client = app.test_client()
        user_1.suspended_at = datetime.utcnow()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
            },
            headers=dict(content_type='multipart/form-data'),
        )

        data = self.assert_token_is_returned(response)
        assert data['access_token'] != token['access_token']
        new_token = OAuth2Token.query.filter_by(
            access_token=token['access_token']
        ).first()
        assert new_token is not None

    def test_it_revokes_old_token(self, app: Flask, user_1: User) -> None:
        oauth_client, token = self.generate_token(app, user_1)
        client = app.test_client()

        client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
            },
            headers=dict(content_type='multipart/form-data'),
        )

        revoked_token = OAuth2Token.query.filter_by(
            access_token=token['access_token']
        ).first()
        assert revoked_token.is_revoked()


class TestOAuthTokenRevocation(ApiTestCaseMixin):
    route = '/api/oauth/revoke'

    def test_it_revokes_user_token(self, app: Flask, user_1: User) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(app, user_1)

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'token': access_token,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        assert response.status_code == 200
        token = OAuth2Token.query.filter_by(
            client_id=oauth_client.client_id
        ).first()
        assert token.access_token_revoked_at is not None

    def test_it_revokes_user_token_when_user_is_suspended(
        self, app: Flask, user_1: User
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(app, user_1)
        user_1.suspended_at = datetime.utcnow()

        response = client.post(
            self.route,
            data={
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'token': access_token,
            },
            headers=dict(content_type='multipart/form-data'),
        )

        assert response.status_code == 200
        token = OAuth2Token.query.filter_by(
            client_id=oauth_client.client_id
        ).first()
        assert token.access_token_revoked_at is not None


class TestOAuthGetClients(ApiTestCaseMixin):
    route = '/api/oauth/apps'

    def test_it_returns_error_if_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type='application/json')

        self.assert_401(response)

    def test_it_returns_empty_list_when_no_clients(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['data']['clients'] == []

    def test_it_returns_apps_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )
        self.create_oauth2_client(suspended_user)

        response = client.get(
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['clients']) == 1
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_returns_pagination(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        [self.create_oauth2_client(user_1) for _ in range(7)]

        response = client.get(
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['clients']) == 5
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_returns_page_2(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        [self.create_oauth2_client(user_1) for _ in range(6)]

        response = client.get(
            f'{self.route}?page=2',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['clients']) == 1
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 6,
        }

    def test_it_returns_clients_order_by_id_descending(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        clients = [self.create_oauth2_client(user_1) for _ in range(7)]

        response = client.get(
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['data']['clients'][0]['client_id'] == clients[6].client_id
        assert data['data']['clients'][4]['client_id'] == clients[2].client_id

    def test_it_does_not_returns_clients_from_another_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        self.create_oauth2_client(user_2)

        response = client.get(
            self.route,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['data']['clients'] == []


class TestOAuthGetClientById(ApiTestCaseMixin):
    route = '/api/oauth/apps/{client_id}/by_id'

    def test_it_returns_error_when_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            self.route.format(client_id=self.random_int()),
            content_type='application/json',
        )

        self.assert_401(response)

    def test_it_returns_error_when_client_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(client_id=self.random_int()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')

    def test_it_returns_user_oauth_client(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client_description = self.random_string()
        oauth_client = self.create_oauth2_client(
            user_1,
            metadata={
                **TEST_OAUTH_CLIENT_METADATA,
                'client_description': client_description,
            },
        )
        client_id = oauth_client.id
        client_client_id = oauth_client.client_id

        response = client.get(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['client']['client_id'] == client_client_id
        assert 'client_secret' not in data['data']['client']
        assert (
            data['data']['client']['client_description'] == client_description
        )
        assert data['data']['client']['id'] == client_id
        assert (
            data['data']['client']['name']
            == TEST_OAUTH_CLIENT_METADATA['client_name']
        )
        assert (
            data['data']['client']['redirect_uris']
            == TEST_OAUTH_CLIENT_METADATA['redirect_uris']
        )
        assert (
            data['data']['client']['website']
            == TEST_OAUTH_CLIENT_METADATA['client_uri']
        )

    def test_it_returns_user_oauth_client_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )
        client_description = self.random_string()
        oauth_client = self.create_oauth2_client(
            suspended_user,
            metadata={
                **TEST_OAUTH_CLIENT_METADATA,
                'client_description': client_description,
            },
        )
        client_id = oauth_client.id
        client_client_id = oauth_client.client_id

        response = client.get(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['client']['client_id'] == client_client_id

    def test_it_does_not_return_oauth_client_from_another_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_2)

        response = client.get(
            self.route.format(client_id=oauth_client.id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')


class TestOAuthGetClientByClientId(ApiTestCaseMixin):
    route = '/api/oauth/apps/{client_id}'

    def test_it_returns_error_when_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            self.route.format(client_id=self.random_string()),
            content_type='application/json',
        )

        self.assert_401(response)

    def test_it_returns_error_when_client_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(client_id=self.random_string()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')

    def test_it_returns_user_oauth_client(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client_description = self.random_string()
        oauth_client = self.create_oauth2_client(
            user_1,
            metadata={
                **TEST_OAUTH_CLIENT_METADATA,
                'client_description': client_description,
            },
        )
        client_id = oauth_client.id
        client_client_id = oauth_client.client_id

        response = client.get(
            self.route.format(client_id=client_client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['client']['client_id'] == client_client_id
        assert 'client_secret' not in data['data']['client']
        assert (
            data['data']['client']['client_description'] == client_description
        )
        assert data['data']['client']['id'] == client_id
        assert (
            data['data']['client']['name']
            == TEST_OAUTH_CLIENT_METADATA['client_name']
        )
        assert (
            data['data']['client']['redirect_uris']
            == TEST_OAUTH_CLIENT_METADATA['redirect_uris']
        )
        assert (
            data['data']['client']['website']
            == TEST_OAUTH_CLIENT_METADATA['client_uri']
        )

    def test_it_returns_user_oauth_client_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )
        client_description = self.random_string()
        oauth_client = self.create_oauth2_client(
            suspended_user,
            metadata={
                **TEST_OAUTH_CLIENT_METADATA,
                'client_description': client_description,
            },
        )
        client_client_id = oauth_client.client_id

        response = client.get(
            self.route.format(client_id=client_client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['client']['client_id'] == client_client_id

    def test_it_does_not_return_oauth_client_from_another_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_2)

        response = client.get(
            self.route.format(client_id=oauth_client.client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')


class TestOAuthDeleteClient(ApiTestCaseMixin):
    route = '/api/oauth/apps/{client_id}'

    def test_it_returns_error_when_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.delete(
            self.route.format(client_id=self.random_int()),
            content_type='application/json',
        )

        self.assert_401(response)

    def test_it_returns_error_when_client_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(client_id=self.random_int()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')

    def test_it_deletes_user_oauth_client(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        client_id = oauth_client.id

        response = client.delete(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        deleted_client = OAuth2Client.query.filter_by(id=client_id).first()
        assert deleted_client is None

    def test_it_deletes_user_oauth_client_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )
        oauth_client = self.create_oauth2_client(suspended_user)
        client_id = oauth_client.id

        response = client.delete(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        deleted_client = OAuth2Client.query.filter_by(id=client_id).first()
        assert deleted_client is None

    def test_it_deletes_user_authorized_oauth_client(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        self.authorize_client(client, oauth_client, auth_token)
        client_id = oauth_client.id

        response = client.delete(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        deleted_client = OAuth2Client.query.filter_by(id=client_id).first()
        assert deleted_client is None

    def test_it_deletes_existing_code_associated_to_client(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        code = self.authorize_client(client, oauth_client, auth_token)
        client_id = oauth_client.id

        response = client.delete(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        deleted_code = OAuth2AuthorizationCode.query.filter_by(
            code=code[0]
        ).first()
        assert deleted_code is None

    def test_it_deletes_existing_token_associated_to_client(
        self, app: Flask, user_1: User
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            auth_token,
        ) = self.create_oauth2_client_and_issue_token(app, user_1)
        client_id = oauth_client.id

        response = client.delete(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        token = OAuth2Token.query.filter_by(access_token=access_token).first()
        assert token is None

    def test_it_can_not_delete_oauth_client_from_another_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_2)
        client_id = oauth_client.id

        response = client.delete(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')
        client = OAuth2Client.query.filter_by(id=client_id).first()
        assert client is not None


class TestOAuthRevokeClientToken(ApiTestCaseMixin):
    route = '/api/oauth/apps/{client_id}/revoke'

    def test_it_returns_error_when_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(client_id=self.random_int()),
            content_type='application/json',
        )

        self.assert_401(response)

    def test_it_returns_error_when_client_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(client_id=self.random_int()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'OAuth2 client not found')

    def test_it_revokes_all_client_tokens(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        tokens = [self.create_oauth2_token(oauth_client) for _ in range(3)]

        response = client.post(
            self.route.format(client_id=oauth_client.id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        for token in tokens:
            assert token.is_revoked()

    def test_it_revokes_client_tokens_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )
        oauth_client = self.create_oauth2_client(suspended_user)
        token = self.create_oauth2_token(oauth_client)

        response = client.post(
            self.route.format(client_id=oauth_client.id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert token.is_revoked()

    def test_it_does_not_revoke_another_client_token(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        oauth_client = self.create_oauth2_client(user_1)
        client_id = oauth_client.id
        another_client = self.create_oauth2_client(user_1)
        another_client_token = self.create_oauth2_token(another_client)

        response = client.post(
            self.route.format(client_id=client_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert not another_client_token.is_revoked()

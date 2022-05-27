import json
from typing import List, Union
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.oauth2.models import OAuth2Client
from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import random_domain, random_string

TEST_METADATA = {
    'client_name': random_string(),
    'client_uri': random_domain(),
    'redirect_uris': [random_domain()],
    'scope': 'read write',
}


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
            data=json.dumps(TEST_METADATA),
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
            response, error_message='OAuth client metadata missing'
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
        metadata = TEST_METADATA.copy()
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
            error_message=f'OAuth client metadata missing keys: {missing_key}',
        )

    def test_it_creates_oauth_client(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=json.dumps(TEST_METADATA),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 201
        oauth_client = OAuth2Client.query.first()
        assert oauth_client is not None

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
                data=json.dumps(TEST_METADATA),
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        data = json.loads(response.data.decode())
        assert data['data']['client']['client_id'] == client_id
        assert data['data']['client']['client_secret'] == client_secret
        assert data['data']['client']['name'] == TEST_METADATA['client_name']
        assert (
            data['data']['client']['redirect_uris']
            == TEST_METADATA['redirect_uris']
        )
        assert data['data']['client']['website'] == TEST_METADATA['client_uri']

    @pytest.mark.parametrize(
        'input_key,expected_value',
        [
            ('grant_types', ['authorization_code']),
            ('response_types', ['code']),
            ('token_endpoint_auth_method', 'client_secret_post'),
        ],
    )
    def test_it_always_create_oauth_client_with_authorization_grant(
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
                {**TEST_METADATA, input_key: self.random_string()}
            ),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        oauth_client = OAuth2Client.query.first()
        assert getattr(oauth_client, input_key) == expected_value

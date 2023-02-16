from time import time
from typing import Any, Dict
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.oauth2.client import check_scope, create_oauth2_client
from fittrackee.oauth2.exceptions import InvalidOAuth2Scopes
from fittrackee.oauth2.models import OAuth2Client
from fittrackee.users.models import User

from ..utils import random_domain, random_string

TEST_METADATA = {
    'client_name': random_string(),
    'client_uri': random_string(),
    'redirect_uris': [random_domain()],
    'scope': 'profile:read',
}


class TestCreateOAuth2Client:
    def test_it_creates_oauth_client(self, app: Flask, user_1: User) -> None:
        oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert isinstance(oauth_client, OAuth2Client)

    def test_oauth_client_id_is_generated_with_gen_salt(
        self, app: Flask, user_1: User
    ) -> None:
        client_id = random_string()
        with patch(
            'fittrackee.oauth2.client.gen_salt', return_value=client_id
        ):
            oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.client_id == client_id

    def test_oauth_client_client_id_issued_at_is_initialized(
        self, app: Flask, user_1: User
    ) -> None:
        client_id_issued_at = int(time())
        with patch(
            'fittrackee.oauth2.client.time', return_value=client_id_issued_at
        ):
            oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.client_id_issued_at == client_id_issued_at

    def test_oauth_client_has_expected_name(
        self, app: Flask, user_1: User
    ) -> None:
        client_name = random_string()
        client_metadata: Dict = {**TEST_METADATA, 'client_name': client_name}

        oauth_client = create_oauth2_client(client_metadata, user_1)

        assert oauth_client.client_name == client_name

    def test_oauth_client_has_no_description_when_not_provided_in_metadata(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.client_description is None

    def test_oauth_client_has_expected_description(
        self, app: Flask, user_1: User
    ) -> None:
        client_description = random_string()
        client_metadata: Dict = {
            **TEST_METADATA,
            'client_description': client_description,
        }

        oauth_client = create_oauth2_client(client_metadata, user_1)

        assert oauth_client.client_description == client_description

    def test_oauth_client_has_expected_client_uri(
        self, app: Flask, user_1: User
    ) -> None:
        client_uri = random_domain()
        client_metadata: Dict = {**TEST_METADATA, 'client_uri': client_uri}

        oauth_client = create_oauth2_client(client_metadata, user_1)

        assert oauth_client.client_uri == client_uri

    def test_oauth_client_has_expected_grant_types(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.grant_types == [
            'authorization_code',
            'refresh_token',
        ]

    def test_oauth_client_has_expected_redirect_uris(
        self, app: Flask, user_1: User
    ) -> None:
        redirect_uris = [random_domain()]
        client_metadata: Dict = {
            **TEST_METADATA,
            'redirect_uris': redirect_uris,
        }

        oauth_client = create_oauth2_client(client_metadata, user_1)

        assert oauth_client.redirect_uris == redirect_uris

    def test_oauth_client_has_expected_response_types(
        self, app: Flask, user_1: User
    ) -> None:
        response_types = ['code']
        client_metadata: Dict = {
            **TEST_METADATA,
            'response_types': response_types,
        }

        oauth_client = create_oauth2_client(client_metadata, user_1)

        assert oauth_client.response_types == ['code']

    def test_oauth_client_has_expected_scope(
        self, app: Flask, user_1: User
    ) -> None:
        scope = 'workouts:write'
        client_metadata: Dict = {**TEST_METADATA, 'scope': scope}

        oauth_client = create_oauth2_client(client_metadata, user_1)

        assert oauth_client.scope == scope

    def test_it_raises_error_when_scope_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client_metadata: Dict = {**TEST_METADATA, 'scope': random_string()}

        with pytest.raises(InvalidOAuth2Scopes):
            create_oauth2_client(client_metadata, user_1)

    def test_oauth_client_has_expected_token_endpoint_auth_method(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.token_endpoint_auth_method == 'client_secret_post'

    def test_when_auth_method_is_not_none_oauth_client_secret_is_generated(
        self, app: Flask, user_1: User
    ) -> None:
        client_secret = random_string()
        with patch(
            'fittrackee.oauth2.client.gen_salt', return_value=client_secret
        ):
            oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.client_secret == client_secret

    def test_it_creates_oauth_client_for_given_user(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = create_oauth2_client(TEST_METADATA, user_1)

        assert oauth_client.user_id == user_1.id


class TestOAuthCheckScopes:
    @pytest.mark.parametrize(
        'input_scope', ['', 1, 'invalid_scope', ['invalid_scope', 'readwrite']]
    )
    def test_it_raises_error_when_scope_is_invalid(
        self, input_scope: Any
    ) -> None:
        with pytest.raises(InvalidOAuth2Scopes):
            check_scope(input_scope)

    @pytest.mark.parametrize(
        'input_scope,expected_scope',
        [
            ('profile:read', 'profile:read'),
            ('profile:read invalid_scope:read', 'profile:read'),
            ('profile:write', 'profile:write'),
            ('profile:read profile:write', 'profile:read profile:write'),
            (
                'profile:write invalid_scope:read profile:read',
                'profile:write profile:read',
            ),
        ],
    )
    def test_it_return_only_valid_scopes(
        self, input_scope: str, expected_scope: str
    ) -> None:
        assert check_scope(input_scope) == expected_scope

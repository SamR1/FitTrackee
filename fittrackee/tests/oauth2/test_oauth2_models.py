import time
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.oauth2.models import OAuth2Client, OAuth2Token
from fittrackee.users.models import User

from ..mixins import OAuth2Mixin


class TestOAuth2ClientSerialize(OAuth2Mixin):
    def test_it_returns_oauth_client(self, app: Flask, user_1: User) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        oauth_client.client_id_issued_at = 1653738796

        serialized_oauth_client = oauth_client.serialize()

        assert serialized_oauth_client["client_id"] == oauth_client.client_id
        assert (
            serialized_oauth_client["client_description"]
            == oauth_client.client_description
        )
        assert "client_secret" not in serialized_oauth_client
        assert (
            serialized_oauth_client["issued_at"]
            == "Sat, 28 May 2022 11:53:16 GMT"
        )
        assert serialized_oauth_client["id"] == oauth_client.id
        assert serialized_oauth_client["name"] == oauth_client.client_name
        assert (
            serialized_oauth_client["redirect_uris"]
            == oauth_client.redirect_uris
        )
        assert serialized_oauth_client["scope"] == oauth_client.scope
        assert serialized_oauth_client["website"] == oauth_client.client_uri

    def test_it_returns_oauth_client_with_client_secret(
        self, app: Flask
    ) -> None:
        oauth_client = OAuth2Client(
            id=self.random_int(),
            client_id=self.random_string(),
            client_id_issued_at=self.random_int(),
        )
        oauth_client.set_client_metadata(
            {
                "client_name": self.random_string(),
                "redirect_uris": [self.random_string()],
                "client_uri": self.random_domain(),
            }
        )

        serialized_oauth_client = oauth_client.serialize(with_secret=True)

        assert (
            serialized_oauth_client["client_secret"]
            == oauth_client.client_secret
        )


class TestOAuth2Token(OAuth2Mixin):
    @pytest.mark.parametrize(
        "input_expiration,expected_status", [(1000, True), (0, False)]
    )
    def test_it_returns_refresh_token_status(
        self,
        app: Flask,
        user_1: User,
        input_expiration: int,
        expected_status: bool,
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        token = OAuth2Token(
            client_id=oauth_client.client_id,
            access_token=self.random_string(),
            refresh_token=self.random_string(),
            issued_at=int(time.time()),
            expires_in=input_expiration,
        )

        assert token.is_refresh_token_active() is expected_status

    def test_it_returns_refresh_token_active_when_below_twice_expiration(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        issued_at = int(time.time())
        expires_in = self.random_int()
        token = OAuth2Token(
            client_id=oauth_client.client_id,
            access_token=self.random_string(),
            refresh_token=self.random_string(),
            issued_at=int(time.time()),
            expires_in=expires_in,
        )

        with patch(
            "fittrackee.oauth2.models.time.time",
            return_value=(issued_at + expires_in * 2 - 1),
        ):
            assert token.is_refresh_token_active() is True

    def test_it_returns_refresh_token_inactive_when_token_revoked(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        token = OAuth2Token(
            client_id=oauth_client.client_id,
            access_token=self.random_string(),
            refresh_token=self.random_string(),
            issued_at=int(time.time()),
            access_token_revoked_at=int(time.time()),
            expires_in=1000,
        )

        assert token.is_refresh_token_active() is False

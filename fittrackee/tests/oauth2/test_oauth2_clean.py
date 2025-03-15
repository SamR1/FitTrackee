import time

from flask import Flask

from fittrackee.oauth2.clean import clean_tokens
from fittrackee.oauth2.models import OAuth2Token
from fittrackee.users.models import User

from ..mixins import OAuth2Mixin


class TestOAuth2CleanTokens(OAuth2Mixin):
    def test_it_does_not_delete_not_expired_token(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        self.create_oauth2_token(oauth_client)

        clean_tokens(days=1)

        assert OAuth2Token.query.count() == 1

    def test_it_deletes_expired_token(self, app: Flask, user_1: User) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        expires_in = 864000  # 10 days
        days = 5
        self.create_oauth2_token(
            oauth_client,
            issued_at=int(time.time()) - expires_in - (days * 86400) - 1,
            expires_in=expires_in,
        )

        clean_tokens(days=days)

        assert OAuth2Token.query.count() == 0

    def test_it_returns_deleted_rows_count(
        self, app: Flask, user_1: User
    ) -> None:
        oauth_client = self.create_oauth2_client(user_1)
        expires_in = 86400  # 10 days
        days = 5
        expected_deleted_rows = 3
        for _ in range(expected_deleted_rows):
            self.create_oauth2_token(
                oauth_client,
                issued_at=(int(time.time()) - expires_in - (days * 86400) - 1),
                expires_in=expires_in,
            )
        self.create_oauth2_token(oauth_client)
        self.create_oauth2_token(
            oauth_client,
            issued_at=(int(time.time()) - expires_in - (days * 86400) + 2),
            expires_in=expires_in,
        )

        result = clean_tokens(days=days)

        assert result == expected_deleted_rows

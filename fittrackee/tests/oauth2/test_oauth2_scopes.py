import pytest
from flask import Flask

from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin


class TestOAuth2Scopes(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        "endpoint_url,scope",
        [
            ("/api/auth/profile", "profile:read"),
            ("/api/workouts", "workouts:read"),
        ],
    )
    def test_oauth_client_can_access_authorized_endpoints(
        self, app: Flask, user_1: User, endpoint_url: str, scope: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(app, user_1, scope=scope)

        response = client.get(
            endpoint_url,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_not_insufficient_scope_error(response)

    @pytest.mark.parametrize(
        "endpoint_url,scope",
        [
            ("/api/auth/profile", "workouts:read"),
            ("/api/workouts", "profile:read"),
        ],
    )
    def test_oauth_client_can_not_access_unauthorized_endpoints(
        self, app: Flask, user_1: User, endpoint_url: str, scope: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(app, user_1, scope=scope)

        response = client.get(
            endpoint_url,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_insufficient_scope(response)

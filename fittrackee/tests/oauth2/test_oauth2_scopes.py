from typing import TYPE_CHECKING

import pytest

from ..custom_asserts import (
    assert_oauth_errored_response,
)
from ..mixins import ApiTestCaseMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestOAuth2Scopes(ApiTestCaseMixin):
    endpoint = "/api/config"
    valid_scope = "application:write"

    @pytest.mark.parametrize(
        "input_scope",
        [
            "equipments:read",
            "equipments:write",
            "follow:read",
            "follow:write",
            "geocode:read",
            "notifications:read",
            "notifications:write",
            "profile:read",
            "profile:write",
            "reports:read",
            "reports:write",
            "users:read",
            "users:write",
            "workouts:read",
            "workouts:write",
        ],
    )
    def test_it_returns_403_with_insufficient_scope_when_scope_is_invalid(
        self, app: "Flask", user_1_admin: "User", input_scope: str
    ) -> None:
        (
            client,
            _,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=input_scope
        )

        response = client.patch(
            self.endpoint,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        assert_oauth_errored_response(
            response,
            403,
            error="insufficient_scope",
            error_description=(
                "The request requires higher privileges than provided by "
                "the access token."
            ),
        )

    def test_it_does_not_return_403_when_scope_is_invalid(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        (
            client,
            _,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=self.valid_scope
        )

        response = client.patch(
            self.endpoint,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        assert response.status_code != 403

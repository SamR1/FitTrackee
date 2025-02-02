import json
from datetime import datetime, timezone
from typing import Optional

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.application.models import AppConfig
from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestGetConfig(ApiTestCaseMixin):
    def test_it_gets_application_config_for_unauthenticated_user(
        self, app: Flask
    ) -> None:
        config = AppConfig.query.one()
        client = app.test_client()

        response = client.get("/api/config")

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == jsonify_dict(config.serialize())

    def test_it_gets_application_config(
        self, app: Flask, user_1: User
    ) -> None:
        config = AppConfig.query.one()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/config",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == jsonify_dict(config.serialize())

    def test_it_gets_application_config_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        config = AppConfig.query.one()
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            "/api/config",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == jsonify_dict(config.serialize())

    def test_it_returns_error_if_application_has_no_config(
        self, app_no_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_no_config, user_1_admin.email
        )

        response = client.get(
            "/api/config",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "error on getting configuration")

    def test_it_returns_error_if_application_has_several_config(
        self, app: Flask, app_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            "/api/config",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "error on getting configuration")


class TestUpdateConfig(ApiTestCaseMixin):
    def test_it_updates_config_when_user_is_admin(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["gpx_limit_import"] == 100
        assert data["data"]["is_registration_enabled"] is True
        assert data["data"]["max_single_file_size"] == 1048576
        assert data["data"]["max_zip_file_size"] == 10485760
        assert data["data"]["max_users"] == 10

    def test_it_updates_all_config(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        admin_email = self.random_email()

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    admin_contact=admin_email,
                    gpx_limit_import=20,
                    max_single_file_size=10000,
                    max_zip_file_size=25000,
                    max_users=50,
                    stats_workouts_limit=5000,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["admin_contact"] == admin_email
        assert data["data"]["gpx_limit_import"] == 20
        assert data["data"]["is_registration_enabled"] is True
        assert data["data"]["max_single_file_size"] == 10000
        assert data["data"]["max_zip_file_size"] == 25000
        assert data["data"]["max_users"] == 50
        assert data["data"]["stats_workouts_limit"] == 5000

    def test_it_returns_403_when_user_is_not_an_admin(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_400_if_invalid_is_payload(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_error_on_update_if_application_has_no_config(
        self, app_no_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_no_config, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "error when updating configuration")

    def test_it_raises_error_if_archive_max_size_is_below_files_max_size(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    gpx_limit_import=20,
                    max_single_file_size=10000,
                    max_zip_file_size=1000,
                    max_users=50,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            (
                "max size of zip archive must be equal or greater than max "
                "size of uploaded files"
            ),
        )

    def test_it_raises_error_if_archive_max_size_equals_0(
        self, app_with_max_file_size_equals_0: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size_equals_0, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    max_zip_file_size=0,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "max size of zip archive must be greater than 0"
        )

    def test_it_raises_error_if_files_max_size_equals_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    max_single_file_size=0,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "max size of uploaded files must be greater than 0"
        )

    def test_it_raises_error_if_gpx_limit_import_equals_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    gpx_limit_import=0,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "max files in a zip archive must be greater than 0"
        )

    def test_it_raises_error_when_max_users_below_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            json={"max_users": -1},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "max users must be greater than or equal to 0"
        )

    def test_it_raises_error_when_stats_workouts_limit_below_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            json={"stats_workouts_limit": -1},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            (
                "max number of workouts for statistics must be "
                "greater than or equal to 0"
            ),
        )

    def test_it_raises_error_if_admin_contact_is_invalid(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    admin_contact=self.random_string(),
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "valid email must be provided for admin contact"
        )

    @pytest.mark.parametrize(
        "input_description,input_email", [("input string", ""), ("None", None)]
    )
    def test_it_empties_administrator_contact(
        self,
        app: Flask,
        user_1_admin: User,
        input_description: str,
        input_email: Optional[str],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        config = AppConfig.query.one()
        config.admin_contact = self.random_email()

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    admin_contact=input_email,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["admin_contact"] is None

    def test_it_updates_about(
        self,
        app: Flask,
        user_1_admin: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        about = self.random_string()

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(about=about)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["about"] == about

    def test_it_empties_about_text_when_text_is_an_empty_string(
        self, app: Flask, user_1_admin: User
    ) -> None:
        config = AppConfig.query.one()
        config.about = self.random_string()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(about="")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["about"] is None

    def test_it_updates_privacy_policy(
        self,
        app: Flask,
        user_1_admin: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        privacy_policy = self.random_string()
        privacy_policy_date = datetime.now(timezone.utc)

        with travel(privacy_policy_date, tick=False):
            response = client.patch(
                "/api/config",
                content_type="application/json",
                data=json.dumps(dict(privacy_policy=privacy_policy)),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["privacy_policy"] == privacy_policy
        assert data["data"][
            "privacy_policy_date"
        ] == privacy_policy_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    @pytest.mark.parametrize("input_privacy_policy", ["", None])
    def test_it_return_default_privacy_policy_date_when_no_privacy_policy(
        self,
        app: Flask,
        user_1_admin: User,
        input_privacy_policy: Optional[str],
    ) -> None:
        config = AppConfig.query.one()
        config.privacy_policy = self.random_string()
        config.privacy_policy_date = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(privacy_policy=input_privacy_policy)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["privacy_policy"] is None
        assert (
            data["data"]["privacy_policy_date"]
            == app.config["DEFAULT_PRIVACY_POLICY_DATA"]
        )

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "application:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)

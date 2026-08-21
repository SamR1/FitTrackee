import json
import os
from datetime import datetime, timezone
from typing import Optional

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.application.app_config import MAX_GLOBAL_MAP_WORKOUTS
from fittrackee.application.models import AppConfig
from fittrackee.constants import DEFAULT_TILE_PROVIDER
from fittrackee.database import PSQL_INTEGER_LIMIT
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


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
            data=json.dumps(dict(file_limit_import=100, max_users=10)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["file_sync_limit_import"] == 10
        assert data["data"]["file_limit_import"] == 100
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
                    file_limit_import=200,
                    file_sync_limit_import=20,
                    global_map_workouts_limit=7000,
                    max_image_size=20000,
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
        assert data["data"]["elevation_services"] == {
            "open_elevation": False,
            "valhalla": False,
        }
        assert data["data"]["file_limit_import"] == 200
        assert data["data"]["file_sync_limit_import"] == 20
        assert data["data"]["global_map_workouts_limit"] == 7000
        assert data["data"]["is_registration_enabled"] is True
        assert data["data"]["max_image_size"] == 20000
        assert data["data"]["max_single_file_size"] == 10000
        assert data["data"]["max_zip_file_size"] == 25000
        assert data["data"]["max_users"] == 50
        assert data["data"]["stats_workouts_limit"] == 5000

    def test_it_refreshes_config_after_update(
        self,
        app_with_max_workouts: Flask,  # 2 workouts max in archive
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_workouts, user_1_admin.email
        )

        client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(
                    file_sync_limit_import=3,
                    file_limit_import=5,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        file_path = os.path.join(
            app_with_max_workouts.root_path, "tests/files/gpx_test.zip"
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, "rb") as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_workouts, user_2.email
            )

            response = client.post(
                "/api/workouts",
                data=dict(
                    file=(zip_file, "gpx_test.zip"), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

            assert response.status_code == 201
            data = json.loads(response.data.decode())
            assert len(data["data"]["workouts"]) == 3

    def test_it_returns_403_when_user_is_not_an_admin(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(dict(file_limit_import=100, max_users=10)),
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
            data=json.dumps(dict(file_limit_import=100, max_users=10)),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "error when updating configuration")

    @pytest.mark.parametrize(
        "input_param",
        [
            "file_sync_limit_import",
            "file_limit_import",
            "max_image_size",
            "max_zip_file_size",
            "max_users",
            "stats_workouts_limit",
        ],
    )
    def test_it_raises_error_if_given_param_exceeds_limit(
        self, app: Flask, user_1_admin: User, input_param: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            json={input_param: 2147483648},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            f"'{input_param}' must be less than 2147483648",
            "config_value_exceeding_limit",
        )

    def test_it_raises_error_if_max_single_file_size_exceeds_limit(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            json={
                "max_single_file_size": 2147483648,
                "max_zip_file_size": 2147483648,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            "'max_single_file_size' must be less than 2147483648",
            "config_value_exceeding_limit",
        )

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
                    file_limit_import=20,
                    max_single_file_size=10000,
                    max_zip_file_size=1000,
                    max_users=PSQL_INTEGER_LIMIT,
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

    def test_it_raises_error_if_file_limit_import_equals_0(
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
                    file_limit_import=0,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "max files in a zip archive must be greater than 0"
        )

    def test_it_raises_error_if_file_sync_limit_import_equals_0(
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
                    file_sync_limit_import=0,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            "max files in a zip archive processed synchronously "
            "must be greater than 0",
        )

    def test_it_raises_error_if_file_sync_limit_exceeds_file_limit_import(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            data=json.dumps(
                dict(file_sync_limit_import=20, file_limit_import=10)
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            "max files in a zip archive must be equal or greater than "
            "max files in a zip archive processed synchronously",
        )

    def test_it_raises_error_if_max_image_size_equals_0(
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
                    max_image_size=0,
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "max size of images must be greater than 0")

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

    def test_it_raises_error_if_global_map_workouts_limit_exceeds_limit(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            "/api/config",
            content_type="application/json",
            json={
                "global_map_workouts_limit": MAX_GLOBAL_MAP_WORKOUTS + 1,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            (
                f"'global_map_workouts_limit' must be less "
                f"than {MAX_GLOBAL_MAP_WORKOUTS}"
            ),
        )

    def test_expected_scope_is_application_write(
        self, app: Flask, user_1_admin: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1_admin,
            client_method="patch",
            endpoint="/api/config",
            invalid_scope="workouts:read",
            expected_endpoint_scope="application:write",
        )


class TestGetTileProviders(ApiTestCaseMixin):
    route = "/api/tile-providers"

    def test_it_returns_available_tile_providers_when_user_is_not_authenticated(  # noqa
        self, app: "Flask"
    ) -> None:
        client = app.test_client()
        expected_tile_provider = app.config["TILE_PROVIDERS"][
            DEFAULT_TILE_PROVIDER
        ]

        response = client.get(self.route)

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "tile_providers": [
                {
                    "id": "osm",
                    "default": True,
                    "default_for_user": True,
                    "enabled": True,
                    "name": expected_tile_provider.name,
                    "attribution": expected_tile_provider.attribution,
                },
            ]
        }

    def test_it_returns_available_tile_providers_when_user_has_no_admin_rights(
        self,
        app_with_multiple_tile_servers_enabled: "Flask",
        user_1_moderator: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_multiple_tile_servers_enabled, user_1_moderator.email
        )
        tile_providers = app_with_multiple_tile_servers_enabled.config[
            "TILE_PROVIDERS"
        ]

        response = client.get(
            self.route,
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "tile_providers": [
                {
                    "default": False,
                    "default_for_user": True,
                    "id": "osm",
                    "enabled": True,
                    "name": tile_providers["osm"].name,
                    "attribution": tile_providers["osm"].attribution,
                },
                {
                    "default": False,
                    "default_for_user": False,
                    "enabled": True,
                    "id": "osm_fr",
                    "name": tile_providers["osm_fr"].name,
                    "attribution": tile_providers["osm_fr"].attribution,
                },
                {
                    "default": True,
                    "default_for_user": False,
                    "enabled": True,
                    "id": "cyclosm",
                    "name": tile_providers["cyclosm"].name,
                    "attribution": tile_providers["cyclosm"].attribution,
                },
            ]
        }

    def test_it_returns_available_tile_providers_when_user_has_admin_rights(
        self, app_default_static_map: "Flask", user_1_admin: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_default_static_map, user_1_admin.email
        )
        tile_providers = app_default_static_map.config["TILE_PROVIDERS"]

        response = client.get(
            self.route,
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"] == {
            "tile_providers": [
                {
                    "api_key_is_missing": False,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "osm",
                    "attribution": tile_providers["osm"].attribution,
                    "name": tile_providers["osm"].name,
                    "set_by_users": True,
                },
                {
                    "api_key_is_missing": False,
                    "default": True,
                    "default_for_user": True,
                    "enabled": True,
                    "id": "osm_de",
                    "attribution": tile_providers["osm_de"].attribution,
                    "name": tile_providers["osm_de"].name,
                    "set_by_users": False,
                },
                {
                    "api_key_is_missing": False,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "osm_fr",
                    "attribution": tile_providers["osm_fr"].attribution,
                    "name": tile_providers["osm_fr"].name,
                    "set_by_users": False,
                },
                {
                    "api_key_is_missing": False,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "cyclosm",
                    "attribution": tile_providers["cyclosm"].attribution,
                    "name": tile_providers["cyclosm"].name,
                    "set_by_users": False,
                },
                {
                    "api_key_is_missing": True,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "stadiamaps_alidade_smooth",
                    "attribution": tile_providers[
                        "stadiamaps_alidade_smooth"
                    ].attribution,
                    "name": tile_providers["stadiamaps_alidade_smooth"].name,
                    "set_by_users": False,
                },
                {
                    "api_key_is_missing": True,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "stadiamaps_outdoors",
                    "attribution": tile_providers[
                        "stadiamaps_outdoors"
                    ].attribution,
                    "name": tile_providers["stadiamaps_outdoors"].name,
                    "set_by_users": False,
                },
                {
                    "api_key_is_missing": True,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "thunderforest_landscape",
                    "attribution": tile_providers[
                        "thunderforest_landscape"
                    ].attribution,
                    "name": tile_providers["thunderforest_landscape"].name,
                    "set_by_users": False,
                },
                {
                    "api_key_is_missing": True,
                    "default": False,
                    "default_for_user": False,
                    "enabled": False,
                    "id": "thunderforest_outdoors",
                    "attribution": tile_providers[
                        "thunderforest_outdoors"
                    ].attribution,
                    "name": tile_providers["thunderforest_outdoors"].name,
                    "set_by_users": False,
                },
            ]
        }

    def test_expected_scope_is_application_read(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint=self.route,
            invalid_scope="application:write",
            expected_endpoint_scope="application:read",
        )


class TestUpdateTileProvider(ApiTestCaseMixin):
    route = "/api/tile-providers/{tile_provider}"

    @staticmethod
    def assert_default_provider_is_osm() -> None:
        config = AppConfig.query.one()
        assert config.tile_providers == [DEFAULT_TILE_PROVIDER]
        assert config.default_tile_provider == DEFAULT_TILE_PROVIDER

    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.patch(
            self.route.format(tile_provider="osm"),
            json={},
        )

        self.assert_401(response)

    def test_it_returns_403_when_user_has_no_admin_rights(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(tile_provider="osm"),
            content_type="application/json",
            json={},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_when_tile_provider_is_invalid(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(tile_provider="invalid"),
            content_type="application/json",
            json={},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, "tile provider 'invalid' does not exist"
        )

    def test_it_returns_400_when_payload_is_empty(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            self.route.format(tile_provider="osm"),
            content_type="application/json",
            json={},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_400_when_payload_is_invalid(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        provider_key = "osm"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": True, "enabled": False},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            error_message=(
                "default tile provider cannot be disabled, please set another "
                "provider as default first"
            ),
        )
        self.assert_default_provider_is_osm()

    def test_it_enables_tile_provider(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        """
        'osm' is the default provider
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        provider_key = "osm_fr"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": True},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        config = AppConfig.query.one()
        assert set(config.tile_providers) == {"osm", "osm_fr"}
        assert config.default_tile_provider == "osm"

    def test_it_enables_and_set_tile_provider_as_default(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        """
        'osm' is the default provider
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        provider_key = "osm_fr"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": True, "enabled": True},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        config = AppConfig.query.one()
        assert set(config.tile_providers) == {"osm", "osm_fr"}
        assert config.default_tile_provider == "osm_fr"

    def test_it_disabled_tile_provider(
        self,
        app_with_multiple_tile_servers_enabled: "Flask",
        user_1_admin: "User",
    ) -> None:
        """
        set tile providers: 'osm', 'osm_fr' and 'cyclosm'
        'cyclosm' is the default provider
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_multiple_tile_servers_enabled, user_1_admin.email
        )
        provider_key = "osm"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": False},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        config = AppConfig.query.one()
        assert set(config.tile_providers) == {"osm_fr", "cyclosm"}
        assert config.default_tile_provider == "cyclosm"

    def test_it_disabled_default_tile_provider_set_as_default(
        self,
        app_with_multiple_tile_servers_enabled: "Flask",
        user_1_admin: "User",
    ) -> None:
        """
        set tile providers: 'osm', 'osm_fr' and 'cyclosm'
        'cyclosm' is the default provider
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_multiple_tile_servers_enabled, user_1_admin.email
        )
        provider_key = "cyclosm"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": False},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        config = AppConfig.query.one()
        assert set(config.tile_providers) == {"osm", "osm_fr"}
        assert config.default_tile_provider == "osm"

    def test_it_disabled_default_tile_provider(
        self,
        app: "Flask",
        user_1_admin: "User",
    ) -> None:
        app_config = AppConfig.query.one()
        app_config.tile_providers = ["osm", "osm_fr"]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        provider_key = "osm_fr"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": False},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        config = AppConfig.query.one()
        assert set(config.tile_providers) == {"osm"}
        assert config.default_tile_provider == "osm"

    def test_it_set_default_as_false(
        self,
        app_with_multiple_tile_servers_enabled: "Flask",
        user_1_admin: "User",
    ) -> None:
        """
        set tile providers: 'osm', 'osm_fr' and 'cyclosm'
        'cyclosm' is the default provider
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_multiple_tile_servers_enabled, user_1_admin.email
        )
        provider_key = "cyclosm"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": True},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        config = AppConfig.query.one()
        assert set(config.tile_providers) == {"osm", "osm_fr", provider_key}
        assert config.default_tile_provider == "osm"

    def test_it_can_not_set_osm_default_as_false_when_it_is_the_only_tile_provider(  # noqa
        self,
        app: "Flask",
        user_1_admin: "User",
    ) -> None:
        """
        'osm' is the only only one provider
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        provider_key = "osm"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": True},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            error_message=(
                "tile provided 'osm' can not be disabled when it is "
                "the only tile provider"
            ),
        )
        self.assert_default_provider_is_osm()

    def test_it_disables_custom_tile_provider_when_it_is_the_only_provided_set(
        self,
        app_with_custom_tile_server: "Flask",
        user_1_admin: "User",
    ) -> None:
        """
        custom tile server set before FitTrackee 1.4.0
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_custom_tile_server, user_1_admin.email
        )
        provider_key = "custom"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": False},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_response_is_success(response)
        self.assert_default_provider_is_osm()

    def test_it_returns_400_when_api_key_is_missing(
        self,
        app: "Flask",
        user_1_admin: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        provider_key = "thunderforest_outdoors"

        response = client.patch(
            self.route.format(tile_provider=provider_key),
            content_type="application/json",
            json={"default": False, "enabled": True},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            error_message=(
                "no api key is not set for this tile provider, please update "
                "application config first"
            ),
        )
        self.assert_default_provider_is_osm()

    def test_expected_scope_is_application_write(
        self, app: Flask, user_1_admin: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1_admin,
            client_method="patch",
            endpoint="/api/config",
            invalid_scope="workouts:read",
            expected_endpoint_scope="application:write",
        )

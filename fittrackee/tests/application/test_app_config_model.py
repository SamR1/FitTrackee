from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest

from fittrackee import DEFAULT_PRIVACY_POLICY_DATA, VERSION
from fittrackee.application.models import AppConfig

from ..utils import random_int, random_string

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestAppConfigModel:
    def test_application_config_properties_with_default_values(
        self,
        app: "Flask",
        monkeypatch: "pytest.MonkeyPatch",
    ) -> None:
        config = AppConfig.query.one()

        # registration
        assert config.is_registration_enabled is True
        # elevation services
        assert config.elevation_services == {
            "open_elevation": False,
            "valhalla": False,
        }
        # tile providers
        assert config.tile_providers == ["osm"]
        assert config.available_tile_providers == {
            "osm": app.config["TILE_PROVIDERS"]["osm"]
        }
        assert config.default_tile_provider == "osm"

    def test_it_returns_serialized_application_config(
        self, app: "Flask", monkeypatch: "pytest.MonkeyPatch"
    ) -> None:
        monkeypatch.setenv("WEATHER_API_PROVIDER", "visualcrossing")
        config = AppConfig.query.one()
        config.admin_contact = "admin@example.com"

        serialized_app_config = config.serialize()

        assert serialized_app_config == {
            "about": None,
            "admin_contact": config.admin_contact,
            "elevation_services": config.elevation_services,
            "enable_heatmap": False,
            "file_limit_import": config.file_limit_import,
            "file_sync_limit_import": config.file_sync_limit_import,
            "is_email_sending_enabled": True,
            "is_registration_enabled": True,
            "global_map_workouts_limit": 10000,
            "max_image_size": config.max_image_size,
            "max_single_file_size": config.max_single_file_size,
            "max_zip_file_size": config.max_zip_file_size,
            "max_users": config.max_users,
            "privacy_policy": None,
            "privacy_policy_date": app.config["DEFAULT_PRIVACY_POLICY_DATA"],
            "stats_workouts_limit": config.stats_workouts_limit,
            "version": VERSION,
            "weather_provider": "visualcrossing",
        }

    def test_it_returns_enable_heatmap_when_env_var_is_true(
        self, app_with_enabled_heatmap: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["enable_heatmap"] is True

    def test_it_returns_registration_disabled_when_users_count_exceeds_limit(
        self, app: "Flask", user_1: "User", user_2: "User"
    ) -> None:
        config = AppConfig.query.one()
        config.max_users = 2
        serialized_app_config = config.serialize()

        assert config.is_registration_enabled is False
        assert serialized_app_config["is_registration_enabled"] is False

    def test_it_returns_email_sending_disabled_when_no_email_url_provided(
        self, app_wo_email_activation: "Flask", user_1: "User", user_2: "User"
    ) -> None:
        config = AppConfig.query.one()
        serialized_app_config = config.serialize()

        assert serialized_app_config["is_email_sending_enabled"] is False

    @pytest.mark.parametrize(
        "input_weather_api_provider, expected_weather_provider",
        [
            ("darksky", None),  # removed provider
            ("Visualcrossing", "visualcrossing"),
            ("invalid_provider", None),
            ("", None),
        ],
    )
    def test_it_returns_weather_provider(
        self,
        app: "Flask",
        input_weather_api_provider: str,
        expected_weather_provider: str,
        monkeypatch: "pytest.MonkeyPatch",
    ) -> None:
        monkeypatch.setenv("WEATHER_API_PROVIDER", input_weather_api_provider)
        config = AppConfig.query.one()
        serialized_app_config = config.serialize()

        assert (
            serialized_app_config["weather_provider"]
            == expected_weather_provider
        )

    def test_it_returns_only_privacy_policy_date_when_no_custom_privacy(
        self, app: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["privacy_policy"] is None
        assert (
            serialized_app_config["privacy_policy_date"]
            == DEFAULT_PRIVACY_POLICY_DATA
        )

    def test_it_returns_custom_privacy_policy(self, app: "Flask") -> None:
        config = AppConfig.query.one()
        privacy_policy = random_string()
        privacy_policy_date = datetime.now(timezone.utc)
        config.privacy_policy = privacy_policy
        config.privacy_policy_date = privacy_policy_date

        serialized_app_config = config.serialize()

        assert serialized_app_config["privacy_policy"] == privacy_policy
        assert (
            serialized_app_config["privacy_policy_date"] == privacy_policy_date
        )

    def test_it_returns_about(self, app: "Flask") -> None:
        config = AppConfig.query.one()
        about = random_string()
        config.about = about

        serialized_app_config = config.serialize()

        assert serialized_app_config["about"] == about

    def test_it_returns_stats_workouts_limit(self, app: "Flask") -> None:
        config = AppConfig.query.one()
        stats_workouts_limit = random_int()
        config.stats_workouts_limit = stats_workouts_limit

        serialized_app_config = config.serialize()

        assert (
            serialized_app_config["stats_workouts_limit"]
            == stats_workouts_limit
        )

    def test_it_returns_global_map_workouts_limit(self, app: "Flask") -> None:
        config = AppConfig.query.one()
        global_map_workouts_limit = random_int()
        config.global_map_workouts_limit = global_map_workouts_limit

        serialized_app_config = config.serialize()

        assert (
            serialized_app_config["global_map_workouts_limit"]
            == global_map_workouts_limit
        )

    def test_it_returns_elevation_services_when_open_elevation_is_disabled(
        self, app: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["elevation_services"] == {
            "open_elevation": False,
            "valhalla": False,
        }

    def test_it_returns_elevation_services_when_open_elevation_is_enabled(
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["elevation_services"] == {
            "open_elevation": True,
            "valhalla": False,
        }

    def test_it_returns_elevation_services_when_valhalla_is_enabled(
        self, app_with_valhalla_url: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["elevation_services"] == {
            "open_elevation": False,
            "valhalla": True,
        }

    def test_it_returns_elevation_services_when_valhalla_and_open_elevation_are_enabled(  # noqa
        self, app_with_open_elevation_and_valhalla_url: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["elevation_services"] == {
            "open_elevation": True,
            "valhalla": True,
        }

    def test_it_returns_elevation_services_when_valhalla_and_open_elevation_urls_are_empty_string(  # noqa
        self, app_with_empty_string_as_open_elevation_and_valhalla_url: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["elevation_services"] == {
            "open_elevation": False,
            "valhalla": False,
        }

    def test_it_returns_tiles_providers_when_multiple_providers_are_set(
        self, app_with_multiple_tile_servers_enabled: "Flask"
    ) -> None:
        config = AppConfig.query.one()

        assert config.tile_providers == ["osm", "osm_fr", "cyclosm"]
        assert config.available_tile_providers == {
            "osm": app_with_multiple_tile_servers_enabled.config[
                "TILE_PROVIDERS"
            ]["osm"],
            "osm_fr": app_with_multiple_tile_servers_enabled.config[
                "TILE_PROVIDERS"
            ]["osm_fr"],
            "cyclosm": app_with_multiple_tile_servers_enabled.config[
                "TILE_PROVIDERS"
            ]["cyclosm"],
        }
        assert config.default_tile_provider == "cyclosm"

    def test_it_returns_only_tiles_providers_without_missing_api_key(
        self, app_with_missing_tile_provider_api_key: "Flask"
    ) -> None:
        """
        api key is missing for Thunderforest Outdoor tile server
        """
        config = AppConfig.query.one()

        assert config.tile_providers == [
            "osm",
            "cyclosm",
            "thunderforest_outdoors",
        ]
        assert config.available_tile_providers == {
            "osm": app_with_missing_tile_provider_api_key.config[
                "TILE_PROVIDERS"
            ]["osm"],
            "cyclosm": app_with_missing_tile_provider_api_key.config[
                "TILE_PROVIDERS"
            ]["cyclosm"],
        }
        assert config.default_tile_provider == "cyclosm"

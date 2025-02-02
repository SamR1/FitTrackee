from datetime import datetime, timezone

import pytest
from flask import Flask

from fittrackee import DEFAULT_PRIVACY_POLICY_DATA, VERSION
from fittrackee.application.models import AppConfig
from fittrackee.users.models import User

from ..utils import random_int, random_string


class TestConfigModel:
    def test_application_config(
        self, app: Flask, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("WEATHER_API_PROVIDER", "visualcrossing")
        config = AppConfig.query.one()
        config.admin_contact = "admin@example.com"

        assert config.is_registration_enabled is True
        assert (
            config.map_attribution == app.config["TILE_SERVER"]["ATTRIBUTION"]
        )

        serialized_app_config = config.serialize()
        assert serialized_app_config["admin_contact"] == config.admin_contact
        assert (
            serialized_app_config["gpx_limit_import"]
            == config.gpx_limit_import
        )
        assert serialized_app_config["is_email_sending_enabled"] is True
        assert serialized_app_config["is_registration_enabled"] is True
        assert (
            serialized_app_config["max_single_file_size"]
            == config.max_single_file_size
        )
        assert (
            serialized_app_config["max_zip_file_size"]
            == config.max_zip_file_size
        )
        assert serialized_app_config["max_users"] == config.max_users
        assert (
            serialized_app_config["map_attribution"] == config.map_attribution
        )
        assert serialized_app_config["version"] == VERSION
        assert serialized_app_config["weather_provider"] == "visualcrossing"

    def test_it_returns_registration_disabled_when_users_count_exceeds_limit(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        config = AppConfig.query.one()
        config.max_users = 2
        serialized_app_config = config.serialize()

        assert config.is_registration_enabled is False
        assert serialized_app_config["is_registration_enabled"] is False

    def test_it_returns_email_sending_disabled_when_no_email_url_provided(
        self, app_wo_email_activation: Flask, user_1: User, user_2: User
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
        app: Flask,
        input_weather_api_provider: str,
        expected_weather_provider: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("WEATHER_API_PROVIDER", input_weather_api_provider)
        config = AppConfig.query.one()
        serialized_app_config = config.serialize()

        assert (
            serialized_app_config["weather_provider"]
            == expected_weather_provider
        )

    def test_it_returns_only_privacy_policy_date_when_no_custom_privacy(
        self, app: Flask
    ) -> None:
        config = AppConfig.query.one()

        serialized_app_config = config.serialize()

        assert serialized_app_config["privacy_policy"] is None
        assert (
            serialized_app_config["privacy_policy_date"]
            == DEFAULT_PRIVACY_POLICY_DATA
        )

    def test_it_returns_custom_privacy_policy(self, app: Flask) -> None:
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

    def test_it_returns_about(self, app: Flask) -> None:
        config = AppConfig.query.one()
        about = random_string()
        config.about = about

        serialized_app_config = config.serialize()

        assert serialized_app_config["about"] == about

    def test_it_returns_stats_workouts_limit(self, app: Flask) -> None:
        config = AppConfig.query.one()
        stats_workouts_limit = random_int()
        config.stats_workouts_limit = stats_workouts_limit

        serialized_app_config = config.serialize()

        assert (
            serialized_app_config["stats_workouts_limit"]
            == stats_workouts_limit
        )

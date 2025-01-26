from flask import Flask

from fittrackee.application.models import AppConfig
from fittrackee.application.utils import get_or_init_config


class TestGetOrInitAppConfig:
    def test_it_creates_app_config(self, app_no_config: Flask) -> None:
        get_or_init_config()

        assert AppConfig.query.count() == 1

    def test_it_inits_max_users_with_default_value(
        self, app_no_config: Flask
    ) -> None:
        get_or_init_config()

        config = AppConfig.query.one()
        assert config.max_users == 0

    def test_it_inits_max_single_file_size_with_default_value(
        self, app_no_config: Flask
    ) -> None:
        get_or_init_config()

        config = AppConfig.query.one()
        assert config.max_single_file_size == 1048576  # 1MB

    def test_it_inits_max_zip_file_size_with_default_value(
        self, app_no_config: Flask
    ) -> None:
        get_or_init_config()

        config = AppConfig.query.one()
        assert config.max_zip_file_size == 10485760  # 10MB

    def test_it_inits_gpx_limit_import_with_default_value(
        self, app_no_config: Flask
    ) -> None:
        get_or_init_config()

        config = AppConfig.query.one()
        assert config.gpx_limit_import == 10

    def test_it_returns_existing_config(self, app: Flask) -> None:
        config = get_or_init_config()

        assert config is not None
        assert config.max_users == 100

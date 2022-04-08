from flask import Flask

from fittrackee import VERSION
from fittrackee.application.models import AppConfig
from fittrackee.users.models import User


class TestConfigModel:
    def test_application_config(self, app: Flask) -> None:
        app_config = AppConfig.query.first()
        app_config.admin_contact = 'admin@example.com'

        assert app_config.is_registration_enabled is True
        assert (
            app_config.map_attribution
            == app.config['TILE_SERVER']['ATTRIBUTION']
        )

        serialized_app_config = app_config.serialize()
        assert (
            serialized_app_config['admin_contact'] == app_config.admin_contact
        )
        assert serialized_app_config['federation_enabled'] is False
        assert (
            serialized_app_config['gpx_limit_import']
            == app_config.gpx_limit_import
        )
        assert serialized_app_config['is_registration_enabled'] is True
        assert (
            serialized_app_config['max_single_file_size']
            == app_config.max_single_file_size
        )
        assert (
            serialized_app_config['max_zip_file_size']
            == app_config.max_zip_file_size
        )
        assert serialized_app_config['max_users'] == app_config.max_users
        assert (
            serialized_app_config['map_attribution']
            == app_config.map_attribution
        )
        assert serialized_app_config['version'] == VERSION

    def test_it_returns_registration_disabled_when_users_count_exceeds_limit(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        app_config = AppConfig.query.first()
        app_config.max_users = 2
        serialized_app_config = app_config.serialize()

        assert app_config.is_registration_enabled is False
        assert serialized_app_config['is_registration_enabled'] is False

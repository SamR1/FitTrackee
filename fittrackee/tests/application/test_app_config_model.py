from flask import Flask

from fittrackee.application.models import AppConfig


class TestConfigModel:
    def test_application_config(self, app: Flask) -> None:
        app_config = AppConfig.query.first()
        assert 1 == app_config.id

        serialized_app_config = app_config.serialize()
        assert serialized_app_config['gpx_limit_import'] == 10
        assert serialized_app_config['is_registration_enabled'] is True
        assert serialized_app_config['max_single_file_size'] == 1048576
        assert serialized_app_config['max_zip_file_size'] == 10485760
        assert serialized_app_config['max_users'] == 100
        assert serialized_app_config['map_attribution'] == (
            '&copy; <a href="http://www.openstreetmap.org/copyright" '
            'target="_blank" rel="noopener noreferrer">OpenStreetMap</a> '
            'contributors'
        )

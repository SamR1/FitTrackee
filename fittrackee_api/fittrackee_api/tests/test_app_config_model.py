from fittrackee_api.application.models import AppConfig


def test_application_config(app):
    app_config = AppConfig.query.first()
    assert 1 == app_config.id

    serialized_app_config = app_config.serialize()
    assert serialized_app_config['gpx_limit_import'] == 10
    assert serialized_app_config['is_registration_enabled'] is True
    assert serialized_app_config['max_single_file_size'] == 1048576
    assert serialized_app_config['max_zip_file_size'] == 10485760
    assert serialized_app_config['max_users'] == 10
    assert serialized_app_config['registration'] is True

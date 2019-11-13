import os

from fittrackee_api import db
from fittrackee_api.users.models import User

from .models import AppConfig

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB


def init_config():
    """
    init application configuration if not existing in database

    Note: get some configuration values from env variables
    (for FitTrackee versions prior to v0.3.0)
    """
    existing_config = AppConfig.query.one_or_none()
    nb_users = User.query.count()
    if not existing_config:
        config = AppConfig()
        config.max_users = (
            nb_users
            if os.getenv('REACT_APP_ALLOW_REGISTRATION') == "false"
            else 0
        )
        config.max_single_file_size = os.environ.get(
            'REACT_APP_MAX_SINGLE_FILE_SIZE', MAX_FILE_SIZE
        )
        config.max_zip_file_size = os.environ.get(
            'REACT_APP_MAX_ZIP_FILE_SIZE', MAX_FILE_SIZE * 10
        )
        db.session.add(config)
        db.session.commit()
        return True, config
    return False, existing_config


def update_app_config_from_database(current_app, db_config):
    current_app.config['gpx_limit_import'] = db_config.gpx_limit_import
    current_app.config['max_single_file_size'] = db_config.max_single_file_size
    current_app.config['MAX_CONTENT_LENGTH'] = db_config.max_zip_file_size
    current_app.config['max_users'] = db_config.max_users
    current_app.config[
        'is_registration_enabled'
    ] = db_config.is_registration_enabled

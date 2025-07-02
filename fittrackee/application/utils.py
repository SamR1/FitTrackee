import time
from typing import Dict, List

from flask import Flask
from sqlalchemy.exc import OperationalError

from fittrackee import db

from ..dates import get_datetime_in_utc
from .exceptions import AppConfigException
from .models import AppConfig

MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB


def get_or_init_config() -> AppConfig:
    """
    Init application configuration.
    """
    retries = 0
    while retries < 2:
        with db.session.begin():
            # Set isolation level to SERIALIZABLE to ensure that no other rows
            # are created in 'app_config' table during transaction when
            # several workers are started
            db.session.connection(
                execution_options={"isolation_level": "SERIALIZABLE"}
            )
            try:
                existing_config = AppConfig.query.one_or_none()
                if existing_config:
                    return existing_config

                config = AppConfig()
                config.max_users = 0  # no limitation
                config.max_single_file_size = MAX_FILE_SIZE
                config.max_zip_file_size = MAX_FILE_SIZE * 10
                db.session.add(config)
                db.session.commit()
                return config
            except OperationalError:
                db.session.rollback()
                retries += 1
                time.sleep(0.1)
    raise AppConfigException()


def update_app_config_from_database(
    current_app: Flask, db_config: AppConfig
) -> None:
    current_app.config.update(
        {
            "file_limit_import": db_config.file_limit_import,
            "file_sync_limit_import": db_config.file_sync_limit_import,
            "max_single_file_size": db_config.max_single_file_size,
            "MAX_CONTENT_LENGTH": db_config.max_zip_file_size,
            "max_users": db_config.max_users,
            "is_registration_enabled": db_config.is_registration_enabled,
            "privacy_policy_date": (
                db_config.privacy_policy_date
                if db_config.privacy_policy
                else get_datetime_in_utc(
                    current_app.config["DEFAULT_PRIVACY_POLICY_DATA"],
                    "%Y-%m-%d %H:%M:%S",
                )
            ),
            "stats_workouts_limit": db_config.stats_workouts_limit,
        }
    )


def verify_app_config(config_data: Dict) -> List:
    """
    Verify if application config is valid.

    If not, it returns not empty string
    """
    ret = []

    params = [
        (
            "file_sync_limit_import",
            "max files in a zip archive processed synchronously",
        ),
        ("file_limit_import", "max files in a zip archive"),
        ("max_single_file_size", "max size of uploaded files"),
        ("max_zip_file_size", "max size of zip archive"),
    ]
    for param, label in params:
        if param in config_data and config_data[param] <= 0:
            ret.append(f"{label} must be greater than 0")

    params = [
        ("max_users", "max users"),
        ("stats_workouts_limit", "max number of workouts for statistics"),
    ]
    for param, label in params:
        if param in config_data and config_data[param] < 0:
            ret.append(f"{label} must be greater than or equal to 0")

    return ret

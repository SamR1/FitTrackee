import os
from typing import Type, Union
from uuid import uuid4

from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from flask import current_app

from fittrackee import DEFAULT_PRIVACY_POLICY_DATA, VERSION
from fittrackee.constants import IMAGE_MIMETYPES
from fittrackee.languages import SUPPORTED_LANGUAGES
from fittrackee.workouts.constants import (
    HEATMAP_DEFAULT_BASE_ZOOM,
    HEATMAP_MAX_BASE_ZOOM,
    HEATMAP_MIN_BASE_ZOOM,
    WORKOUT_ALL_ALLOWED_EXTENSIONS,
)

broker: Union[Type["RedisBroker"], Type["StubBroker"]] = (
    StubBroker
    if os.getenv("APP_SETTINGS") == "fittrackee.config.TestingConfig"
    else RedisBroker
)

XDIST_WORKER = (
    f"_{os.getenv('PYTEST_XDIST_WORKER')}"
    if os.getenv("PYTEST_XDIST_WORKER")
    else ""
)


def get_heatmap_base_zoom() -> int:
    """
    Heatmap resolution, from HEATMAP_BASE_ZOOM. Each level doubles the detail
    and roughly doubles the number of stored cells, so the range is bounded:
    below the lowest value the tracks show as squares, and above the highest
    the cells mostly resolve the GPS noise.
    """
    value = os.environ.get("HEATMAP_BASE_ZOOM", "")
    if not value:
        return HEATMAP_DEFAULT_BASE_ZOOM
    try:
        base_zoom = int(value)
    except ValueError as e:
        raise ValueError(
            f"invalid HEATMAP_BASE_ZOOM: '{value}' is not an integer"
        ) from e
    if not HEATMAP_MIN_BASE_ZOOM <= base_zoom <= HEATMAP_MAX_BASE_ZOOM:
        raise ValueError(
            f"invalid HEATMAP_BASE_ZOOM: {base_zoom} is not between "
            f"{HEATMAP_MIN_BASE_ZOOM} and {HEATMAP_MAX_BASE_ZOOM}"
        )
    return base_zoom


class BaseConfig:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 13
    TOKEN_EXPIRATION_DAYS = 30
    TOKEN_EXPIRATION_SECONDS = 0
    PASSWORD_TOKEN_EXPIRATION_SECONDS = 3600
    UPLOAD_FOLDER = os.path.join(
        os.getenv("UPLOAD_FOLDER", current_app.root_path), "uploads"
    )
    PICTURE_ALLOWED_EXTENSIONS = set(IMAGE_MIMETYPES.keys())
    WORKOUT_ALLOWED_EXTENSIONS = WORKOUT_ALL_ALLOWED_EXTENSIONS
    DEFAULT_STATICMAP = (
        os.environ.get("DEFAULT_STATICMAP", "false").lower() == "true"
    )

    # resolution the heatmap cells are stored at, as a zoom level: the finest
    # detail the heatmap can display, at the cost of rows. Changing it needs a
    # rebuild ('ftcli workouts rebuild_heatmap').
    HEATMAP_BASE_ZOOM = get_heatmap_base_zoom()

    # Enable heatmap on User Interface
    # (temporary setting)
    ENABLE_HEATMAP = (
        os.environ.get("ENABLE_HEATMAP", "false").lower() == "true"
    )

    OPEN_ELEVATION_API_URL = os.environ.get("OPEN_ELEVATION_API_URL", "")
    VALHALLA_API_URL = os.environ.get("VALHALLA_API_URL", "")

    DRAMATIQ_BROKER = broker
    TASKS_PROCESSING_AVAILABLE = False

    LANGUAGES = SUPPORTED_LANGUAGES
    BABEL_DEFAULT_LOCALE = "en"
    TRANSLATIONS_FOLDER = os.path.join(current_app.root_path, "translations")

    EMAIL_URL = os.environ.get("EMAIL_URL")
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    CAN_SEND_EMAILS = False
    EMAILS_TEMPLATES_FOLDER = os.path.join(
        current_app.root_path, "emails/templates"
    )

    FEEDS_TEMPLATES_FOLDER = os.path.join(
        current_app.root_path, "feeds/templates"
    )

    UI_URL = os.environ["UI_URL"]
    OAUTH2_TOKEN_EXPIRES_IN = {
        "authorization_code": 864000,  # 10 days
        "refresh_token": 864000,  # 10 days
    }
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    DATA_EXPORT_EXPIRATION = 24  # hours
    VERSION = VERSION
    DEFAULT_PRIVACY_POLICY_DATA = DEFAULT_PRIVACY_POLICY_DATA


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.getenv("APP_SECRET_KEY")
    BCRYPT_LOG_ROUNDS = 4


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_TEST_URL", "") + XDIST_WORKER
    )
    UPLOAD_FOLDER = os.path.join(
        os.getenv("UPLOAD_FOLDER", current_app.root_path),
        "uploads" + XDIST_WORKER,
    )
    SECRET_KEY = uuid4().hex
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRATION_DAYS = 0
    TOKEN_EXPIRATION_SECONDS = 60
    PASSWORD_TOKEN_EXPIRATION_SECONDS = 60
    UI_URL = "https://example.com"
    SENDER_EMAIL = "fittrackee@example.com"
    OAUTH2_TOKEN_EXPIRES_IN = {
        "authorization_code": 60,
        "refresh_token": 60,
    }


class End2EndTestingConfig(TestingConfig):
    UI_URL = "http://0.0.0.0:5000"
    TOKEN_EXPIRATION_SECONDS = 300
    PASSWORD_TOKEN_EXPIRATION_SECONDS = 300


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.getenv("APP_SECRET_KEY")

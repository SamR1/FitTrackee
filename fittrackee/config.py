import os
from typing import Type, Union

from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from flask import current_app

from fittrackee import DEFAULT_PRIVACY_POLICY_DATA, VERSION
from fittrackee.languages import SUPPORTED_LANGUAGES
from fittrackee.workouts.constants import WORKOUT_ALLOWED_EXTENSIONS

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
    PICTURE_ALLOWED_EXTENSIONS = {"jpg", "png", "gif"}
    WORKOUT_ALLOWED_EXTENSIONS = {"zip"}.union(WORKOUT_ALLOWED_EXTENSIONS)
    TEMPLATES_FOLDER = os.path.join(current_app.root_path, "emails/templates")
    UI_URL = os.environ["UI_URL"]
    EMAIL_URL = os.environ.get("EMAIL_URL")
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    CAN_SEND_EMAILS = False
    DRAMATIQ_BROKER = broker
    TILE_SERVER = {
        "URL": os.environ.get(
            "TILE_SERVER_URL",
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        "ATTRIBUTION": os.environ.get(
            "MAP_ATTRIBUTION",
            '&copy; <a href="http://www.openstreetmap.org/copyright" '
            'target="_blank" rel="noopener noreferrer">OpenStreetMap</a>'
            " contributors",
        ),
        "DEFAULT_STATICMAP": (
            os.environ.get("DEFAULT_STATICMAP", "false").lower() == "true"
        ),
        "STATICMAP_SUBDOMAINS": os.environ.get("STATICMAP_SUBDOMAINS", ""),
    }
    TRANSLATIONS_FOLDER = os.path.join(
        current_app.root_path, "emails/translations"
    )
    LANGUAGES = SUPPORTED_LANGUAGES
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
    SECRET_KEY = "development key"  # nosec
    BCRYPT_LOG_ROUNDS = 4
    DRAMATIQ_BROKER_URL = os.getenv("REDIS_URL", "redis://")


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
    SECRET_KEY = "test key"  # nosec
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
    DRAMATIQ_BROKER_URL = os.getenv("REDIS_URL", "redis://")
    UI_URL = "http://0.0.0.0:5000"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.getenv("APP_SECRET_KEY")
    DRAMATIQ_BROKER_URL = os.getenv("REDIS_URL", "redis://")

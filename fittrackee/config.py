import os
from typing import Dict, Type, Union
from uuid import uuid4

from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.stub import StubBroker
from flask import current_app

from fittrackee import DEFAULT_PRIVACY_POLICY_DATA, VERSION
from fittrackee.application.tile_servers import (
    SUBDOMAINS,
    OSMTileProvider,
    StadiaTileProvider,
    ThunderForestTileProvider,
    TileProviderBase,
    get_tile_provider_from_env_var,
)
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


def get_tiles_providers() -> Dict[str, TileProviderBase]:
    tile_providers: Dict[str, TileProviderBase] = {
        "osm": OSMTileProvider(
            name="OpenStreetMap",
            url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        "osm_de": OSMTileProvider(
            name="OpenStreetMap (de)",
            url_template="https://tile.openstreetmap.de/{z}/{x}/{y}.png",
        ),
        "osm_fr": OSMTileProvider(
            name="OpenStreetMap (fr)",
            url_template="https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
        ),
        "cyclosm": OSMTileProvider(
            attribution=(
                '<a href="https://github.com/cyclosm/cyclosm-cartocss-style/'
                'releases" title="CyclOSM - Open Bicycle render">CyclOSM</a> |'
                ' Map data: &copy; <a href="https://www.openstreetmap.org/'
                'copyright">OpenStreetMap</a> contributors'
            ),
            name="CyclOSM",
            subdomains=SUBDOMAINS,
            url_template=(
                "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png"
            ),
        ),
        "stadiamaps_alidade_smooth": StadiaTileProvider(
            name="Stadia Alidade Smooth", style="alidade_smooth"
        ),
        "stadiamaps_outdoors": StadiaTileProvider(
            name="Stadia Outdoors", style="outdoors"
        ),
        "thunderforest_landscape": ThunderForestTileProvider(
            name="Thunderforest Landscape", style="landscape"
        ),
        "thunderforest_outdoors": ThunderForestTileProvider(
            name="Thunderforest Outdoors", style="outdoors"
        ),
    }
    custom_provider = get_tile_provider_from_env_var()
    if custom_provider:
        tile_providers["custom"] = TileProviderBase(**custom_provider)
    return tile_providers


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

    TILE_PROVIDERS = get_tiles_providers()
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

import os
import shutil
from typing import Generator, Iterator, List, Optional, Union
from unittest.mock import MagicMock, patch

import pytest
from flask import current_app

from fittrackee import create_app, db, limiter
from fittrackee.application.models import AppConfig
from fittrackee.application.utils import update_app_config_from_database
from fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service import (  # noqa
    weather_service,
)

TILE_PROVIDERS_KEYS = [
    "CUSTOM_TILE_PROVIDER_URL",
    "CUSTOM_TILE_PROVIDER_ATTRIBUTION",
    "CUSTOM_TILE_PROVIDER_SUBDOMAINS",
    "TILE_SERVER_URL",
    "STATICMAP_SUBDOMAINS",
    "MAP_ATTRIBUTION",
    "STADIAMAPS_API_KEY",
    "THUNDERFOREST_API_KEY",
]


@pytest.fixture(autouse=True)
def default_weather_service(
    request: pytest.FixtureRequest,
) -> Iterator[Optional[MagicMock]]:
    if "disable_autouse_default_weather_service" in request.keywords:
        yield None
    else:
        with patch.object(
            weather_service, "get_weather", return_value=None
        ) as mock:
            yield mock


def get_app_config(
    max_sync_workouts: Optional[int] = None,
    max_workouts: Optional[int] = None,
    max_image_size: Optional[Union[int, float]] = None,
    max_single_file_size: Optional[Union[int, float]] = None,
    max_zip_file_size: Optional[Union[int, float]] = None,
    max_users: Optional[int] = None,
    global_map_workouts_limit: Optional[int] = None,
    tile_providers: Optional[List[str]] = None,
    default_tile_provider: Optional[str] = None,
) -> AppConfig:
    config = AppConfig.query.one_or_none()
    if not config:
        config = AppConfig()
        db.session.add(config)
        db.session.flush()
    config.file_sync_limit_import = (
        10 if max_sync_workouts is None else max_sync_workouts
    )
    config.file_limit_import = 100 if max_workouts is None else max_workouts
    config.max_image_size = (
        (5 if max_image_size is None else max_image_size) * 1024 * 1024
    )
    config.max_single_file_size = (
        (1 if max_single_file_size is None else max_single_file_size)
        * 1024
        * 1024
    )
    config.max_zip_file_size = (
        (10 if max_zip_file_size is None else max_zip_file_size) * 1024 * 1024
    )
    config.max_users = 100 if max_users is None else max_users
    if global_map_workouts_limit:
        config.global_map_workouts_limit = global_map_workouts_limit
    if tile_providers:
        config.tile_providers = tile_providers
    if default_tile_provider:
        config.default_tile_provider = default_tile_provider
    db.session.commit()
    return config


def get_app(
    *,
    with_config: Optional[bool] = False,
    max_sync_workouts: Optional[int] = None,
    max_workouts: Optional[int] = None,
    max_image_size: Optional[Union[int, float]] = None,
    max_single_file_size: Optional[Union[int, float]] = None,
    max_zip_file_size: Optional[Union[int, float]] = None,
    max_users: Optional[int] = None,
    global_map_workouts_limit: Optional[int] = None,
    tasks_processing_available: bool = True,
    tile_providers: Optional[List[str]] = None,
    default_tile_provider: Optional[str] = None,
) -> Generator:
    app = create_app()
    app.config["TASKS_PROCESSING_AVAILABLE"] = tasks_processing_available
    limiter.enabled = False
    with app.app_context():
        try:
            db.create_all()
            if with_config:
                app_db_config = get_app_config(
                    max_sync_workouts,
                    max_workouts,
                    max_image_size,
                    max_single_file_size,
                    max_zip_file_size,
                    max_users,
                    global_map_workouts_limit,
                    tile_providers,
                    default_tile_provider,
                )
                update_app_config_from_database(app, app_db_config)
            yield app
        except Exception as e:
            print(f"Error with app configuration: {e}")  # noqa: T201
        finally:
            db.session.remove()
            db.drop_all()
            # close unused idle connections => avoid the following error:
            # FATAL: remaining connection slots are reserved for
            # non-replication superuser connections
            db.engine.dispose()
            # remove all temp files like gpx files
            shutil.rmtree(
                current_app.config["UPLOAD_FOLDER"],
                ignore_errors=True,
            )


def delete_env_vars(
    env_vars: List[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    for env_var in env_vars:
        if os.getenv(env_var):
            monkeypatch.delenv(env_var)


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    delete_env_vars(
        [
            *TILE_PROVIDERS_KEYS,
            "DEFAULT_STATICMAP",
            "NOMINATIM_URL",
            "ENABLE_GEOSPATIAL_FEATURES",
            "API_RATE_LIMITS",
            "OPEN_ELEVATION_API_URL",
            "VALHALLA_API_URL",
            "HEATMAP_BASE_ZOOM",
            "ENABLE_HEATMAP",
        ],
        monkeypatch,
    )
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_enabled_heatmap(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("ENABLE_HEATMAP", "true")
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_multiple_tile_servers_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    delete_env_vars(
        [
            *TILE_PROVIDERS_KEYS,
            "DEFAULT_STATICMAP",
        ],
        monkeypatch,
    )
    yield from get_app(
        with_config=True,
        tile_providers=["osm", "osm_fr", "cyclosm"],
        default_tile_provider="cyclosm",
    )


@pytest.fixture
def app_with_custom_tile_server(monkeypatch: pytest.MonkeyPatch) -> Generator:
    """
    custom tile server set before FitTrackee 1.4.0
    """
    delete_env_vars(
        [
            *TILE_PROVIDERS_KEYS,
            "DEFAULT_STATICMAP",
        ],
        monkeypatch,
    )
    monkeypatch.setenv(
        "CUSTOM_TILE_PROVIDER_URL",
        "https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=XXXX",
    )
    yield from get_app(
        with_config=True,
        tile_providers=["custom"],
        default_tile_provider="custom",
    )


@pytest.fixture
def app_with_deprecated_custom_tile_server(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    """
    custom tile server set before FitTrackee 1.4.0
    """
    delete_env_vars(
        [
            *TILE_PROVIDERS_KEYS,
            "DEFAULT_STATICMAP",
        ],
        monkeypatch,
    )
    monkeypatch.setenv(
        "TILE_SERVER_URL",
        "https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=XXXX",
    )
    yield from get_app(
        with_config=True,
        tile_providers=["custom"],
        default_tile_provider="custom",
    )


@pytest.fixture
def app_default_static_map(monkeypatch: pytest.MonkeyPatch) -> Generator:
    delete_env_vars(
        TILE_PROVIDERS_KEYS,
        monkeypatch,
    )
    monkeypatch.setenv("DEFAULT_STATICMAP", "True")
    yield from get_app(
        with_config=True,
        tile_providers=["osm_de"],
        default_tile_provider="osm_de",
    )


@pytest.fixture
def app_with_missing_tile_provider_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    delete_env_vars(
        [*TILE_PROVIDERS_KEYS, "DEFAULT_STATICMAP"],
        monkeypatch,
    )
    yield from get_app(
        with_config=True,
        tile_providers=["osm", "cyclosm", "thunderforest_outdoors"],
        default_tile_provider="cyclosm",
    )


@pytest.fixture
def app_with_max_workouts(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_sync_workouts=1, max_workouts=2)


@pytest.fixture
def app_with_max_file_size_equals_0(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_single_file_size=0)


@pytest.fixture
def app_with_max_file_size(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_single_file_size=0.001)


@pytest.fixture
def app_with_max_zip_file_size(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_zip_file_size=0.001)


@pytest.fixture
def app_with_max_image_size(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_image_size=0.001)


@pytest.fixture
def app_with_3_users_max(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_users=3)


@pytest.fixture
def app_no_config(monkeypatch: pytest.MonkeyPatch) -> Generator:
    delete_env_vars(
        [
            *TILE_PROVIDERS_KEYS,
            "DEFAULT_STATICMAP",
            "NOMINATIM_URL",
            "ENABLE_GEOSPATIAL_FEATURES",
            "API_RATE_LIMITS",
            "OPEN_ELEVATION_API_URL",
            "VALHALLA_API_URL",
            "HEATMAP_BASE_ZOOM",
            "ENABLE_HEATMAP",
        ],
        monkeypatch,
    )
    yield from get_app(with_config=False)


@pytest.fixture
def app_ssl(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv(
        "EMAIL_URL", "smtp://username:password@0.0.0.0:1025?ssl=True"
    )
    yield from get_app(with_config=True)


@pytest.fixture
def app_tls(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv(
        "EMAIL_URL", "smtp://username:password@0.0.0.0:1025?tls=True"
    )
    yield from get_app(with_config=True)


@pytest.fixture
def app_wo_email_auth(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://0.0.0.0:1025")
    yield from get_app(with_config=True)


@pytest.fixture
def app_wo_email_activation(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "")
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_nominatim_url(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("NOMINATIM_URL", "https://nominatim.example.com")
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_open_elevation_url(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv(
        "OPEN_ELEVATION_API_URL", "https://api.open-elevation.example.com"
    )
    delete_env_vars(
        ["VALHALLA_API_URL"],
        monkeypatch,
    )
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_valhalla_url(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("VALHALLA_API_URL", "https://api.valhalla.example.com")
    delete_env_vars(
        ["OPEN_ELEVATION_API_URL"],
        monkeypatch,
    )
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_open_elevation_and_valhalla_url(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    monkeypatch.setenv(
        "OPEN_ELEVATION_API_URL", "https://api.open-elevation.example.com"
    )
    monkeypatch.setenv("VALHALLA_API_URL", "https://api.valhalla.example.com")
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_empty_string_as_open_elevation_and_valhalla_url(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    monkeypatch.setenv("OPEN_ELEVATION_API_URL", "")
    monkeypatch.setenv("VALHALLA_API_URL", "")
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_global_map_workouts_limit_equal_to_1(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    yield from get_app(with_config=True, global_map_workouts_limit=1)


@pytest.fixture
def app_with_task_processing_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator:
    yield from get_app(with_config=True, tasks_processing_available=False)


@pytest.fixture()
def app_config() -> AppConfig:
    config = AppConfig()
    config.file_sync_limit_import = 10
    config.file_limit_import = 100
    config.max_single_file_size = 1048576
    config.max_zip_file_size = 10485760
    config.max_users = 0
    db.session.add(config)
    db.session.commit()
    return config

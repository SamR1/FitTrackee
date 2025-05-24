import os
import shutil
from typing import Generator, Iterator, Optional, Union
from unittest.mock import MagicMock, patch

import pytest
from flask import current_app

from fittrackee import create_app, db, limiter
from fittrackee.application.models import AppConfig
from fittrackee.application.utils import update_app_config_from_database
from fittrackee.workouts.services.workout_from_file.base_workout_with_segment_service import (  # noqa
    weather_service,
)


@pytest.fixture(autouse=True)
def default_weather_service() -> Iterator[MagicMock]:
    with patch.object(
        weather_service, "get_weather", return_value=None
    ) as mock:
        yield mock


def get_app_config(
    max_sync_workouts: Optional[int] = None,
    max_workouts: Optional[int] = None,
    max_single_file_size: Optional[Union[int, float]] = None,
    max_zip_file_size: Optional[Union[int, float]] = None,
    max_users: Optional[int] = None,
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
    config.max_single_file_size = (
        (1 if max_single_file_size is None else max_single_file_size)
        * 1024
        * 1024
    )
    config.max_zip_file_size = (
        (10 if max_zip_file_size is None else max_zip_file_size) * 1024 * 1024
    )
    config.max_users = 100 if max_users is None else max_users
    db.session.commit()
    return config


def get_app(
    *,
    with_config: Optional[bool] = False,
    max_sync_workouts: Optional[int] = None,
    max_workouts: Optional[int] = None,
    max_single_file_size: Optional[Union[int, float]] = None,
    max_zip_file_size: Optional[Union[int, float]] = None,
    max_users: Optional[int] = None,
) -> Generator:
    app = create_app()
    limiter.enabled = False
    with app.app_context():
        try:
            db.create_all()
            if with_config:
                app_db_config = get_app_config(
                    max_sync_workouts,
                    max_workouts,
                    max_single_file_size,
                    max_zip_file_size,
                    max_users,
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
            return app  # type: ignore  # noqa: B012


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    if os.getenv("TILE_SERVER_URL"):
        monkeypatch.delenv("TILE_SERVER_URL")
    if os.getenv("STATICMAP_SUBDOMAINS"):
        monkeypatch.delenv("STATICMAP_SUBDOMAINS")
    if os.getenv("MAP_ATTRIBUTION"):
        monkeypatch.delenv("MAP_ATTRIBUTION")
    if os.getenv("DEFAULT_STATICMAP"):
        monkeypatch.delenv("DEFAULT_STATICMAP")
    yield from get_app(with_config=True)


@pytest.fixture
def app_default_static_map(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv(
        "TILE_SERVER_URL", "https://tile.openstreetmap.de/{z}/{x}/{y}.png"
    )
    monkeypatch.setenv("DEFAULT_STATICMAP", "True")
    yield from get_app(with_config=True)


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
def app_with_3_users_max(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv("EMAIL_URL", "smtp://none:none@0.0.0.0:1025")
    yield from get_app(with_config=True, max_users=3)


@pytest.fixture
def app_no_config(monkeypatch: pytest.MonkeyPatch) -> Generator:
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

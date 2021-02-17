import os
from typing import Generator, Optional

import pytest

from fittrackee import create_app, db
from fittrackee.application.models import AppConfig
from fittrackee.application.utils import update_app_config_from_database


def get_app_config(
    with_config: Optional[bool] = False,
    max_workouts: Optional[int] = None,
) -> Optional[AppConfig]:
    if with_config:
        config = AppConfig()
        config.gpx_limit_import = 10 if max_workouts is None else max_workouts
        config.max_single_file_size = 1 * 1024 * 1024
        config.max_zip_file_size = 1 * 1024 * 1024 * 10
        config.max_users = 100
        db.session.add(config)
        db.session.commit()
        return config
    return None


def get_app(
    with_config: Optional[bool] = False,
    max_workouts: Optional[int] = None,
) -> Generator:
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            app_db_config = get_app_config(with_config, max_workouts)
            if app_db_config:
                update_app_config_from_database(app, app_db_config)
            yield app
        except Exception as e:
            print(f'Error with app configuration: {e}')
        finally:
            db.session.remove()
            db.drop_all()
            # close unused idle connections => avoid the following error:
            # FATAL: remaining connection slots are reserved for
            # non-replication superuser connections
            db.engine.dispose()
            return app


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025')
    if os.getenv('TILE_SERVER_URL'):
        monkeypatch.delenv('TILE_SERVER_URL')
    if os.getenv('MAP_ATTRIBUTION'):
        monkeypatch.delenv('MAP_ATTRIBUTION')
    yield from get_app(with_config=True)


@pytest.fixture
def app_with_max_workouts(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025')
    yield from get_app(with_config=True, max_workouts=2)


@pytest.fixture
def app_no_config() -> Generator:
    yield from get_app(with_config=False)


@pytest.fixture
def app_ssl(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025?ssl=True')
    yield from get_app(with_config=True)


@pytest.fixture
def app_tls(monkeypatch: pytest.MonkeyPatch) -> Generator:
    monkeypatch.setenv('EMAIL_URL', 'smtp://none:none@0.0.0.0:1025?tls=True')
    yield from get_app(with_config=True)


@pytest.fixture
def app_wo_domain() -> Generator:
    yield from get_app(with_config=True)


@pytest.fixture()
def app_config() -> AppConfig:
    config = AppConfig()
    config.gpx_limit_import = 10
    config.max_single_file_size = 1048576
    config.max_zip_file_size = 10485760
    config.max_users = 0
    db.session.add(config)
    db.session.commit()
    return config

from flask import Flask

from fittrackee.application.utils import (
    init_config,
    update_app_config_from_database,
)


def init_database(app: Flask) -> None:
    """Init the database."""
    _, db_app_config = init_config()
    update_app_config_from_database(app, db_app_config)

    print('Initial data stored in database.')

from flask import Flask

from fittrackee import db
from fittrackee.application.utils import (
    init_config,
    update_app_config_from_database,
)
from fittrackee.users.models import User


def init_database(app: Flask) -> None:
    """Init the database."""
    admin = User(
        username='admin', email='admin@example.com', password='mpwoadmin'
    )
    admin.admin = True
    admin.timezone = 'Europe/Paris'
    db.session.add(admin)
    db.session.commit()
    _, db_app_config = init_config()
    update_app_config_from_database(app, db_app_config)

    print('Initial data stored in database.')

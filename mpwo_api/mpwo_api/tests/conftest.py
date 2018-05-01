import os

import pytest
from mpwo_api import create_app, db

os.environ["FLASK_ENV"] = 'testing'
os.environ["APP_SETTINGS"] = 'mpwo_api.config.TestingConfig'


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        return app

import pytest
from mpwo_api import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object('mpwo_api.config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        return app

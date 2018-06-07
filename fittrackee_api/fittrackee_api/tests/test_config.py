import os


def test_development_config(app):
    app.config.from_object('fittrackee_api.config.DevelopmentConfig')
    assert app.config['DEBUG']
    assert not app.config['TESTING']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
        'DATABASE_URL')


def test_testing_config(app):
    app.config.from_object('fittrackee_api.config.TestingConfig')
    assert app.config['DEBUG']
    assert app.config['TESTING']
    assert not app.config['PRESERVE_CONTEXT_ON_EXCEPTION']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
        'DATABASE_TEST_URL')

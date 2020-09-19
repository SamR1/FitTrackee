import os


class TestConfig:
    def test_development_config(self, app):
        app.config.from_object('fittrackee.config.DevelopmentConfig')
        assert app.config['DEBUG']
        assert not app.config['TESTING']
        assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
            'DATABASE_URL'
        )

    def test_testing_config(self, app):
        app.config.from_object('fittrackee.config.TestingConfig')
        assert app.config['DEBUG']
        assert app.config['TESTING']
        assert not app.config['PRESERVE_CONTEXT_ON_EXCEPTION']
        assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
            'DATABASE_TEST_URL'
        )

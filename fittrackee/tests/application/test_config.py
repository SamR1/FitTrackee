import os

from flask import Flask


class TestDevelopmentConfig:
    def test_debug_is_enabled(self, app: Flask) -> None:
        app.config.from_object('fittrackee.config.DevelopmentConfig')

        assert app.config['DEBUG']

    def test_testing_is_disabled(self, app: Flask) -> None:
        app.config.from_object('fittrackee.config.DevelopmentConfig')

        assert not app.config['TESTING']

    def test_sqlalchemy_is_configured_to_use_dev_database(
        self, app: Flask
    ) -> None:
        app.config.from_object('fittrackee.config.DevelopmentConfig')

        assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
            'DATABASE_URL'
        )


class TestTestingConfig:
    def test_debug_is_enabled(self, app: Flask) -> None:
        app.config.from_object('fittrackee.config.TestingConfig')

        assert app.config['DEBUG']

    def test_testing_is_enabled(self, app: Flask) -> None:
        app.config.from_object('fittrackee.config.TestingConfig')

        assert app.config['TESTING']

    def test_sqlalchemy_is_configured_to_use_testing_database(
        self, app: Flask
    ) -> None:
        app.config.from_object('fittrackee.config.TestingConfig')

        assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
            'DATABASE_TEST_URL'
        )

    def test_it_does_not_preserve_context_on_exception(
        self, app: Flask
    ) -> None:
        app.config.from_object('fittrackee.config.TestingConfig')

        assert not app.config['PRESERVE_CONTEXT_ON_EXCEPTION']


class TestProductionConfig:
    def test_debug_is_disabled(self, app: Flask) -> None:
        app.config.from_object('fittrackee.config.ProductionConfig')

        assert not app.config['DEBUG']

    def test_testing_is_disabled(self, app: Flask) -> None:
        app.config.from_object('fittrackee.config.ProductionConfig')

        assert not app.config['TESTING']

    def test_sqlalchemy_is_configured_to_use_testing_database(
        self, app: Flask
    ) -> None:
        app.config.from_object('fittrackee.config.ProductionConfig')

        assert app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get(
            'DATABASE_TEST_URL'
        )

    def test_it_does_not_preserve_context_on_exception(
        self, app: Flask
    ) -> None:
        app.config.from_object('fittrackee.config.ProductionConfig')

        assert not app.config['PRESERVE_CONTEXT_ON_EXCEPTION']

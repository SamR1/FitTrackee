import os

from flask import Flask

from fittrackee import DEFAULT_PRIVACY_POLICY_DATA, VERSION


class TestDevelopmentConfig:
    def test_debug_is_enabled(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert app.config["DEBUG"]

    def test_testing_is_disabled(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert not app.config["TESTING"]

    def test_sqlalchemy_is_configured_to_use_dev_database(
        self, app: Flask
    ) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get(
            "DATABASE_URL"
        )

    def test_it_returns_application_version(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert app.config["VERSION"] == VERSION

    def test_it_returns_default_privacy_policy_date(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert (
            app.config["DEFAULT_PRIVACY_POLICY_DATA"]
            == DEFAULT_PRIVACY_POLICY_DATA
        )


class TestTestingConfig:
    def test_debug_is_enabled(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.TestingConfig")

        assert app.config["DEBUG"]

    def test_testing_is_enabled(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.TestingConfig")

        assert app.config["TESTING"]

    def test_sqlalchemy_is_configured_to_use_testing_database(
        self, app: Flask
    ) -> None:
        app.config.from_object("fittrackee.config.TestingConfig")

        assert app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get(
            "DATABASE_TEST_URL", ""
        ) + (
            f"_{os.getenv('PYTEST_XDIST_WORKER')}"
            if os.getenv("PYTEST_XDIST_WORKER")
            else ""
        )

    def test_it_returns_application_version(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.TestingConfig")

        assert app.config["VERSION"] == VERSION

    def test_it_returns_default_privacy_policy_date(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert (
            app.config["DEFAULT_PRIVACY_POLICY_DATA"]
            == DEFAULT_PRIVACY_POLICY_DATA
        )


class TestProductionConfig:
    def test_debug_is_disabled(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.ProductionConfig")

        assert not app.config["DEBUG"]

    def test_testing_is_disabled(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.ProductionConfig")

        assert not app.config["TESTING"]

    def test_sqlalchemy_is_configured_to_use_testing_database(
        self, app: Flask
    ) -> None:
        app.config.from_object("fittrackee.config.ProductionConfig")

        assert app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get(
            "DATABASE_TEST_URL"
        )

    def test_it_returns_application_version(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.ProductionConfig")

        assert app.config["VERSION"] == VERSION

    def test_it_returns_default_privacy_policy_date(self, app: Flask) -> None:
        app.config.from_object("fittrackee.config.DevelopmentConfig")

        assert (
            app.config["DEFAULT_PRIVACY_POLICY_DATA"]
            == DEFAULT_PRIVACY_POLICY_DATA
        )

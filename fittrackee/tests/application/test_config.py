import os
from unittest.mock import patch

import pytest
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


class TestHeatmapBaseZoomConfig:
    """
    the helper is imported in the tests: importing the config module needs an
    application context
    """

    def test_it_returns_default_when_not_set(self, app: Flask) -> None:
        from fittrackee.config import get_heatmap_base_zoom
        from fittrackee.workouts.constants import HEATMAP_DEFAULT_BASE_ZOOM

        with patch.dict("os.environ", {}, clear=True):
            assert get_heatmap_base_zoom() == HEATMAP_DEFAULT_BASE_ZOOM

    @pytest.mark.parametrize("input_zoom", [20, 22, 24])
    def test_it_returns_given_zoom(self, app: Flask, input_zoom: int) -> None:
        from fittrackee.config import get_heatmap_base_zoom

        with patch.dict("os.environ", {"HEATMAP_BASE_ZOOM": str(input_zoom)}):
            assert get_heatmap_base_zoom() == input_zoom

    @pytest.mark.parametrize("input_zoom", ["abc", "24.5", "-"])
    def test_it_raises_error_when_zoom_is_not_an_integer(
        self, app: Flask, input_zoom: str
    ) -> None:
        from fittrackee.config import get_heatmap_base_zoom

        with patch.dict("os.environ", {"HEATMAP_BASE_ZOOM": input_zoom}):
            with pytest.raises(ValueError, match="not an integer"):
                get_heatmap_base_zoom()

    @pytest.mark.parametrize("input_zoom", [19, 25, 0, -1])
    def test_it_raises_error_when_zoom_is_out_of_range(
        self, app: Flask, input_zoom: int
    ) -> None:
        from fittrackee.config import get_heatmap_base_zoom

        with patch.dict("os.environ", {"HEATMAP_BASE_ZOOM": str(input_zoom)}):
            with pytest.raises(ValueError, match="is not between"):
                get_heatmap_base_zoom()

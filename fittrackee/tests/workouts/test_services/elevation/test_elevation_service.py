from typing import TYPE_CHECKING, List, Tuple
from unittest.mock import patch, sentinel

import pytest

from fittrackee.constants import MissingElevationsProcessing
from fittrackee.workouts.services.elevation.elevation_service import (
    ElevationService,
)
from fittrackee.workouts.services.elevation.open_elevation_service import (
    OpenElevationService,
)
from fittrackee.workouts.services.elevation.valhalla_elevation_service import (
    ValhallaElevationService,
)

if TYPE_CHECKING:
    from flask import Flask
    from gpxpy.gpx import GPXTrackPoint

    from fittrackee.users.models import User


class TestElevationServiceInstantiation:
    def test_it_instantiates_service_when_no_elevation_api_urls_set_in_env_var(
        self, app: "Flask", user_1: "User"
    ) -> None:
        # user preference is None
        service = ElevationService(user_1)

        assert service.elevation_service is None
        assert service.smooth is False

    def test_it_instantiates_service_when_all_elevation_api_urls_set_and_preference_is_none(  # noqa
        self, app_with_open_elevation_and_valhalla_url: "Flask", user_1: "User"
    ) -> None:
        # user preference is None
        service = ElevationService(user_1)

        assert service.elevation_service is None
        assert service.smooth is False

    def test_it_instantiates_service_when_no_elevation_api_urls_set_and_preference_is_not_none(  # noqa
        self, app: "Flask", user_1: "User"
    ) -> None:
        user_1.missing_elevations_processing = (
            MissingElevationsProcessing.OPEN_ELEVATION
        )
        service = ElevationService(user_1)

        assert service.elevation_service is None
        assert service.smooth is False

    @pytest.mark.parametrize(
        "input_preference,expected_service,expected_smooth",
        [
            (
                MissingElevationsProcessing.OPEN_ELEVATION,
                OpenElevationService,
                False,
            ),
            (
                MissingElevationsProcessing.OPEN_ELEVATION_SMOOTH,
                OpenElevationService,
                True,
            ),
            (
                MissingElevationsProcessing.VALHALLA,
                ValhallaElevationService,
                False,
            ),
        ],
    )
    def test_it_instantiates_service_when_all_elevation_api_urls_set_and_preference_is_set(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        input_preference: "MissingElevationsProcessing",
        expected_service: Tuple[
            "OpenElevationService", "ValhallaElevationService"
        ],
        expected_smooth: bool,
    ) -> None:
        user_1.missing_elevations_processing = input_preference
        service = ElevationService(user_1)

        assert isinstance(service.elevation_service, expected_service)  # type: ignore[arg-type]
        assert service.smooth is expected_smooth


class TestElevationServiceGetElevations:
    @pytest.mark.parametrize(
        "input_preferences",
        [
            MissingElevationsProcessing.OPEN_ELEVATION,
            MissingElevationsProcessing.VALHALLA,
        ],
    )
    def test_it_does_not_call_elevation_service_when_no_service_set(
        self,
        app: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
        input_preferences: "MissingElevationsProcessing",
    ) -> None:
        user_1.missing_elevations_processing = input_preferences
        service = ElevationService(user_1)

        with (
            patch.object(
                OpenElevationService, "get_elevations"
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService, "get_elevations"
            ) as get_valhalla_elevations_mock,
        ):
            results = service.get_elevations(
                gpx_track_points_without_elevations
            )

        assert results == []
        get_open_elevations_mock.assert_not_called()
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_calls_open_elevation(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        user_1.missing_elevations_processing = (
            MissingElevationsProcessing.OPEN_ELEVATION
        )
        service = ElevationService(user_1)

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService, "get_elevations", return_value=[]
            ) as get_valhalla_elevations_mock,
        ):
            service.get_elevations(gpx_track_points_without_elevations)

        get_open_elevations_mock.assert_called_once_with(
            gpx_track_points_without_elevations, smooth=False
        )
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_calls_open_elevation_with_smooth_as_true(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        user_1.missing_elevations_processing = (
            MissingElevationsProcessing.OPEN_ELEVATION_SMOOTH
        )
        service = ElevationService(user_1)

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService, "get_elevations", return_value=[]
            ) as get_valhalla_elevations_mock,
        ):
            service.get_elevations(gpx_track_points_without_elevations)

        get_open_elevations_mock.assert_called_once_with(
            gpx_track_points_without_elevations, smooth=True
        )
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_calls_valhalla(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        user_1.missing_elevations_processing = (
            MissingElevationsProcessing.VALHALLA
        )
        service = ElevationService(user_1)

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService, "get_elevations", return_value=[]
            ) as get_valhalla_elevations_mock,
        ):
            service.get_elevations(gpx_track_points_without_elevations)

        get_valhalla_elevations_mock.assert_called_once_with(
            gpx_track_points_without_elevations, smooth=False
        )
        get_open_elevations_mock.assert_not_called()

    @pytest.mark.parametrize(
        "input_preferences,expected_response",
        [
            (MissingElevationsProcessing.OPEN_ELEVATION, "open_api_response"),
            (MissingElevationsProcessing.VALHALLA, "valhalla_response"),
        ],
    )
    def test_it_returns_elevation_service_response(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
        input_preferences: "MissingElevationsProcessing",
        expected_response: str,
    ) -> None:
        user_1.missing_elevations_processing = input_preferences
        service = ElevationService(user_1)

        with (
            patch.object(
                OpenElevationService,
                "get_elevations",
                return_value=sentinel.open_api_response,
            ),
            patch.object(
                ValhallaElevationService,
                "get_elevations",
                return_value=sentinel.valhalla_response,
            ),
        ):
            results = service.get_elevations(
                gpx_track_points_without_elevations
            )

        assert results == getattr(sentinel, expected_response)

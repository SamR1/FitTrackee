from typing import TYPE_CHECKING, List, Tuple
from unittest.mock import patch, sentinel

import pytest

from fittrackee.constants import ElevationDataSource, ElevationProcessing
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
        self, app: "Flask"
    ) -> None:
        service = ElevationService(
            ElevationDataSource.FILE, ElevationProcessing.NONE
        )

        assert service.elevation_service is None
        assert service.elevation_data_source == ElevationDataSource.FILE
        assert service.elevation_processing == ElevationProcessing.NONE

    def test_it_instantiates_service_when_all_elevation_api_urls_set_and_preference_is_file(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
    ) -> None:
        # user preference is None
        service = ElevationService(
            ElevationDataSource.FILE, ElevationProcessing.NONE
        )

        assert service.elevation_service is None
        assert service.elevation_data_source == ElevationDataSource.FILE
        assert service.elevation_processing == ElevationProcessing.NONE

    def test_it_instantiates_service_when_no_elevation_api_urls_set_and_preference_is_not_file(  # noqa
        self, app: "Flask", user_1: "User"
    ) -> None:
        service = ElevationService(
            ElevationDataSource.OPEN_ELEVATION, ElevationProcessing.NONE
        )

        assert service.elevation_service is None
        assert service.elevation_data_source == ElevationDataSource.FILE
        assert service.elevation_processing == ElevationProcessing.NONE

    @pytest.mark.parametrize(
        "input_elevation_data_source,input_elevation_processing,"
        "expected_service",
        [
            (
                ElevationDataSource.OPEN_ELEVATION,
                ElevationProcessing.FLAT_WINDOW,
                OpenElevationService,
            ),
            (
                ElevationDataSource.VALHALLA,
                ElevationProcessing.NONE,
                ValhallaElevationService,
            ),
        ],
    )
    def test_it_instantiates_service_when_all_elevation_api_urls_set_and_preference_is_set(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        input_elevation_data_source: "ElevationDataSource",
        input_elevation_processing: "ElevationProcessing",
        expected_service: Tuple[
            "OpenElevationService", "ValhallaElevationService"
        ],
    ) -> None:
        service = ElevationService(
            input_elevation_data_source, input_elevation_processing
        )

        assert isinstance(service.elevation_service, expected_service)  # type: ignore[arg-type]
        assert service.elevation_data_source == input_elevation_data_source
        assert service.elevation_processing == input_elevation_processing


class TestElevationServiceGetElevations:
    @pytest.mark.parametrize(
        "input_preferences",
        [
            ElevationDataSource.OPEN_ELEVATION,
            ElevationDataSource.VALHALLA,
        ],
    )
    def test_it_does_not_call_elevation_service_when_no_service_set(
        self,
        app: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
        input_preferences: "ElevationDataSource",
    ) -> None:
        user_1.missing_elevations_data_source = input_preferences
        service = ElevationService(
            user_1.missing_elevations_data_source, ElevationProcessing.NONE
        )

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
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ElevationService(
            ElevationDataSource.OPEN_ELEVATION, ElevationProcessing.NONE
        )

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
            gpx_track_points_without_elevations,
            elevation_processing=ElevationProcessing.NONE,
        )
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_calls_open_elevation_with_flat_window_processing(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ElevationService(
            ElevationDataSource.OPEN_ELEVATION,
            ElevationProcessing.FLAT_WINDOW,
        )

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
            gpx_track_points_without_elevations,
            elevation_processing=ElevationProcessing.FLAT_WINDOW,
        )
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_calls_valhalla(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        user_1: "User",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ElevationService(
            ElevationDataSource.VALHALLA, ElevationProcessing.NONE
        )

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
            gpx_track_points_without_elevations,
            elevation_processing=ElevationProcessing.NONE,
        )
        get_open_elevations_mock.assert_not_called()

    @pytest.mark.parametrize(
        "input_elevation_data_source,expected_response",
        [
            (ElevationDataSource.OPEN_ELEVATION, "open_api_response"),
            (ElevationDataSource.VALHALLA, "valhalla_response"),
        ],
    )
    def test_it_returns_elevation_service_response(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
        input_elevation_data_source: "ElevationDataSource",
        expected_response: str,
    ) -> None:
        service = ElevationService(
            input_elevation_data_source, ElevationProcessing.NONE
        )

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

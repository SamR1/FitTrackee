from typing import TYPE_CHECKING, List
from unittest.mock import patch

import requests

from fittrackee.tests.mixins import ResponseMockMixin
from fittrackee.workouts.services.elevation.valhalla_elevation_service import (
    ValhallaElevationService,
)

if TYPE_CHECKING:
    from flask import Flask
    from gpxpy.gpx import GPXTrackPoint

VALHALLA_RESPONSE = [
    998.0,
    998.0,
    994.0,
    994.0,
    994.0,
    1124.0,
    1124.0,
    1124.0,
    1124.0,
]


class TestValhallaElevationServiceInstantiation:
    def test_it_instantiates_service_when_no_valhalla_url_set_in_env_var(
        self, app: "Flask"
    ) -> None:
        service = ValhallaElevationService()

        assert service.url is None
        assert service.is_enabled is False

    def test_it_instantiates_service_when_valhalla_url_is_set_in_env_var(
        self, app_with_valhalla_url: "Flask"
    ) -> None:
        service = ValhallaElevationService()

        assert service.url == "https://api.valhalla.example.com/height"
        assert service.is_enabled is True


class TestValhallaElevationServiceGetElevation(ResponseMockMixin):
    def test_it_does_not_call_valhalla_elevation_api_when_no_url_set(
        self,
        app: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response({}),
        ) as post_mock:
            service.get_elevations(gpx_track_points_without_elevations)

        post_mock.assert_not_called()

    def test_it_calls_valhalla_elevation_api_with_given_points(
        self,
        app_with_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response({"height": VALHALLA_RESPONSE}),
        ) as post_mock:
            service.get_elevations(gpx_track_points_without_elevations)

        post_mock.assert_called_once_with(
            service.url,
            json={
                "shape": [
                    {
                        "lat": point.latitude,
                        "lon": point.longitude,
                    }
                    for point in gpx_track_points_without_elevations
                ]
            },
            timeout=30,
        )

    def test_it_returns_elevations(
        self,
        app_with_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response({"height": VALHALLA_RESPONSE}),
        ):
            result = service.get_elevations(
                gpx_track_points_without_elevations
            )

        assert result == VALHALLA_RESPONSE

    def test_it_returns_empty_list_when_valhalla_elevation_api_raises_exception(  # noqa
        self,
        app_with_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with patch.object(
            requests,
            "post",
            side_effect=requests.exceptions.HTTPError,
        ):
            result = service.get_elevations(
                gpx_track_points_without_elevations
            )

        assert result == []

    def test_it_logs_error_when_valhalla_elevation_api_raises_exception(
        self,
        app_with_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with (
            patch(
                "fittrackee.workouts.services.elevation."
                "valhalla_elevation_service.appLog"
            ) as logger_mock,
            patch.object(
                requests,
                "post",
                side_effect=requests.exceptions.HTTPError,
            ),
        ):
            service.get_elevations(gpx_track_points_without_elevations)

        logger_mock.exception.assert_called_once_with(
            "Valhalla Elevation API: error when getting missing elevations"
        )

    def test_it_returns_empty_list_when_number_of_elevation_returned_valhalla_does_not_match(  # noqa
        self,
        app_with_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response({"height": VALHALLA_RESPONSE[:-1]}),
        ):
            result = service.get_elevations(
                gpx_track_points_without_elevations
            )

        assert result == []

    def test_it_logs_error_when_number_of_elevation_returned_valhalla_elevation_does_not_match(  # noqa
        self,
        app_with_valhalla_url: "Flask",
        gpx_track_points_without_elevations: List["GPXTrackPoint"],
    ) -> None:
        service = ValhallaElevationService()

        with (
            patch(
                "fittrackee.workouts.services.elevation."
                "base_elevation_service.appLog"
            ) as logger_mock,
            patch.object(
                requests,
                "post",
                return_value=self.get_response(
                    {"height": VALHALLA_RESPONSE[:-1]}
                ),
            ),
        ):
            service.get_elevations(gpx_track_points_without_elevations)

        logger_mock.error.assert_called_once_with(
            "Valhalla Elevation API: mismatch between number of points in "
            "results, ignoring results"
        )

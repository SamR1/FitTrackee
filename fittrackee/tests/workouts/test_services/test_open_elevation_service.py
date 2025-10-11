from typing import TYPE_CHECKING
from unittest.mock import patch

import requests
from gpxpy.gpx import GPXTrackPoint

from fittrackee.workouts.services.elevation.open_elevation_service import (
    OpenElevationService,
)

from ...mixins import ResponseMockMixin

if TYPE_CHECKING:
    from flask import Flask

POINTS_WITHOUT_ELEVATION = [
    GPXTrackPoint(latitude=44.68095, longitude=6.07367),
    GPXTrackPoint(latitude=44.68091, longitude=6.07367),
    GPXTrackPoint(latitude=44.6808, longitude=6.07364),
]
OPEN_ELEVATION_RESPONSE = {
    "results": [
        {
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
        },
        {
            "elevation": 998.0,
            "latitude": 44.68091,
            "longitude": 6.07367,
        },
        {
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
        },
    ]
}


class TestOpenElevationServiceInstantiation:
    def test_it_instantiates_service_when_no_open_api_url_set_in_env_var(
        self, app: "Flask"
    ) -> None:
        service = OpenElevationService()

        assert service.url is None
        assert service.is_enabled is False

    def test_it_instantiates_service_when_nominatim_url_is_set_in_env_var(
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        service = OpenElevationService()

        assert (
            service.url
            == "https://api.open-elevation.example.com/api/v1/lookup"
        )
        assert service.is_enabled is True


class TestOpenElevationServiceGetElevation(ResponseMockMixin):
    def test_it_does_not_call_open_elevation_api_when_no_url_set(
        self, app: "Flask"
    ) -> None:
        service = OpenElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response({}),
        ) as post_mock:
            service.get_elevations(POINTS_WITHOUT_ELEVATION)

        post_mock.assert_not_called()

    def test_it_calls_open_elevation_api_with_given_points(
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        service = OpenElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
        ) as post_mock:
            service.get_elevations(POINTS_WITHOUT_ELEVATION)

        post_mock.assert_called_once_with(
            service.url,
            json={
                "locations": [
                    {
                        "latitude": 44.68095,
                        "longitude": 6.07367,
                    },
                    {
                        "latitude": 44.68091,
                        "longitude": 6.07367,
                    },
                    {
                        "latitude": 44.6808,
                        "longitude": 6.07364,
                    },
                ]
            },
            timeout=30,
        )

    def test_it_returns_elevations(
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        service = OpenElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
        ):
            result = service.get_elevations(POINTS_WITHOUT_ELEVATION)

        assert result == OPEN_ELEVATION_RESPONSE["results"]

    def test_it_returns_empty_list_when_open_elevation_api_raises_exception(
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        service = OpenElevationService()

        with patch.object(
            requests,
            "post",
            side_effect=requests.exceptions.HTTPError,
        ):
            result = service.get_elevations(POINTS_WITHOUT_ELEVATION)

        assert result == []

    def test_it_logs_error_when_open_elevation_api_raises_exception(
        self,
        app_with_open_elevation_url: "Flask",
    ) -> None:
        service = OpenElevationService()

        with (
            patch(
                "fittrackee.workouts.services.elevation."
                "open_elevation_service.appLog"
            ) as logger_mock,
            patch.object(
                requests,
                "post",
                side_effect=requests.exceptions.HTTPError,
            ),
        ):
            service.get_elevations(POINTS_WITHOUT_ELEVATION)

        logger_mock.exception.assert_called_once_with(
            "Open Elevation API: error when getting missing elevations"
        )

    def test_it_returns_empty_list_when_number_of_elevation_returned_open_elevation_does_not_match(  # noqa
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        service = OpenElevationService()

        with patch.object(
            requests,
            "post",
            return_value=self.get_response(
                {"results": OPEN_ELEVATION_RESPONSE["results"][:-1]}
            ),
        ):
            result = service.get_elevations(POINTS_WITHOUT_ELEVATION)

        assert result == []

    def test_it_logs_error_when_number_of_elevation_returned_open_elevation_does_not_match(  # noqa
        self, app_with_open_elevation_url: "Flask"
    ) -> None:
        service = OpenElevationService()

        with (
            patch(
                "fittrackee.workouts.services.elevation."
                "open_elevation_service.appLog"
            ) as logger_mock,
            patch.object(
                requests,
                "post",
                return_value=self.get_response(
                    {"results": OPEN_ELEVATION_RESPONSE["results"][:-1]}
                ),
            ),
        ):
            service.get_elevations(POINTS_WITHOUT_ELEVATION)

        logger_mock.error.assert_called_once_with(
            "Open Elevation API: mismatch between number of points in "
            "results, ignoring results"
        )

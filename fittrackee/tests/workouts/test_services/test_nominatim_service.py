from typing import TYPE_CHECKING, List
from unittest.mock import patch

import requests

from fittrackee import VERSION
from fittrackee.workouts.geocode import NominatimService

from ...mixins import ResponseMockMixin

if TYPE_CHECKING:
    from flask import Flask


class TestNominatimServiceInstantiation:
    def test_it_instantiates_service_when_no_nominatim_url_set_in_env_var(
        self, app: "Flask"
    ) -> None:
        service = NominatimService()

        assert service.base_url == "https://nominatim.openstreetmap.org"
        assert service.params == {"format": "jsonv2"}
        assert service.headers == {"User-Agent": f"FitTrackee v{VERSION}"}

    def test_it_instantiates_service_when_nominatim_url_is_set_in_env_var(
        self, app_with_nominatim_url: "Flask"
    ) -> None:
        service = NominatimService()

        assert service.base_url == "https://nominatim.example.com"
        assert service.params == {"format": "jsonv2"}
        assert service.headers == {"User-Agent": f"FitTrackee v{VERSION}"}


class TestNominatimServiceGetLocationsFromQuery(ResponseMockMixin):
    def test_it_calls_nominatim_api_with_given_query(
        self, app: "Flask"
    ) -> None:
        service = NominatimService()
        query = "Paris"

        with patch.object(
            requests, "get", return_value=self.get_response([])
        ) as get_mock:
            service.get_locations_from_query(query)

        get_mock.assert_called_once_with(
            f"{service.base_url}/search",
            params={**service.params, "q": query},
            timeout=30,
            headers=service.headers,
        )

    def test_it_returns_location_data(
        self, app: "Flask", nominatim_response: List
    ) -> None:
        service = NominatimService()
        query = "Paris"

        with patch.object(
            requests, "get", return_value=self.get_response(nominatim_response)
        ):
            locations = service.get_locations_from_query(query)

        assert locations == [
            {
                "addresstype": "suburb",
                "coordinates": "48.8588897,2.3200410",
                "display_name": (
                    "Paris, Île-de-France, France métropolitaine, France"
                ),
                "name": "Paris",
            },
            {
                "addresstype": "town",
                "coordinates": "33.6617962,-95.5555130",
                "display_name": "Paris, Lamar County, Texas, United States",
                "name": "Paris",
            },
        ]

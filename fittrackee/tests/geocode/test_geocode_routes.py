import json
from typing import TYPE_CHECKING
from unittest.mock import patch

import requests
from requests import HTTPError

from ..mixins import ApiTestCaseMixin, ResponseMockMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


class GeocodeTestCase(ApiTestCaseMixin, ResponseMockMixin):
    route = ""

    def test_it_returns_401_when_user_is_not_authenticated(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client = app.test_client()

        response = client.get(self.route)

        self.assert_401(response)

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: "Flask",
        suspended_user: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            self.route, headers=dict(Authorization=f"Bearer {auth_token}")
        )

        self.assert_403(response)

    def test_expected_scope_is_geocode_read(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint=self.route,
            invalid_scope="workouts:read",
            expected_endpoint_scope="geocode:read",
        )


class TestGeocodeGetCoordinatesFromLocation(GeocodeTestCase):
    route = "/api/geocode/search"

    def test_it_returns_empty_list_when_no_city_provided(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.geocode.routes.nominatim_service.get_locations_from_city",
            return_value=[],
        ) as nominatim_service_mock:
            response = client.get(
                self.route,
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_not_called()
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["locations"] == []

    def test_it_returns_500_when_nominatim_api_returns_error(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch.object(requests, "get", side_effect=HTTPError()):
            response = client.get(
                f"{self.route}?city=Paris",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_500(
            response, "error when getting coordinates from location"
        )

    def test_it_calls_nominatim_api_with_language_when_provided(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        city = "Paris"
        language = "en"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.geocode.routes.nominatim_service.get_locations_from_city",
            return_value=[],
        ) as nominatim_service_mock:
            client.get(
                f"{self.route}?city={city}&language={language}",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_called_once_with(city.lower(), language)

    def test_it_returns_nominatim_api_response(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        city = "Paris"
        nominatim_service_response = [
            {
                "addresstype": "suburb",
                "coordinates": "48.8588897,2.3200410",
                "display_name": (
                    "Paris, Île-de-France, France métropolitaine, France"
                ),
                "name": "Paris",
                "osm_id": "r71525",
            },
        ]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.geocode.routes.nominatim_service.get_locations_from_city",
            return_value=nominatim_service_response,
        ) as nominatim_service_mock:
            response = client.get(
                f"{self.route}?city={city}",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_called_once_with(city.lower(), None)
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["locations"] == nominatim_service_response


class TestGeocodeGetLocationFromId(GeocodeTestCase):
    route = "/api/geocode/lookup"

    def test_it_returns_empty_dict_when_no_osm_id_provided(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.geocode.routes.nominatim_service.get_location_from_id",
            return_value=[],
        ) as nominatim_service_mock:
            response = client.get(
                self.route,
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_not_called()
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["location"] == {}

    def test_it_returns_500_when_nominatim_api_returns_error(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch.object(requests, "get", side_effect=HTTPError()):
            response = client.get(
                f"{self.route}?osm_id=r71525",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_500(response, "error when getting location from OSM id")

    def test_it_calls_nominatim_api_with_provided_language(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        osm_id = "R71525"
        language = "fr"

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.geocode.routes.nominatim_service.get_location_from_id",
            return_value=[],
        ) as nominatim_service_mock:
            client.get(
                f"{self.route}?osm_id={osm_id}&language={language}",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_called_once_with(
            osm_id.lower(), language
        )

    def test_it_returns_nominatim_api_response(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        osm_id = "R71525"
        nominatim_service_response = {
            "addresstype": "suburb",
            "coordinates": "48.8588897,2.3200410",
            "display_name": (
                "Paris, Île-de-France, France métropolitaine, France"
            ),
            "name": "Paris",
            "osm_id": "r71525",
        }
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.geocode.routes.nominatim_service.get_location_from_id",
            return_value=nominatim_service_response,
        ) as nominatim_service_mock:
            response = client.get(
                f"{self.route}?osm_id={osm_id}",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_called_once_with(osm_id.lower(), None)
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["location"] == nominatim_service_response

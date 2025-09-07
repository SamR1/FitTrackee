import json
from typing import TYPE_CHECKING
from unittest.mock import patch

from ..mixins import ApiTestCaseMixin, ResponseMockMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


class TestGeocodeGetCoordinatesFromLocation(
    ApiTestCaseMixin, ResponseMockMixin
):
    route = "/api/geocode/search"

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

    def test_it_returns_empty_list_when_not_query(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.workouts.geocode.nominatim_service.get_locations_from_query",
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

    def test_it_returns_nominatim_api_response(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        query = "Paris"
        nominatim_service_response = [
            {
                "addresstype": "suburb",
                "coordinates": "48.8588897,2.3200410",
                "display_name": (
                    "Paris, Île-de-France, France métropolitaine, France"
                ),
                "name": "Paris",
            },
        ]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.workouts.geocode.nominatim_service.get_locations_from_query",
            return_value=nominatim_service_response,
        ) as nominatim_service_mock:
            response = client.get(
                f"{self.route}?query={query}",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        nominatim_service_mock.assert_called_once_with(query)
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["locations"] == nominatim_service_response

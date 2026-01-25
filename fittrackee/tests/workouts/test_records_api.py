import json
from typing import TYPE_CHECKING, Dict, List, Set

import pytest

from fittrackee.constants import PaceSpeedDisplay

from ..mixins import ApiTestCaseMixin, WorkoutMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User, UserSportPreference
    from fittrackee.workouts.models import Sport, Workout


@pytest.mark.disable_autouse_update_records_patch
class TestGetRecords(ApiTestCaseMixin, WorkoutMixin):
    @staticmethod
    def assert_record_types(
        records: List[Dict], exported_record_types: Set
    ) -> None:
        assert len(records) == len(exported_record_types)
        assert {
            record["record_type"] for record in records
        } == exported_record_types

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
    ) -> None:
        client = app.test_client()

        response = client.get("/api/records")

        self.assert_401(response)

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: "Flask",
        suspended_user: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_records_type_when_sport_is_cycling(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_2: "Workout",
    ) -> None:
        self.update_workout_with_file_data(workout_cycling_user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        self.assert_record_types(
            data["data"]["records"], {"AS", "FD", "HA", "LD", "MS"}
        )
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["records"][0]["workout_date"]
        )
        assert "test" == data["data"]["records"][0]["user"]
        assert sport_1_cycling.id == data["data"]["records"][0]["sport_id"]
        assert (
            workout_cycling_user_1.short_id
            == data["data"]["records"][0]["workout_id"]
        )
        assert "AS" == data["data"]["records"][0]["record_type"]
        assert "value" in data["data"]["records"][0]

    def test_it_returns_records_type_when_sport_is_running(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_running_user_1: "Workout",
    ) -> None:
        self.update_workout_with_file_data(workout_running_user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        self.assert_record_types(
            data["data"]["records"], {"AP", "BP", "FD", "HA", "LD"}
        )

    @pytest.mark.parametrize(
        "input_pace_speed_display,expected_record_types",
        [
            (PaceSpeedDisplay.PACE, {"AP", "BP", "FD", "HA", "LD"}),
            (PaceSpeedDisplay.SPEED, {"AS", "FD", "HA", "LD", "MS"}),
            (
                PaceSpeedDisplay.PACE_AND_SPEED,
                {"AP", "AS", "BP", "FD", "HA", "LD", "MS"},
            ),
        ],
    )
    def test_it_returns_records_depending_on_user_preferences_when_sport_is_running(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_running_user_1: "Workout",
        user_1_sport_2_preference: "UserSportPreference",
        input_pace_speed_display: "PaceSpeedDisplay",
        expected_record_types: Set[str],
    ) -> None:
        user_1_sport_2_preference.pace_speed_display = input_pace_speed_display
        self.update_workout_with_file_data(workout_running_user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        self.assert_record_types(
            data["data"]["records"], expected_record_types
        )

    def test_it_returns_records_when_sport_is_outdoor_tennis(
        self,
        app: "Flask",
        user_1: "User",
        workout_outdoor_tennis_user_1_with_elevation_data: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["records"]) == 4
        self.assert_record_types(
            data["data"]["records"], {"AS", "FD", "LD", "MS"}
        )

    def test_it_gets_no_records_if_user_has_no_workout(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_2: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["records"]) == 0

    def test_it_gets_no_records_if_workout_has_zero_value(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            "/api/workouts/no_gpx",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=0,
                    workout_date="2018-05-14 14:05",
                    distance=0,
                    title="Workout test",
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["records"]) == 0

    def test_it_gets_records_for_several_sports(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        sport_4_paragliding: "Sport",
        sport_5_outdoor_tennis: "Sport",
        workout_cycling_user_1: "Workout",
        workout_running_user_1: "Workout",
        workout_paragliding_user_1: "Workout",
        workout_outdoor_tennis_user_1: "Workout",
        user_1_sport_2_preference: "UserSportPreference",
    ) -> None:
        self.update_workout_with_file_data(workout_cycling_user_1)
        self.update_workout_with_file_data(workout_running_user_1)
        self.update_workout_with_file_data(workout_paragliding_user_1)
        self.update_workout_with_file_data(workout_outdoor_tennis_user_1)
        user_1_sport_2_preference.pace_speed_display = (
            PaceSpeedDisplay.PACE_AND_SPEED
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/records",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["records"]) == 21

        # Cycling (Sport) records
        self.assert_record_types(
            data["data"]["records"][0:5], {"AS", "FD", "HA", "LD", "MS"}
        )
        # Running records
        self.assert_record_types(
            data["data"]["records"][5:12],
            {"AP", "AS", "BP", "FD", "HA", "LD", "MS"},
        )
        # Paragliding
        self.assert_record_types(
            data["data"]["records"][12:17], {"AS", "FD", "HA", "LD", "MS"}
        )
        # Outdoor tennis
        self.assert_record_types(
            data["data"]["records"][17:21], {"AS", "FD", "LD", "MS"}
        )

    def test_expected_scope_is_workouts_read(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1_admin,
            client_method="get",
            endpoint="/api/records",
            invalid_scope="workouts:write",
            expected_endpoint_scope="workouts:read",
        )

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel

from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import WorkoutApiTestCaseMixin
from .utils import MAX_WORKOUT_VALUES, post_a_workout

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import FollowRequest, User
    from fittrackee.workouts.models import Sport, Workout


class TestEditWorkout(WorkoutApiTestCaseMixin):
    def test_it_returns_401_when_no_authenticated(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1}",
            content_type="application/json",
            json={"sport_id": 2, "title": "Workout test"},
        )

        assert response.status_code == 401

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            data=json.dumps(dict(sport_id=2, title="Workout test")),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f"/api/workouts/{self.random_short_id()}",
            content_type="application/json",
            json={"sport_id": 2, "title": "Workout test"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility,expected_status_code",
        [
            ("workout visibility: private", VisibilityLevel.PRIVATE, 404),
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
                403,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_updating_workout_from_followed_user(
        self,
        input_desc: str,
        input_workout_visibility: "VisibilityLevel",
        expected_status_code: int,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        follow_request_from_user_2_to_user_1: "FollowRequest",
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"sport_id": 2, "title": "Workout test"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility,expected_status_code",
        [
            ("workout visibility: private", VisibilityLevel.PRIVATE, 404),
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
                404,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC, 403),
        ],
    )
    def test_returns_403_when_updating_workout_from_another_user(
        self,
        input_desc: str,
        input_workout_visibility: "VisibilityLevel",
        expected_status_code: int,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_2: "Workout",
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_2.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date="2018-05-15 15:05",
                    distance=8,
                    title="Workout test",
                )
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == expected_status_code

    def test_it_returns_400_if_payload_is_empty(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_raises_400_if_sport_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"sport_id": 2},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "sport id 2 not found", "invalid")

    @pytest.mark.parametrize(
        "input_attribute", ["description", "notes", "title"]
    )
    def test_it_updates_value_with_special_characters_for_a_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        input_attribute: str,
    ) -> None:
        content = "test \nworkout ©"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={input_attribute: content},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0][input_attribute] == content

    def test_it_adds_equipment(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"equipment_ids": [equipment_bike_user_1.short_id]},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"][0]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]

    def test_it_updates_equipments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_running_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
        equipment_another_shoes_user_1: "Equipment",
    ) -> None:
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_running_user_1.short_id}",
            content_type="application/json",
            json={"equipment_ids": [equipment_another_shoes_user_1.short_id]},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["equipments"] == [
            jsonify_dict(
                equipment_another_shoes_user_1.serialize(current_user=user_1)
            )
        ]
        assert equipment_another_shoes_user_1.total_workouts == 1
        assert (
            equipment_another_shoes_user_1.total_distance
            == workout_running_user_1.distance
        )
        assert (
            equipment_another_shoes_user_1.total_duration
            == workout_running_user_1.duration
        )
        assert (
            equipment_another_shoes_user_1.total_moving
            == workout_running_user_1.moving
        )

    def test_it_returns_400_when_equipment_ids_are_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
        equipment_bike_user_1: "Equipment",
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"equipment_ids": equipment_bike_user_1.short_id},
            headers=dict(Authorization=f"Bearer {token}"),
        )

        self.assert_400(
            response,
            "equipment_ids must be an array of strings",
        )

    def test_it_returns_400_when_multiple_equipments_are_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_2_running: "Sport",
        gpx_file: str,
        equipment_shoes_user_1: "Equipment",
        equipment_another_shoes_user_1: "Equipment",
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)

        client = app.test_client()
        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                    equipment_another_shoes_user_1.short_id,
                ]
            },
            headers=dict(Authorization=f"Bearer {token}"),
        )

        self.assert_400(response, "only one equipment can be added")

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            json={"title": "some title"},
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestEditWorkoutWithGpx(WorkoutApiTestCaseMixin):
    def test_it_returns_400_if_payload_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"distance": 10},
            headers=dict(Authorization=f"Bearer {token}"),
        )

        self.assert_400(
            response,
            "invalid key ('distance') for workout with gpx",
            "invalid",
        )

    def test_it_updates_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"sport_id": 2, "title": "Workout test"},
            headers=dict(Authorization=f"Bearer {token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert sport_2_running.id == data["data"]["workouts"][0]["sport_id"]
        assert data["data"]["workouts"][0]["title"] == "Workout test"
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Tue, 13 Mar 2018 12:44:45 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_1.serialize()
        )
        assert "0:04:10" == data["data"]["workouts"][0]["duration"]
        assert data["data"]["workouts"][0]["ascent"] == 0.4
        assert data["data"]["workouts"][0]["ave_speed"] == 4.61
        assert data["data"]["workouts"][0]["descent"] == 23.4
        assert data["data"]["workouts"][0]["description"] is None
        assert data["data"]["workouts"][0]["distance"] == 0.32
        assert data["data"]["workouts"][0]["max_alt"] == 998.0
        assert data["data"]["workouts"][0]["max_speed"] == 5.12
        assert data["data"]["workouts"][0]["min_alt"] == 975.0
        assert data["data"]["workouts"][0]["moving"] == "0:04:10"
        assert data["data"]["workouts"][0]["pauses"] is None
        assert data["data"]["workouts"][0]["with_gpx"] is True

        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 5
        assert records[0]["sport_id"] == sport_2_running.id
        assert records[0]["workout_id"] == data["data"]["workouts"][0]["id"]
        assert records[0]["record_type"] == "AS"
        assert records[0]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[0]["value"] == 4.61
        assert records[1]["sport_id"] == sport_2_running.id
        assert records[1]["workout_id"] == data["data"]["workouts"][0]["id"]
        assert records[1]["record_type"] == "FD"
        assert records[1]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[1]["value"] == 0.32
        assert records[2]["sport_id"] == sport_2_running.id
        assert records[2]["workout_id"] == data["data"]["workouts"][0]["id"]
        assert records[2]["record_type"] == "HA"
        assert records[2]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[2]["value"] == 0.4
        assert records[3]["sport_id"] == sport_2_running.id
        assert records[3]["workout_id"] == data["data"]["workouts"][0]["id"]
        assert records[3]["record_type"] == "LD"
        assert records[3]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[3]["value"] == "0:04:10"
        assert records[4]["sport_id"] == sport_2_running.id
        assert records[4]["workout_id"] == data["data"]["workouts"][0]["id"]
        assert records[4]["record_type"] == "MS"
        assert records[4]["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[4]["value"] == 5.12

    @pytest.mark.parametrize(
        "input_description,input_workout_visibility",
        [
            ("private", VisibilityLevel.PRIVATE),
            ("followers_only", VisibilityLevel.FOLLOWERS),
            ("public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_updates_workout_visibility_for_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        input_description: str,
        input_workout_visibility: "VisibilityLevel",
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"workout_visibility": input_workout_visibility.value},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["workout_visibility"]
            == input_workout_visibility.value
        )

    @pytest.mark.parametrize(
        "input_description,input_analysis_visibility",
        [
            ("private", VisibilityLevel.PRIVATE),
            ("followers_only", VisibilityLevel.FOLLOWERS),
            ("public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_updates_analysis_visibility_for_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        input_description: str,
        input_analysis_visibility: "VisibilityLevel",
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"analysis_visibility": input_analysis_visibility.value},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["analysis_visibility"]
            == input_analysis_visibility.value
        )
        assert (
            workout_cycling_user_1.analysis_visibility.value
            == input_analysis_visibility.value
        )

    @pytest.mark.parametrize(
        "input_description,input_map_visibility",
        [
            ("private", VisibilityLevel.PRIVATE),
            ("followers_only", VisibilityLevel.FOLLOWERS),
            ("public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_updates_map_visibility_for_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        input_description: str,
        input_map_visibility: "VisibilityLevel",
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"map_visibility": input_map_visibility.value},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["map_visibility"]
            == input_map_visibility.value
        )
        assert (
            workout_cycling_user_1.map_visibility.value
            == input_map_visibility.value
        )


class TestEditWorkoutWithoutGpx(WorkoutApiTestCaseMixin):
    def test_it_updates_a_workout_wo_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={
                "sport_id": 2,
                "duration": 3600,
                "workout_date": "2018-05-15 15:05",
                "distance": 8,
                "title": "Workout test",
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            data["data"]["workouts"][0]["workout_date"]
            == "Tue, 15 May 2018 15:05:00 GMT"
        )
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_1.serialize()
        )
        assert data["data"]["workouts"][0]["sport_id"] == sport_2_running.id
        assert data["data"]["workouts"][0]["duration"] == "1:00:00"
        assert data["data"]["workouts"][0]["title"] == "Workout test"
        assert data["data"]["workouts"][0]["ascent"] is None
        assert data["data"]["workouts"][0]["ave_speed"] == 8.0
        assert data["data"]["workouts"][0]["descent"] is None
        assert data["data"]["workouts"][0]["description"] is None
        assert data["data"]["workouts"][0]["distance"] == 8.0
        assert data["data"]["workouts"][0]["max_alt"] is None
        assert data["data"]["workouts"][0]["max_speed"] == 8.0
        assert data["data"]["workouts"][0]["min_alt"] is None
        assert data["data"]["workouts"][0]["moving"] == "1:00:00"
        assert data["data"]["workouts"][0]["pauses"] is None
        assert data["data"]["workouts"][0]["with_gpx"] is False
        assert data["data"]["workouts"][0]["map"] is None
        assert data["data"]["workouts"][0]["weather_start"] is None
        assert data["data"]["workouts"][0]["weather_end"] is None
        assert data["data"]["workouts"][0]["notes"] is None

        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 4
        assert records[0]["sport_id"] == sport_2_running.id
        assert records[0]["workout_id"] == workout_short_id
        assert records[0]["record_type"] == "AS"
        assert records[0]["workout_date"] == "Tue, 15 May 2018 15:05:00 GMT"
        assert records[0]["value"] == 8.0
        assert records[1]["sport_id"] == sport_2_running.id
        assert records[1]["workout_id"] == workout_short_id
        assert records[1]["record_type"] == "FD"
        assert records[1]["workout_date"] == "Tue, 15 May 2018 15:05:00 GMT"
        assert records[1]["value"] == 8.0
        assert records[2]["sport_id"] == sport_2_running.id
        assert records[2]["workout_id"] == workout_short_id
        assert records[2]["record_type"] == "LD"
        assert records[2]["workout_date"] == "Tue, 15 May 2018 15:05:00 GMT"
        assert records[2]["value"] == "1:00:00"
        assert records[3]["sport_id"] == sport_2_running.id
        assert records[3]["workout_id"] == workout_short_id
        assert records[3]["record_type"] == "MS"
        assert records[3]["workout_date"] == "Tue, 15 May 2018 15:05:00 GMT"
        assert records[3]["value"] == 8.0

    def test_it_updates_ascent_and_descent_values(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        ascent = 10
        descent = 0

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"ascent": ascent, "descent": descent},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["ascent"] == ascent
        assert data["data"]["workouts"][0]["descent"] == descent

        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 5
        assert records[0]["sport_id"] == sport_1_cycling.id
        assert records[0]["workout_id"] == workout_short_id
        assert records[0]["record_type"] == "AS"
        assert records[0]["workout_date"] == "Mon, 01 Jan 2018 00:00:00 GMT"
        assert records[0]["value"] == 10.0
        assert records[1]["sport_id"] == sport_1_cycling.id
        assert records[1]["workout_id"] == workout_short_id
        assert records[1]["record_type"] == "FD"
        assert records[1]["workout_date"] == "Mon, 01 Jan 2018 00:00:00 GMT"
        assert records[1]["value"] == 10.0
        assert records[2]["sport_id"] == sport_1_cycling.id
        assert records[2]["workout_id"] == workout_short_id
        assert records[2]["record_type"] == "HA"
        assert records[2]["workout_date"] == "Mon, 01 Jan 2018 00:00:00 GMT"
        assert records[2]["value"] == ascent
        assert records[3]["sport_id"] == sport_1_cycling.id
        assert records[3]["workout_id"] == workout_short_id
        assert records[3]["record_type"] == "LD"
        assert records[3]["workout_date"] == "Mon, 01 Jan 2018 00:00:00 GMT"
        assert records[3]["value"] == "1:00:00"
        assert records[4]["sport_id"] == sport_1_cycling.id
        assert records[4]["workout_id"] == workout_short_id
        assert records[4]["record_type"] == "MS"
        assert records[4]["workout_date"] == "Mon, 01 Jan 2018 00:00:00 GMT"
        assert records[4]["value"] == 10.0

    def test_it_empties_ascent_and_descent_values(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_1.ascent = 100
        workout_cycling_user_1.descent = 150

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"ascent": None, "descent": None},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["ascent"] is None
        assert data["data"]["workouts"][0]["descent"] is None
        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 4
        assert "HA" not in [record["record_type"] for record in records]

    def test_it_returns_400_if_payload_is_empty(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            data=json.dumps(dict()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response)

    def test_it_returns_error_when_workout_value_exceeds_max_value(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        data = {"distance": MAX_WORKOUT_VALUES["distance"] + 0.001}

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json=data,
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            error_message=(
                "one or more values, entered or calculated, exceed the limits"
            ),
        )

    def test_it_returns_500_if_date_format_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"workout_date": "15/2018"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response)

    def test_it_returns_400_if_ascent_or_descent_are_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={"ascent": None, "descent": 100},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid ascent or descent", "invalid")

    def test_it_returns_400_when_values_are_invalid_for_workout_without_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            json={
                "analysis_visibility": VisibilityLevel.FOLLOWERS,
                "map_visibility": VisibilityLevel.FOLLOWERS,
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            (
                "invalid keys ('analysis_visibility', 'map_visibility') "
                "for workout without gpx"
            ),
            "invalid",
        )

    def test_it_updates_workout_visibility_for_workout_without_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            content_type="application/json",
            data=json.dumps(
                dict(workout_visibility=VisibilityLevel.FOLLOWERS)
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["workout_visibility"]
            == VisibilityLevel.FOLLOWERS
        )
        assert (
            data["data"]["workouts"][0]["analysis_visibility"]
            == VisibilityLevel.PRIVATE.value
        )
        assert (
            data["data"]["workouts"][0]["map_visibility"]
            == VisibilityLevel.PRIVATE.value
        )

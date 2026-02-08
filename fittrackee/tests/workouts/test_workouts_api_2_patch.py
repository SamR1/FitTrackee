import json
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from fittrackee import db
from fittrackee.constants import ElevationDataSource
from fittrackee.equipments.models import Equipment
from fittrackee.tests.fixtures.fixtures_workouts import VALHALLA_VALUES
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import WorkoutSegment
from fittrackee.workouts.services.elevation.elevation_service import (
    ElevationService,
)
from fittrackee.workouts.services.elevation.valhalla_elevation_service import (
    ValhallaElevationService,
)
from fittrackee.workouts.services.workouts_from_file_refresh_service import (
    WorkoutFromFileRefreshService,
)

from ..utils import jsonify_dict
from .mixins import WorkoutApiTestCaseMixin
from .utils import MAX_WORKOUT_VALUES, create_a_workout_with_file

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
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout.short_id}",
            content_type="application/json",
            json={"equipment_ids": equipment_bike_user_1.short_id},
            headers=dict(Authorization=f"Bearer {auth_token}"),
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
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout.short_id}",
            content_type="application/json",
            json={
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                    equipment_another_shoes_user_1.short_id,
                ]
            },
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "only one equipment can be added")

    def test_expected_scope_is_workouts_write(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="patch",
            endpoint=f"/api/workouts/{self.random_short_id()}",
            invalid_scope="workouts:read",
            expected_endpoint_scope="workouts:write",
        )


class TestEditWorkoutWithFile(WorkoutApiTestCaseMixin):
    def test_it_returns_400_if_payload_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout.short_id}",
            content_type="application/json",
            json={"distance": 10},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            "invalid key ('distance') for workout with file",
            "invalid",
        )

    def test_it_updates_title_for_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch.object(
            WorkoutFromFileRefreshService, "refresh"
        ) as refresh_mock:
            response = client.patch(
                f"/api/workouts/{workout.short_id}",
                content_type="application/json",
                json={"title": "Workout test"},
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        refresh_mock.assert_not_called()
        db.session.refresh(workout)
        assert workout.title == "Workout test"
        segment = WorkoutSegment.query.filter_by(workout_id=workout.id).one()
        assert segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["sport_id"] == sport_1_cycling.id
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
        assert data["data"]["workouts"][0]["with_file"] is True

        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 5
        for record in records:
            assert record["sport_id"] == sport_1_cycling.id
            assert record["workout_id"] == data["data"]["workouts"][0]["id"]
            assert record["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[0]["record_type"] == "AS"
        assert records[0]["value"] == 4.61
        assert records[1]["record_type"] == "FD"
        assert records[1]["value"] == 0.32
        assert records[2]["record_type"] == "HA"
        assert records[2]["value"] == 0.4
        assert records[3]["record_type"] == "LD"
        assert records[3]["value"] == "0:04:10"
        assert records[4]["record_type"] == "MS"
        assert records[4]["value"] == 5.12

    def test_it_updates_sport_and_refreshes_workout(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_5_outdoor_tennis: "Sport",
        gpx_file: str,
    ) -> None:
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout.short_id}",
            content_type="application/json",
            json={"sport_id": sport_5_outdoor_tennis.id},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        db.session.refresh(workout)
        assert workout.sport_id == sport_5_outdoor_tennis.id
        segment = WorkoutSegment.query.filter_by(workout_id=workout.id).one()
        assert segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": None,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["sport_id"]
            == sport_5_outdoor_tennis.id
        )
        assert data["data"]["workouts"][0]["title"] == "just a workout"
        assert "creation_date" in data["data"]["workouts"][0]
        assert (
            "Tue, 13 Mar 2018 12:44:45 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_1.serialize()
        )
        assert "0:04:10" == data["data"]["workouts"][0]["duration"]
        assert data["data"]["workouts"][0]["ascent"] is None
        assert data["data"]["workouts"][0]["ave_pace"] is None
        assert data["data"]["workouts"][0]["ave_speed"] == 4.57
        assert data["data"]["workouts"][0]["best_pace"] is None
        assert data["data"]["workouts"][0]["descent"] is None
        assert data["data"]["workouts"][0]["description"] is None
        assert data["data"]["workouts"][0]["distance"] == 0.317
        assert data["data"]["workouts"][0]["max_alt"] is None
        assert data["data"]["workouts"][0]["max_speed"] == 5.1
        assert data["data"]["workouts"][0]["min_alt"] is None
        assert data["data"]["workouts"][0]["moving"] == "0:04:10"
        assert data["data"]["workouts"][0]["pauses"] is None
        assert data["data"]["workouts"][0]["with_file"] is True

        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 4
        for record in records:
            assert record["sport_id"] == sport_5_outdoor_tennis.id
            assert record["workout_id"] == data["data"]["workouts"][0]["id"]
            assert record["workout_date"] == "Tue, 13 Mar 2018 12:44:45 GMT"
        assert records[0]["record_type"] == "AS"
        assert records[0]["value"] == 4.57
        assert records[1]["record_type"] == "FD"
        assert records[1]["value"] == 0.317
        assert records[2]["record_type"] == "LD"
        assert records[2]["value"] == "0:04:10"
        assert records[3]["record_type"] == "MS"
        assert records[3]["value"] == 5.1

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
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1.original_file = "file.gpx"
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

    @pytest.mark.parametrize(
        "input_elevation_data_source", ["invalid", "valhalla"]
    )
    def test_it_returns_400_when_elevation_data_source_is_invalid(
        self,
        app_with_open_elevation_url: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
        input_elevation_data_source: str,
    ) -> None:
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_open_elevation_url, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout.short_id}",
            content_type="application/json",
            json={"elevation_data_source": input_elevation_data_source},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            f"'{input_elevation_data_source}' as elevation "
            f"data source is not valid",
        )

    def test_it_updates_elevation_data_source_from_elevation_service(
        self,
        app_with_valhalla_url: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        workout = create_a_workout_with_file(user_1, gpx_file)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_valhalla_url, user_1.email
        )

        with (
            patch.object(
                ValhallaElevationService,
                "get_elevations",
                return_value=VALHALLA_VALUES,
            ) as get_elevations_mock,
        ):
            response = client.patch(
                f"/api/workouts/{workout.short_id}",
                content_type="application/json",
                json={"elevation_data_source": "valhalla"},
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_elevations_mock.assert_called_once()
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["elevation_data_source"] == "valhalla"
        )

    def test_it_updates_elevation_data_source_from_file(
        self,
        app_with_valhalla_url: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
    ) -> None:
        workout = create_a_workout_with_file(user_1, gpx_file)
        workout.elevation_data_source = ElevationDataSource.VALHALLA
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_valhalla_url, user_1.email
        )
        with (
            patch.object(
                ElevationService, "get_elevations", return_value=[]
            ) as get_elevations_mock,
        ):
            response = client.patch(
                f"/api/workouts/{workout.short_id}",
                content_type="application/json",
                json={"elevation_data_source": "file"},
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_elevations_mock.assert_not_called()
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["elevation_data_source"] == "file"


class TestEditWorkoutWithoutFile(WorkoutApiTestCaseMixin):
    def test_it_updates_a_workout_without_file(
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

        with patch.object(
            WorkoutFromFileRefreshService, "refresh"
        ) as refresh_mock:
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

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.duration == timedelta(seconds=3600)
        assert workout_cycling_user_1.distance == 8
        assert workout_cycling_user_1.ave_speed == 8.0
        assert workout_cycling_user_1.max_speed == 8.0
        assert workout_cycling_user_1.ave_pace == timedelta(
            minutes=7, seconds=30
        )
        assert workout_cycling_user_1.best_pace == timedelta(
            minutes=7, seconds=30
        )
        refresh_mock.assert_not_called()
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
        assert data["data"]["workouts"][0]["ave_pace"] == "0:07:30"
        assert data["data"]["workouts"][0]["ave_speed"] is None
        assert data["data"]["workouts"][0]["best_pace"] == "0:07:30"
        assert data["data"]["workouts"][0]["descent"] is None
        assert data["data"]["workouts"][0]["description"] is None
        assert data["data"]["workouts"][0]["distance"] == 8.0
        assert data["data"]["workouts"][0]["max_alt"] is None
        assert data["data"]["workouts"][0]["max_speed"] is None
        assert data["data"]["workouts"][0]["min_alt"] is None
        assert data["data"]["workouts"][0]["moving"] == "1:00:00"
        assert data["data"]["workouts"][0]["pauses"] is None
        assert data["data"]["workouts"][0]["with_file"] is False
        assert data["data"]["workouts"][0]["map"] is None
        assert data["data"]["workouts"][0]["weather_start"] is None
        assert data["data"]["workouts"][0]["weather_end"] is None
        assert data["data"]["workouts"][0]["notes"] is None

        records = data["data"]["workouts"][0]["records"]
        assert len(records) == 4
        for record in records:
            assert record["sport_id"] == sport_2_running.id
            assert record["workout_id"] == workout_short_id
            assert record["workout_date"] == "Tue, 15 May 2018 15:05:00 GMT"
        assert records[0]["record_type"] == "AP"
        assert records[0]["value"] == "0:07:30"
        assert records[1]["record_type"] == "BP"
        assert records[1]["value"] == "0:07:30"
        assert records[2]["record_type"] == "FD"
        assert records[2]["value"] == 8.0
        assert records[3]["record_type"] == "LD"
        assert records[3]["value"] == "1:00:00"

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

    def test_it_updates_calories(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        calories = 650
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"calories": calories},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["calories"] == calories

    def test_it_empties_calories(
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
        workout_cycling_user_1.calories = 650

        response = client.patch(
            f"/api/workouts/{workout_short_id}",
            content_type="application/json",
            json={"calories": None},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["calories"] is None

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

    def test_it_returns_400_when_values_are_invalid_for_workout_without_file(
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
                "for workout without file"
            ),
            "invalid",
        )

    def test_it_updates_workout_visibility_for_workout_without_file(
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

    def test_it_returns_400_when_elevation_data_source_is_provided(
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
            json={"elevation_data_source": "file"},
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            "'elevation_data_source' can not be provided "
            "for workout without file",
        )

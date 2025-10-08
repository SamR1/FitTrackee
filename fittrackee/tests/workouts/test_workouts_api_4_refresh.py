import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import mock_open, patch

import pytest

from fittrackee import db
from fittrackee.visibility_levels import VisibilityLevel

from ..utils import jsonify_dict
from .mixins import WorkoutApiTestCaseMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import FollowRequest, User
    from fittrackee.workouts.models import Sport, Workout


class TestRefreshWorkout(WorkoutApiTestCaseMixin):
    def test_it_returns_404_when_workout_not_found(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/workouts/{self.random_short_id()}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_401_when_user_is_not_authenticated(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client = app.test_client()

        response = client.delete(
            f"/api/workouts/{workout_cycling_user_1.short_id}"
        )

        self.assert_401(response)

    def test_it_returns_404_when_workout_does_not_belong_to_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f"/api/workouts/{workout_cycling_user_1.short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

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
    def test_it_returns_403_when_refresh_workout_from_followed_user_user(
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

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/refresh",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == expected_status_code

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/refresh",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_error_when_workout_has_no_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/workouts/{workout_cycling_user_1.short_id}/refresh",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "workout without original file")

    def test_it_refreshes_workout_with_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        gpx_file: str,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        open_mock = mock_open(read_data=gpx_file)

        with patch("builtins.open", open_mock):
            response = client.post(
                f"/api/workouts/{workout_cycling_user_1.short_id}/refresh",
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        db.session.refresh(workout_cycling_user_1)
        assert response.status_code == 200
        assert float(workout_cycling_user_1.distance) == 0.32  # type: ignore
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(
                workout_cycling_user_1.serialize(user=user_1, light=False)
            )
        ]

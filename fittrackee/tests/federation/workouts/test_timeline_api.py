import json

import pytest
from flask import Flask
from werkzeug.test import TestResponse

from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ...mixins import ApiTestCaseMixin


class TestFederationGetUserTimeline(ApiTestCaseMixin):
    @staticmethod
    def assert_no_workout_returned(response: TestResponse) -> None:
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 0

    @staticmethod
    def assert_workout_returned(
        response: TestResponse, workout: Workout
    ) -> None:
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["id"] == workout.short_id

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            ("workout visibility: private", VisibilityLevel.PRIVATE),
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            (
                "workout visibility: followers_and_remote_only",
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_authenticated_user_workout(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_workout_returned(response, workout_cycling_user_1)

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            (
                "workout visibility: followers_and_remote_only",
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout_when_visibility_allows_it(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_workout_returned(response, workout_cycling_user_2)

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout visibility: private", VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_does_return_workout_if_visibility_does_not_allow_it(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_workout_returned(response)

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            (
                "map visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("map visibility: private", VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_does_not_return_followed_user_workout_map_when_privacy_does_not_allow_it(  # noqa
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.map_visibility = input_map_visibility
        workout_cycling_user_2.map_id = self.random_string()
        workout_cycling_user_2.map = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert data["data"]["workouts"][0]["map"] is None

    @pytest.mark.parametrize(
        "input_desc,input_visibility",
        [
            (
                "workout, analysis and map visibility: "
                "followers_and_remote_only",
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
            (
                "workout, analysis and map visibility: public",
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_it_returns_followed_user_workout_map_when_visibility_allows_it(
        self,
        input_desc: str,
        input_visibility: VisibilityLevel,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_visibility
        workout_cycling_user_2.analysis_visibility = input_visibility
        workout_cycling_user_2.map_visibility = input_visibility
        map_id = self.random_string()
        workout_cycling_user_2.map_id = map_id
        workout_cycling_user_2.map = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert data["data"]["workouts"][0]["map"] == map_id

import json
from datetime import datetime, timezone
from typing import List

import pytest
from flask import Flask
from werkzeug.test import TestResponse

from fittrackee import db
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import WorkoutApiTestCaseMixin


class GetUserTimelineTestCase(WorkoutApiTestCaseMixin):
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


class TestGetUserTimeline(GetUserTimelineTestCase):
    def test_it_returns_401_if_no_authentication(self, app: Flask) -> None:
        client = app.test_client()

        response = client.get("/api/timeline")

        assert response.status_code == 401

    def test_it_returns_403_when_user_is_suspended(
        self, app: Flask, suspended_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_empty_list_when_no_workouts(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_workout_returned(response)

    def test_it_gets_minimal_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user=user_1)
        )

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self, app: Flask, user_1: User, client_scope: str, can_access: bool
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            "/api/timeline",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestGetUserTimelineForAuthUserWorkouts(GetUserTimelineTestCase):
    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            ("workout visibility: private", VisibilityLevel.PRIVATE),
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_authenticated_user_workout(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_workout_returned(response, workout_cycling_user_1)

    def test_it_returns_authenticated_user_suspended_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_workout_returned(response, workout_cycling_user_1)


class TestGetUserTimelineForFollowedUserWorkouts(GetUserTimelineTestCase):
    def test_it_does_not_return_followed_user_private_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_workout_returned(response)

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout_when_visibility_allows_it(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_does_not_return_workout_from_blocked_user(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        user_1.blocks_user(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_workout_returned(response)

    def test_blocked_user_can_not_get_workout_in_timeline(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        user_2.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_workout_returned(response)

    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_does_not_return_followed_user_suspended_workouts(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        user_1.blocks_user(user_2)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_does_not_return_followed_user_workout_map_when_private(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        workout_cycling_user_2.map_visibility = VisibilityLevel.PRIVATE
        workout_cycling_user_2.map_id = self.random_string()
        workout_cycling_user_2.map = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
                "workout and map visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout and map visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout_map_when_visibility_allows_it(
        self,
        input_desc: str,
        input_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_visibility
        workout_cycling_user_2.analysis_visibility = input_visibility
        workout_cycling_user_2.map_visibility = input_visibility
        map_id = self.random_string()
        workout_cycling_user_2.map_id = map_id
        workout_cycling_user_2.map = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert data["data"]["workouts"][0]["map"] == map_id


class TestGetUserTimelineForNotFollowedUserWorkouts(GetUserTimelineTestCase):
    @pytest.mark.parametrize(
        "input_desc,input_workout_visibility",
        [
            (
                "workout visibility: private",
                VisibilityLevel.PRIVATE,
            ),
            (
                "workout visibility: followers_only",
                VisibilityLevel.FOLLOWERS,
            ),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_does_not_return_workout(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_no_workout_returned(response)


class TestGetUserTimelinePagination(WorkoutApiTestCaseMixin):
    def test_it_returns_pagination_when_no_workouts(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_pagination_when_one_workout_returned(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_gets_first_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert len(data["data"]["workouts"]) == 5
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_second_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert len(data["data"]["workouts"]) == 2
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 7,
        }

    def test_it_gets_empty_third_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline?page=3",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert len(data["data"]["workouts"]) == 0
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 3,
            "pages": 2,
            "total": 7,
        }

    def test_it_returns_workouts_ordered_by_workout_date_descending(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/timeline",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert (
            "Wed, 09 May 2018 00:00:00 GMT"
            == data["data"]["workouts"][0]["workout_date"]
        )
        assert (
            "Mon, 01 Jan 2018 00:00:00 GMT"
            == data["data"]["workouts"][4]["workout_date"]
        )

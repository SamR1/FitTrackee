import json
import re
from datetime import datetime, timezone
from typing import List
from unittest.mock import mock_open, patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

from ..mixins import GeometryMixin
from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import WorkoutApiTestCaseMixin
from .utils import post_a_workout


class GetWorkoutGpxAsFollowerMixin:
    @staticmethod
    def init_test_data_for_follower(
        workout: Workout,
        *,
        analysis_visibility: VisibilityLevel = VisibilityLevel.FOLLOWERS,
        map_visibility: VisibilityLevel,
        follower: User,
        followed: User,
    ) -> None:
        workout.gpx = "file.gpx"
        workout.workout_visibility = analysis_visibility
        workout.analysis_visibility = analysis_visibility
        workout.map_visibility = map_visibility
        followed.approves_follow_request_from(follower)


class GetWorkoutGpxPublicVisibilityMixin:
    @staticmethod
    def init_test_data_for_public_workout(
        workout: Workout,
        *,
        analysis_visibility: VisibilityLevel = VisibilityLevel.PUBLIC,
        map_visibility: VisibilityLevel,
    ) -> None:
        workout.gpx = "file.gpx"
        workout.workout_visibility = analysis_visibility
        workout.analysis_visibility = VisibilityLevel.PUBLIC
        workout.map_visibility = map_visibility


class GetWorkoutTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}"


class TestGetWorkoutAsWorkoutOwner(GetWorkoutTestCase):
    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_gets_owner_workout(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user=user_1, light=False)
        )

    def test_it_gets_owner_suspended_workout(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user=user_1, light=False)
        )


class TestGetWorkoutAsFollower(CommentMixin, GetWorkoutTestCase):
    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_404_when_workout_is_suspended_and_no_user_comments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_404_when_workout_is_suspended_and_auth_user_commented_workout(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0] == jsonify_dict(
            workout_cycling_user_2.serialize(user=user_1)
        )

    @pytest.mark.parametrize(
        "input_desc,input_workout_level",
        [
            ("workout visibility: follower", VisibilityLevel.FOLLOWERS),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout(
        self,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_2.serialize()
        )
        assert (
            data["data"]["workouts"][0]["map_visibility"]
            == VisibilityLevel.PRIVATE.value
        )
        assert (
            data["data"]["workouts"][0]["workout_visibility"]
            == input_workout_level
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutAsUser(CommentMixin, GetWorkoutTestCase):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_404_when_workout_is_suspended_and_no_user_comments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_404_when_workout_is_suspended_and_auth_user_commented_workout(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0] == jsonify_dict(
            workout_cycling_user_2.serialize(user=user_1)
        )

    @pytest.mark.parametrize(
        "input_desc,input_workout_level",
        [
            ("workout visibility: private", VisibilityLevel.PRIVATE),
            ("workout visibility: follower", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_404_when_user_is_blocked_workout_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        user_2.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_another_user_workout_when_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_2.serialize()
        )
        assert (
            data["data"]["workouts"][0]["map_visibility"]
            == VisibilityLevel.PRIVATE.value
        )
        assert (
            data["data"]["workouts"][0]["analysis_visibility"]
            == VisibilityLevel.PRIVATE.value
        )
        assert (
            data["data"]["workouts"][0]["workout_visibility"]
            == VisibilityLevel.PUBLIC.value
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutAsUnauthenticatedUser(GetWorkoutTestCase):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=short_id),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_404_when_workout_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    @pytest.mark.parametrize(
        "input_desc,input_workout_level",
        [
            ("workout visibility: private", VisibilityLevel.PRIVATE),
            ("workout visibility: follower", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_level
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        data = self.assert_404(response)
        assert len(data["data"]["workouts"]) == 0

    def test_it_returns_a_user_workout_when_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert data["data"]["workouts"][0]["user"] == jsonify_dict(
            user_1.serialize()
        )
        assert (
            data["data"]["workouts"][0]["map_visibility"]
            == VisibilityLevel.PRIVATE.value
        )
        assert (
            data["data"]["workouts"][0]["analysis_visibility"]
            == VisibilityLevel.PRIVATE.value
        )
        assert (
            data["data"]["workouts"][0]["workout_visibility"]
            == VisibilityLevel.PUBLIC.value
        )


class GetWorkoutGpxTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/gpx"


class TestGetWorkoutGpxAsWorkoutOwner(GetWorkoutGpxTestCase):
    def test_it_returns_404_if_workout_have_no_gpx(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert (
            "no gpx file for this workout (id: "
            f"{workout_cycling_user_1.short_id})"
        ) in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
        workout_cycling_user_1.gpx = "file.gpx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)

    def test_it_returns_owner_workout_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        gpx_file_with_gpxtpx_extensions: str,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == gpx_file_with_gpxtpx_extensions


class TestGetWorkoutGpxAsFollower(
    GetWorkoutGpxTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_1,
            followed=user_2,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=self.random_string(),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
            ("map visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout_gpx(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        gpx_file_with_gpxtpx_extensions: str,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            map_visibility=input_map_visibility,
            follower=user_1,
            followed=user_2,
        )
        user_2.hr_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == gpx_file_with_gpxtpx_extensions

    def test_it_does_not_return_heart_rate(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        gpx_file_with_gpxtpx_extensions: str,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            map_visibility=VisibilityLevel.FOLLOWERS,
            follower=user_1,
            followed=user_2,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == re.sub(
            r"<(.*):hr>([\r\n\d]*)</(.*):hr>",
            "",
            gpx_file_with_gpxtpx_extensions,
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            map_visibility=VisibilityLevel.FOLLOWERS,
            follower=user_1,
            followed=user_2,
        )
        gpx_content = self.random_string()
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)


class TestGetWorkoutGpxAsUser(
    GetWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert f"workout not found (id: {random_short_id})" in data["message"]
        assert data["data"]["gpx"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: private", VisibilityLevel.PRIVATE),
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2, map_visibility=input_map_visibility
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=self.random_string(),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        gpx_file_with_ns3_extensions: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2, map_visibility=VisibilityLevel.PUBLIC
        )
        user_2.hr_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_ns3_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == gpx_file_with_ns3_extensions

    def test_it_does_not_return_heart_rate(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        gpx_file_with_ns3_extensions: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2, map_visibility=VisibilityLevel.PUBLIC
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_ns3_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == re.sub(
            r"<(.*):hr>([\r\n\d]*)</(.*):hr>",
            "",
            gpx_file_with_ns3_extensions,
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2, map_visibility=VisibilityLevel.PUBLIC
        )
        gpx_content = self.random_string()
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)


class TestGetWorkoutGpxAsUnauthenticatedUser(
    GetWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["gpx"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: private", VisibilityLevel.PRIVATE),
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
        )
        client = app.test_client()
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=self.random_string(),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        gpx_file_with_ns3_extensions: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        user_1.hr_visibility = VisibilityLevel.PUBLIC
        client = app.test_client()
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_ns3_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == gpx_file_with_ns3_extensions

    def test_it_does_not_return_heart_rate(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        gpx_file_with_ns3_extensions: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client = app.test_client()
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_ns3_extensions,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["gpx"] == re.sub(
            r"<(.*):hr>([\r\n\d]*)</(.*):hr>",
            "",
            gpx_file_with_ns3_extensions,
        )


class GetWorkoutGeoJSONTestCase(WorkoutApiTestCaseMixin, GeometryMixin):
    route = "/api/workouts/{workout_uuid}/geojson"


class TestGetWorkoutGeoJsonAsWorkoutOwner(GetWorkoutGeoJSONTestCase):
    def test_it_returns_404_if_workout_have_no_gpx(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert (
            "no gpx file for this workout (id: "
            f"{workout_cycling_user_1.short_id})"
        ) in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
        workout_cycling_user_1.gpx = "file.gpx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)

    def test_it_returns_owner_workout_geojson(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]

        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_with_coordinates.geom
        )

    def test_it_returns_none_when_no_coordinates(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]

        assert data["data"]["geojson"] is None


class TestGetWorkoutGeoJsonAsFollower(
    GetWorkoutGeoJSONTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
            ("map visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout_gpx(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            map_visibility=input_map_visibility,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_with_coordinates.geom
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            map_visibility=VisibilityLevel.FOLLOWERS,
            follower=user_2,
            followed=user_1,
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutGeoJsonAsUser(
    GetWorkoutGeoJSONTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert f"workout not found (id: {random_short_id})" in data["message"]
        assert data["data"]["geojson"] is None

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: private", VisibilityLevel.PRIVATE),
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    def test_it_returns_geojson_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_with_coordinates.geom
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutGeoJsonAsUnauthenticatedUser(
    GetWorkoutGeoJSONTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["geojson"] is None

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: private", VisibilityLevel.PRIVATE),
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
        )
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_with_coordinates.geom
        )


class GetWorkoutChartDataTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/chart_data"


class TestGetWorkoutChartDataAsWorkoutOwner(GetWorkoutChartDataTestCase):
    def test_it_returns_404_if_workout_have_no_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert "not found" in data["status"]
        assert (
            f"no gpx file for this workout (id: {workout_short_id})"
            in data["message"]
        )

    def test_it_returns_500_if_a_workout_has_invalid_gpx_pathname(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response)

    def test_it_calls_get_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_1.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_chart_data_mock.assert_called_once_with(
            get_absolute_file_path(workout_cycling_user_1.gpx),
            sport_1_cycling.label,
            workout_cycling_user_1.ave_cadence,
            can_see_heart_rate=True,
            segment_id=None,
        )

    def test_it_returns_owner_workout_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_1.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data

    def test_it_returns_chart_data_when_cadence_zero_values(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_with_cadence_zero_values: str,
    ) -> None:
        auth_token, workout_short_id = post_a_workout(
            app, gpx_file_with_cadence_zero_values
        )
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        # cadence key is not present
        assert data["data"]["chart_data"][0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "hr": 92,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "power": 0,
            "speed": 3.21,
            "time": "Tue, 13 Mar 2018 12:44:45 GMT",
        }

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutChartDataAsFollower(
    GetWorkoutChartDataTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_analysis_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            analysis_visibility=VisibilityLevel.PRIVATE,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_1,
            followed=user_2,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    @pytest.mark.parametrize(
        "input_desc,input_analysis_visibility",
        [
            ("analysis visibility: followers_only", VisibilityLevel.FOLLOWERS),
            ("analysis visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_chart_data_when_visibility_to_follower(
        self,
        input_desc: str,
        input_analysis_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_1,
            followed=user_2,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_2.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data

    @pytest.mark.parametrize(
        "input_hr_visibility,expected_can_see_heart_rate",
        [
            (VisibilityLevel.FOLLOWERS, True),
            (VisibilityLevel.PRIVATE, False),
        ],
    )
    def test_it_calls_get_chart_data_when_user_can_not_see_heart_rate(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        input_hr_visibility: VisibilityLevel,
        expected_can_see_heart_rate: bool,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PUBLIC,
            follower=user_1,
            followed=user_2,
        )
        user_2.hr_visibility = input_hr_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_2.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_chart_data_mock.assert_called_once_with(
            get_absolute_file_path(workout_cycling_user_2.gpx),
            sport_1_cycling.label,
            workout_cycling_user_2.ave_cadence,
            can_see_heart_rate=expected_can_see_heart_rate,
            segment_id=None,
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.gpx = "file.gpx"
        self.init_test_data_for_follower(
            workout_cycling_user_2,
            analysis_visibility=VisibilityLevel.FOLLOWERS,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_1,
            followed=user_2,
        )
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutChartDataAsUser(
    GetWorkoutChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["chart_data"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_analysis_visibility",
        [
            ("analysis visibility: private", VisibilityLevel.PRIVATE),
            ("analysis visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_analysis_visibility_is_not_public(
        self,
        input_desc: str,
        input_analysis_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )

    @pytest.mark.parametrize(
        "input_hr_visibility,expected_can_see_heart_rate",
        [
            (VisibilityLevel.PUBLIC, True),
            (VisibilityLevel.FOLLOWERS, False),
        ],
    )
    def test_it_calls_get_chart_data_when_user_can_not_see_heart_rate(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_hr_visibility: VisibilityLevel,
        expected_can_see_heart_rate: bool,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.analysis_visibility = VisibilityLevel.PUBLIC
        user_2.hr_visibility = input_hr_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_2.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_chart_data_mock.assert_called_once_with(
            get_absolute_file_path(workout_cycling_user_2.gpx),
            sport_1_cycling.label,
            workout_cycling_user_2.ave_cadence,
            can_see_heart_rate=expected_can_see_heart_rate,
            segment_id=None,
        )

    def test_it_returns_chart_data_when_analysis_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_2.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_2.gpx = "file.gpx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutChartDataAsUnauthenticatedUser(
    GetWorkoutChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["chart_data"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_analysis_visibility",
        [
            ("analysis visibility: private", VisibilityLevel.PRIVATE),
            ("analysis visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_analysis_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    @pytest.mark.parametrize(
        "input_hr_visibility,expected_can_see_heart_rate",
        [
            (VisibilityLevel.PUBLIC, True),
            (VisibilityLevel.FOLLOWERS, False),
        ],
    )
    def test_it_calls_get_chart_data_when_user_can_not_see_heart_rate(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_hr_visibility: VisibilityLevel,
        expected_can_see_heart_rate: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        user_1.hr_visibility = input_hr_visibility
        client = app.test_client()
        workout_cycling_user_1.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(workout_uuid=workout_cycling_user_1.short_id)
            )

        get_chart_data_mock.assert_called_once_with(
            get_absolute_file_path(workout_cycling_user_1.gpx),
            sport_1_cycling.label,
            workout_cycling_user_1.ave_cadence,
            can_see_heart_rate=expected_can_see_heart_rate,
            segment_id=None,
        )

    def test_it_returns_chart_data_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        chart_data: List = []
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client = app.test_client()
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data


class GetWorkoutSegmentGpxTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/gpx/segment/{segment_id}"


class TestGetWorkoutSegmentGpxAsWorkoutOwner(GetWorkoutSegmentGpxTestCase):
    def test_it_returns_404_if_workout_have_no_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"no gpx file for this workout (id: {workout_short_id})"
        )

    def test_it_returns_404_if_segment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id,
                    segment_id=100,
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_404_with_message(response, "No segment with id '100'")

    def test_it_gets_segment_gpx_for_owner_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert '<trkpt lat="44.68095" lon="6.07367">' in data["data"]["gpx"]

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutSegmentGpxAsFollower(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        data = self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )
        assert data["data"]["gpx"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
            ("map visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_segment_gpx_for_followed_user_workout(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            map_visibility=input_map_visibility,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert '<trkpt lat="44.68095" lon="6.07367">' in data["data"]["gpx"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            map_visibility=VisibilityLevel.FOLLOWERS,
            follower=user_2,
            followed=user_1,
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)


class TestGetWorkoutSegmentGpxAsUser(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["gpx"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: private", VisibilityLevel.PRIVATE),
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    def test_it_returns_segment_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert '<trkpt lat="44.68095" lon="6.07367">' in data["data"]["gpx"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutSegmentGpxAsUnauthenticatedUser(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["gpx"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_map_visibility",
        [
            ("map visibility: private", VisibilityLevel.PRIVATE),
            ("map visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
        )
        client = app.test_client()
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
            )

        data = self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )
        assert data["data"]["gpx"] == ""

    def test_it_returns_segment_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client = app.test_client()
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert '<trkpt lat="44.68095" lon="6.07367">' in data["data"]["gpx"]


class GetWorkoutSegmentChartDataTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/chart_data/segment/{segment_id}"


class TestGetWorkoutSegmentChartDataAsWorkoutOwner(
    GetWorkoutSegmentChartDataTestCase
):
    def test_it_returns_404_if_workout_have_no_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_short_id, segment_id=1),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"no gpx file for this workout (id: {workout_short_id})"
        )

    def test_it_returns_500_if_workout_has_invalid_gpx_pathname(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response)

    def test_it_returns_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_1.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutSegmentChartDataAsFollower(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_analysis_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            analysis_visibility=VisibilityLevel.PRIVATE,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    @pytest.mark.parametrize(
        "input_desc,input_analysis_visibility",
        [
            ("analysis visibility: followers_only", VisibilityLevel.FOLLOWERS),
            ("analysis visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_chart_data_for_follower_user_workout(
        self,
        input_desc: str,
        input_analysis_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        chart_data: List = []
        workout_cycling_user_1.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        self.init_test_data_for_follower(
            workout_cycling_user_1,
            analysis_visibility=VisibilityLevel.FOLLOWERS,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_2,
            followed=user_1,
        )
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        chart_data: List = []

        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)


class TestGetWorkoutSegmentChartDataAsUser(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["chart_data"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_analysis_visibility",
        [
            ("analysis visibility: private", VisibilityLevel.PRIVATE),
            ("analysis visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_analysis_visibility_is_not_public(
        self,
        input_desc: str,
        input_analysis_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    def test_it_returns_chart_data_when_analysis_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        chart_data: List = []
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        workout_cycling_user_1.gpx = "file.gpx"
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        chart_data: List = []
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        workout_cycling_user_1.gpx = "file.gpx"
        user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)


class TestGetWorkoutSegmentChartDataAsUnauthenticatedUser(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
        )

        data = self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )
        assert data["data"]["chart_data"] == ""

    @pytest.mark.parametrize(
        "input_desc,input_analysis_visibility",
        [
            ("analysis visibility: private", VisibilityLevel.PRIVATE),
            ("analysis visibility: followers_only", VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_analysis_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_1.short_id})",
        )

    def test_it_returns_chart_data_when_analysis_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        chart_data: List = []
        self.init_test_data_for_public_workout(
            workout_cycling_user_1,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client = app.test_client()
        with (
            patch("builtins.open", new_callable=mock_open),
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=chart_data,
            ),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["chart_data"] == chart_data


class TestGetWorkoutMap(WorkoutApiTestCaseMixin):
    def test_it_returns_404_if_workout_has_no_map(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            f"/api/workouts/map/{self.random_string()}",
        )

        self.assert_404_with_message(response, "Map does not exist")

    def test_it_calls_send_from_directory_if_workout_has_map(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        map_id = self.random_string()
        map_file_path = self.random_string()
        workout_cycling_user_1.map_id = map_id
        workout_cycling_user_1.map = map_file_path
        client = app.test_client()
        with patch(
            "fittrackee.workouts.workouts.send_from_directory",
            return_value="file",
        ) as mock:
            response = client.get(
                f"/api/workouts/map/{map_id}",
            )

        assert response.status_code == 200
        mock.assert_called_once_with(
            app.config["UPLOAD_FOLDER"], map_file_path
        )

    def test_it_returns_404_if_map_file_not_found(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        map_ip = self.random_string()
        workout_cycling_user_1.map = self.random_string()
        workout_cycling_user_1.map_id = map_ip
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts/map/{map_ip}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "Map file does not exist")


class TestWorkoutScope(WorkoutApiTestCaseMixin):
    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/workouts/{workout_short_id}",
            "/api/workouts/{workout_short_id}/gpx",
            "/api/workouts/{workout_short_id}/chart_data",
            "/api/workouts/{workout_short_id}/gpx/segment/1",
            "/api/workouts/{workout_short_id}/chart_data/segment/1",
        ],
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        client_scope: str,
        can_access: bool,
        endpoint: str,
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
            endpoint.format(workout_short_id=workout_cycling_user_1.short_id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class DownloadWorkoutGpxTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/gpx/download"


class TestDownloadWorkoutGpxAsWorkoutOwner(DownloadWorkoutGpxTestCase):
    def test_it_returns_404_if_workout_does_not_have_gpx(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no gpx file for workout")

    def test_it_calls_send_from_directory_if_workout_has_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_file_path = "file.gpx"
        workout_cycling_user_1.gpx = "file.gpx"
        with patch(
            "fittrackee.workouts.workouts.send_from_directory",
            return_value="file",
        ) as mock:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        mock.assert_called_once_with(
            app.config["UPLOAD_FOLDER"],
            gpx_file_path,
            mimetype="application/gpx+xml",
            as_attachment=True,
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
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

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestDownloadWorkoutGpxAsFollower(DownloadWorkoutGpxTestCase):
    def test_it_returns_404_for_followed_user_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.gpx = "file.gpx"
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.map_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )


class TestDownloadWorkoutGpxAsUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )

    def test_it_returns_404_for_another_user_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2, map_visibility=VisibilityLevel.PUBLIC
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )


class TestDownloadWorkoutGpxAsUnauthenticatedUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        self.assert_401(response)


class DownloadWorkoutOriginalFileTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/original/download"


class TestDownloadWorkoutOriginalFileAsWorkoutOwner(
    DownloadWorkoutOriginalFileTestCase
):
    def test_it_returns_404_if_workout_does_not_have_original_file(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no original file for workout")

    @pytest.mark.parametrize(
        "input_extension,expected_mimetype",
        [
            ("gpx", "application/gpx+xml"),
            ("kml", "application/vnd.google-earth.kml+xml"),
            ("tcx", "application/vnd.garmin.tcx+xml"),
            ("fit", "application/vnd.ant.fit"),
        ],
    )
    def test_it_calls_send_from_directory_if_workout_has_original_file(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_extension: str,
        expected_mimetype: str,
    ) -> None:
        workout_cycling_user_1.original_file = f"file.{input_extension}"
        with patch(
            "fittrackee.workouts.workouts.send_from_directory",
            return_value="file",
        ) as mock:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        mock.assert_called_once_with(
            app.config["UPLOAD_FOLDER"],
            workout_cycling_user_1.original_file,
            mimetype=expected_mimetype,
            as_attachment=True,
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.original_file = "file.tcx"
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
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

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestDownloadWorkoutOriginalFileAsFollower(
    DownloadWorkoutOriginalFileTestCase
):
    def test_it_returns_404_for_followed_user_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.gpx = "file.tcx"
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.map_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )


class TestDownloadWorkoutOriginalFileAsUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response, f"workout not found (id: {random_short_id})"
        )

    def test_it_returns_404_for_another_user_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_2, map_visibility=VisibilityLevel.PUBLIC
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {workout_cycling_user_2.short_id})",
        )


class TestDownloadWorkoutOriginalFileAsUnauthenticatedUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=VisibilityLevel.PUBLIC
        )
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        self.assert_401(response)

import json
from datetime import datetime, timezone
from typing import Dict, List
from unittest.mock import mock_open, patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

from ..mixins import GeometryMixin
from ..utils import jsonify_dict
from .mixins import WorkoutApiTestCaseMixin


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
        workout.original_file = "file.gpx"
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
        workout.original_file = "file.gpx"
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


class TestGetWorkoutGpx(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/gpx"

    def test_it_returns_410(
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

        assert response.status_code == 410


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
            f"no file for this workout (id: {workout_cycling_user_1.short_id})"
        ) in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1_with_coordinates.original_file = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]

        assert data["data"][
            "geojson"
        ] == self.get_multilinestring_geojson_from_geom(
            [workout_cycling_user_1_segment_0_with_coordinates.geom]
        )

    def test_it_returns_404_when_no_coordinates(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1.original_file = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "geojson not found")


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
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1_with_coordinates,
            map_visibility=input_map_visibility,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"][
            "geojson"
        ] == self.get_multilinestring_geojson_from_geom(
            [workout_cycling_user_1_segment_0_with_coordinates.geom]
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            map_visibility=VisibilityLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"][
            "geojson"
        ] == self.get_multilinestring_geojson_from_geom(
            [workout_cycling_user_1_segment_0_with_coordinates.geom]
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            map_visibility=VisibilityLevel.PUBLIC,
        )
        client = app.test_client()

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"][
            "geojson"
        ] == self.get_multilinestring_geojson_from_geom(
            [workout_cycling_user_1_segment_0_with_coordinates.geom]
        )


class GetWorkoutSegmentGeoJSONTestCase(WorkoutApiTestCaseMixin, GeometryMixin):
    route = "/api/workouts/{workout_uuid}/geojson/segment/{segment_id}"


class TestGetWorkoutSegmentGeoJsonAsWorkoutOwner(
    GetWorkoutSegmentGeoJSONTestCase
):
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
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert "not found" in data["status"]
        assert (
            f"no file for this workout (id: {workout_cycling_user_1.short_id})"
        ) in data["message"]

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
        workout_cycling_user_1.original_file = "file.gpx"
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
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_403(response)

    def test_it_returns_owner_workout_geojson(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1_with_coordinates.original_file = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id,
                segment_id=1,
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]

        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_0_with_coordinates.geom
        )

    def test_it_returns_error_when_no_coordinates(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1.original_file = "file.gpx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "geojson not found")


class TestGetWorkoutSegmentGeoJsonAsFollower(
    GetWorkoutSegmentGeoJSONTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1_with_coordinates,
            map_visibility=input_map_visibility,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id,
                segment_id=1,
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_0_with_coordinates.geom
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)


class TestGetWorkoutSegmentGeoJsonAsUser(
    GetWorkoutSegmentGeoJSONTestCase, GetWorkoutGpxPublicVisibilityMixin
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
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
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

    def test_it_returns_geojson_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            map_visibility=VisibilityLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id,
                segment_id=1,
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_0_with_coordinates.geom
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
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


class TestGetWorkoutSegmentGeoJsonAsUnauthenticatedUser(
    GetWorkoutSegmentGeoJSONTestCase, GetWorkoutGpxPublicVisibilityMixin
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
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1, map_visibility=input_map_visibility
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

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            map_visibility=VisibilityLevel.PUBLIC,
        )
        client = app.test_client()

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id,
                segment_id=1,
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["geojson"] == self.get_geojson_from_geom(
            workout_cycling_user_1_segment_0_with_coordinates.geom
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
        # workout created without file
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
            f"no file for this workout (id: {workout_short_id})"
            in data["message"]
        )

    def test_it_returns_owner_workout_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_0_chart_data: List[Dict],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert (
            data["data"]["chart_data"]
            == workout_cycling_user_1_segment_0_chart_data
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_0_chart_data_wo_hr: List[Dict],
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1_with_coordinates,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
            follower=user_2,
            followed=user_1,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert (
            data["data"]["chart_data"]
            == workout_cycling_user_1_segment_0_chart_data_wo_hr
        )

    @pytest.mark.parametrize(
        "input_hr_visibility,expected_can_see_heart_rate",
        [
            (VisibilityLevel.FOLLOWERS, True),
            (VisibilityLevel.PRIVATE, False),
        ],
    )
    def test_it_calls_get_chart_data_from_gpx_when_user_can_not_see_heart_rate(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_hr_visibility: VisibilityLevel,
        expected_can_see_heart_rate: bool,
    ) -> None:
        self.init_test_data_for_follower(
            workout_cycling_user_1_with_coordinates,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PUBLIC,
            follower=user_2,
            followed=user_1,
        )
        user_1.hr_visibility = input_hr_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        with (
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1_with_coordinates.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_chart_data_mock.assert_called_once_with(
            workout_cycling_user_1_with_coordinates,
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
        workout_cycling_user_2.original_file = "file.gpx"
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(
            response,
            "workout not found (id: "
            f"{workout_cycling_user_1_with_coordinates.short_id})",
        )

    @pytest.mark.parametrize(
        "input_hr_visibility,expected_can_see_heart_rate",
        [
            (VisibilityLevel.PUBLIC, True),
            (VisibilityLevel.FOLLOWERS, False),
        ],
    )
    def test_it_calls_get_chart_data_from_gpx_when_user_can_not_see_heart_rate(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        input_hr_visibility: VisibilityLevel,
        expected_can_see_heart_rate: bool,
    ) -> None:
        workout_cycling_user_1_with_coordinates.workout_visibility = (
            VisibilityLevel.PUBLIC
        )
        workout_cycling_user_1_with_coordinates.analysis_visibility = (
            VisibilityLevel.PUBLIC
        )
        user_1.hr_visibility = input_hr_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        with (
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1_with_coordinates.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        get_chart_data_mock.assert_called_once_with(
            workout_cycling_user_1_with_coordinates,
            can_see_heart_rate=expected_can_see_heart_rate,
            segment_id=None,
        )

    def test_it_returns_chart_data_when_analysis_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_0_chart_data: List[Dict],
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert (
            data["data"]["chart_data"]
            == workout_cycling_user_1_segment_0_chart_data
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
            workout_cycling_user_2,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_2.original_file = "file.gpx"
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
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            analysis_visibility=input_analysis_visibility,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
        )

        self.assert_404_with_message(
            response,
            "workout not found (id: "
            f"{workout_cycling_user_1_with_coordinates.short_id})",
        )

    @pytest.mark.parametrize(
        "input_hr_visibility,expected_can_see_heart_rate",
        [
            (VisibilityLevel.PUBLIC, True),
            (VisibilityLevel.FOLLOWERS, False),
        ],
    )
    def test_it_calls_get_chart_data_from_gpx_when_user_can_not_see_heart_rate(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        input_hr_visibility: VisibilityLevel,
        expected_can_see_heart_rate: bool,
    ) -> None:
        workout_cycling_user_1_with_coordinates.workout_visibility = (
            VisibilityLevel.PUBLIC
        )
        workout_cycling_user_1_with_coordinates.analysis_visibility = (
            VisibilityLevel.PUBLIC
        )
        user_1.hr_visibility = input_hr_visibility
        client = app.test_client()

        with (
            patch(
                "fittrackee.workouts.workouts.get_chart_data",
                return_value=[],
            ) as get_chart_data_mock,
        ):
            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1_with_coordinates.short_id
                )
            )

        get_chart_data_mock.assert_called_once_with(
            workout_cycling_user_1_with_coordinates,
            can_see_heart_rate=expected_can_see_heart_rate,
            segment_id=None,
        )

    def test_it_returns_chart_data_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1_with_coordinates: Workout,
        workout_cycling_user_1_segment_0_with_coordinates: WorkoutSegment,
        workout_cycling_user_1_segment_0_chart_data_wo_hr: List[Dict],
    ) -> None:
        self.init_test_data_for_public_workout(
            workout_cycling_user_1_with_coordinates,
            analysis_visibility=VisibilityLevel.PUBLIC,
            map_visibility=VisibilityLevel.PRIVATE,
        )
        client = app.test_client()

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1_with_coordinates.short_id
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert (
            data["data"]["chart_data"]
            == workout_cycling_user_1_segment_0_chart_data_wo_hr
        )


class TestGetWorkoutSegmentGpx(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/gpx/segment/{segment_id}"

    def test_it_returns_410(
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
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )
        assert response.status_code == 410

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.original_file = "file.gpx"
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
            response, f"no file for this workout (id: {workout_short_id})"
        )

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
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1.original_file = "file.gpx"
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
        workout_cycling_user_1.original_file = "file.gpx"
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
        "endpoint",
        [
            "/api/workouts/{workout_short_id}",
            "/api/workouts/{workout_short_id}/gpx",
            "/api/workouts/{workout_short_id}/chart_data",
            "/api/workouts/{workout_short_id}/gpx/segment/1",
            "/api/workouts/{workout_short_id}/chart_data/segment/1",
        ],
    )
    def test_expected_scope_is_workouts_read(
        self, app: Flask, user_1: User, endpoint: str
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint=endpoint.format(workout_short_id=self.random_short_id()),
            invalid_scope="workouts:write",
            expected_endpoint_scope="workouts:read",
        )


class DownloadWorkoutGpxTestCase(WorkoutApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/gpx/download"


class TestDownloadWorkoutGpxAsWorkoutOwner(DownloadWorkoutGpxTestCase):
    def test_it_returns_404_if_workout_does_not_have_file(
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

    def test_it_returns_500_if_workout_has_no_segments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.original_file = "file.tcx"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "No segments")

    def test_it_calls_send_from_directory_if_original_file_is_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_file_path = "file.gpx"
        workout_cycling_user_1.original_file = gpx_file_path
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

    def test_it_calls_generate_gpx_if_original_file_is_not_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        gpx_file: str,
    ) -> None:
        tcx_file_path = "file.tcx"
        workout_cycling_user_1.original_file = tcx_file_path
        with patch(
            "fittrackee.workouts.workouts.generate_gpx",
            return_value=gpx_file,
        ) as mock:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        mock.assert_called_once_with(workout_cycling_user_1)
        assert response.status_code == 200
        assert response.mimetype == "application/gpx+xml"
        assert (
            response.headers["Content-Disposition"]
            == "attachment; filename=file.gpx"
        )
        assert response.data.decode() == gpx_file

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.original_file = "file.gpx"
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

    def test_expected_scope_is_workouts_read(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint=self.route.format(workout_uuid=self.random_short_id()),
            invalid_scope="workouts:write",
            expected_endpoint_scope="workouts:read",
        )


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
        workout_cycling_user_2.original_file = "file.gpx"
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
    def test_it_returns_401_when_user_is_not_authenticated(
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
            ("kmz", "application/vnd.google-earth.kmz"),
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

    def test_expected_scope_is_workouts_read(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint=self.route.format(workout_uuid=self.random_short_id()),
            invalid_scope="workouts:write",
            expected_endpoint_scope="workouts:read",
        )


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
        workout_cycling_user_2.original_file = "file.tcx"
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

import json
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestWorkoutLikePost(ApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/like"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id)
        )

        self.assert_401(response)

    def test_it_return_error_when_user_is_suspended(
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

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_when_workout_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    @pytest.mark.parametrize(
        "input_desc,input_workout_level",
        [
            ("workout visibility: follower", VisibilityLevel.FOLLOWERS),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_creates_workout_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(
                workout_cycling_user_2.serialize(user=user_1, light=False)
            )
        ]
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is not None
        )
        assert workout_cycling_user_2.likes.all() == [user_1]

    def test_it_does_not_return_error_when_like_already_exists(
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
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        )
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["id"]
            == workout_cycling_user_2.short_id
        )
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is not None
        )
        assert workout_cycling_user_2.likes.all() == [user_1]

    def test_expected_scope_is_workouts_write(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="post",
            endpoint=self.route.format(workout_uuid=self.random_short_id()),
            invalid_scope="workouts:read",
            expected_endpoint_scope="workouts:write",
        )


class TestWorkoutUndoLikePost(ApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/like/undo"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id)
        )

        self.assert_401(response)

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        )
        db.session.add(like)
        db.session.flush()
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    @pytest.mark.parametrize(
        "input_desc,input_workout_level",
        [
            ("workout visibility: follower", VisibilityLevel.FOLLOWERS),
            ("workout visibility: public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_removes_workout_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        )
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["workouts"] == [
            jsonify_dict(
                workout_cycling_user_2.serialize(user=user_1, light=False)
            )
        ]
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is None
        )
        assert workout_cycling_user_2.likes.all() == []

    def test_it_does_not_return_error_when_no_existing_like(
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

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["workouts"]) == 1
        assert (
            data["data"]["workouts"][0]["id"]
            == workout_cycling_user_2.short_id
        )
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is None
        )
        assert workout_cycling_user_2.likes.all() == []

    def test_expected_scope_is_workouts_write(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="post",
            endpoint=self.route.format(workout_uuid=self.random_short_id()),
            invalid_scope="workouts:read",
            expected_endpoint_scope="workouts:write",
        )


class TestWorkoutLikesGet(ApiTestCaseMixin):
    route = "/api/workouts/{workout_uuid}/likes"

    def test_it_return_error_when_user_is_suspended(
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

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_it_returns_empty_list_when_no_likes(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_1.id,
            workout_id=workout_cycling_user_1.id,
        )
        db.session.add(like)
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
        assert data["data"]["likes"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    @patch("fittrackee.workouts.workouts.DEFAULT_WORKOUT_LIKES_PER_PAGE", 2)
    def test_it_returns_users_who_like_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        for user in [user_2, user_3, user_4]:
            like = WorkoutLike(
                user_id=user.id,
                workout_id=workout_cycling_user_1.id,
            )
            db.session.add(like)
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
        assert data["data"]["likes"] == [
            jsonify_dict(user_4.serialize(current_user=user_1)),
            jsonify_dict(user_3.serialize(current_user=user_1)),
        ]
        assert data["pagination"] == {
            "has_next": True,
            "has_prev": False,
            "page": 1,
            "pages": 2,
            "total": 3,
        }

    @patch("fittrackee.workouts.workouts.DEFAULT_WORKOUT_LIKES_PER_PAGE", 2)
    def test_it_returns_page_2(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        for user in [user_2, user_3, user_4]:
            like = WorkoutLike(
                user_id=user.id,
                workout_id=workout_cycling_user_1.id,
            )
            db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_uuid = workout_cycling_user_1.short_id

        response = client.get(
            f"{self.route.format(workout_uuid=workout_uuid)}?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["likes"] == [
            jsonify_dict(user_2.serialize(current_user=user_1))
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 3,
        }

    def test_it_returns_like_when_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id,
            workout_id=workout_cycling_user_1.id,
        )
        db.session.add(like)
        db.session.commit()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["likes"] == [jsonify_dict(user_2.serialize())]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_expected_scope_is_workout_read(
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

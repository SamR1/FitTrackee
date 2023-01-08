import json

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from ...mixins import ApiTestCaseMixin, BaseTestMixin
from ...utils import jsonify_dict
from ...workouts.utils import WorkoutCommentMixin


class TestPostWorkoutComment(ApiTestCaseMixin, BaseTestMixin):
    @pytest.mark.parametrize(
        'input_workout_visibility',
        [
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_returns_404_when_user_can_not_access_workout(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        remote_cycling_workout.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f"/api/workouts/{remote_cycling_workout.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {remote_cycling_workout.short_id})",
        )

    def test_it_returns_404_when_follower_can_not_access_workout(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = PrivacyLevel.PRIVATE
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f"/api/workouts/{remote_cycling_workout.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=self.random_string(),
                    text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout not found (id: {remote_cycling_workout.short_id})",
        )

    def test_it_returns_201_when_comment_is_created(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment_text = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f"/api/workouts/{remote_cycling_workout.short_id}/comments",
            content_type="application/json",
            data=json.dumps(
                dict(
                    text=comment_text,
                    text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
                )
            ),
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        new_comment = WorkoutComment.query.filter_by(
            user_id=user_1.id, workout_id=remote_cycling_workout.id
        ).first()
        assert data['comment'] == jsonify_dict(new_comment.serialize(user_1))


class TestGetWorkoutCommentAsUser(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {workout_comment.short_id})",
        )


class TestGetWorkoutCommentAsFollower(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        user_1.send_follow_request_to(user_3)
        user_3.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(
            workout_comment.serialize(user_1)
        )


class TestGetWorkoutCommentAsRemoteFollower(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        user_1.send_follow_request_to(remote_user)
        remote_user.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            remote_user,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(
            workout_comment.serialize(user_1)
        )


class TestGetWorkoutCommentAsOwner(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_comment_when_visibility_allows_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
            headers=dict(
                Authorization=f"Bearer {auth_token}",
            ),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['comment'] == jsonify_dict(
            workout_comment.serialize(user_1)
        )


class TestGetWorkoutCommentAsUnauthenticatedUser(
    WorkoutCommentMixin, ApiTestCaseMixin, BaseTestMixin
):
    def test_it_returns_404_when_comment_visibility_does_not_allow_access(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        client = app_with_federation.test_client()

        response = client.get(
            f"/api/workouts/{workout_cycling_user_2.short_id}/"
            f"comments/{workout_comment.short_id}",
            content_type="application/json",
        )

        self.assert_404_with_message(
            response,
            f"workout comment not found (id: {workout_comment.short_id})",
        )

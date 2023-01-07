import json

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from ...mixins import ApiTestCaseMixin, BaseTestMixin
from ...utils import jsonify_dict


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

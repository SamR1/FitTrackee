from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.tests.utils import generate_follow_request
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ...mixins import ApiTestCaseMixin


@patch('fittrackee.workouts.workouts.send_to_remote_inbox')
class TestFederationDeleteWorkout(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        'workout_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_does_not_call_sent_to_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        workout_visibility: VisibilityLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'workout_visibility',
        [
            VisibilityLevel.FOLLOWERS_AND_REMOTE,
            VisibilityLevel.PUBLIC,
        ],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_fittrackee_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        workout_visibility: VisibilityLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        delete_workout_activity, _ = workout_cycling_user_1.get_activities(
            activity_type='Delete'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=delete_workout_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'workout_visibility',
        [
            VisibilityLevel.FOLLOWERS_AND_REMOTE,
            VisibilityLevel.PUBLIC,
        ],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_other_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        workout_visibility: VisibilityLevel,
    ) -> None:
        generate_follow_request(remote_user_2, user_1)
        user_1.approves_follow_request_from(remote_user_2)
        workout_cycling_user_1.workout_visibility = workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        _, delete_note_activity = workout_cycling_user_1.get_activities(
            activity_type='Delete'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=delete_note_activity,
            recipients=[remote_user_2.actor.shared_inbox_url],
        )

import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ...mixins import ApiTestCaseMixin


@patch('fittrackee.workouts.workouts.send_to_remote_inbox')
class TestFederationUpdateWorkout(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        'workout_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_does_not_call_sent_to_inbox_when_visibility_does_not_change_for_local_workouts(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'workout_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_fittrackee_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    title=self.random_string(),
                    workout_visibility=workout_visibility.value,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        update_workout_activity, _ = workout_cycling_user_1.get_activities(
            activity_type='Update'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=update_workout_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'old_workout_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    @pytest.mark.parametrize(
        'new_workout_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS],
    )
    def test_it_calls_sent_to_inbox_with_delete_activity_when_workout_is_not_visible_anymore_on_remote(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        old_workout_visibility: PrivacyLevel,
        new_workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = old_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        delete_workout_activity, _ = workout_cycling_user_1.get_activities(
            activity_type='Delete'
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    title=self.random_string(),
                    workout_visibility=new_workout_visibility.value,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=delete_workout_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'old_workout_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS],
    )
    @pytest.mark.parametrize(
        'new_workout_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_with_create_activity_when_workout_is_now_visible_on_remote(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        old_workout_visibility: PrivacyLevel,
        new_workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_1.workout_visibility = old_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    title=self.random_string(),
                    workout_visibility=new_workout_visibility.value,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        create_workout_activity, _ = workout_cycling_user_1.get_activities(
            activity_type='Create'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=create_workout_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

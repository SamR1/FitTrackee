import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from ...mixins import ApiTestCaseMixin, BaseTestMixin
from ...utils import jsonify_dict
from ...workouts.utils import WorkoutCommentMixin


@patch('fittrackee.workouts.workouts.send_to_remote_inbox')
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
        send_to_remote_inbox_mock: Mock,
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
        send_to_remote_inbox_mock: Mock,
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
        send_to_remote_inbox_mock: Mock,
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
        assert new_comment.ap_id == (
            f'{user_1.actor.activitypub_id}/'
            f'workouts/{remote_cycling_workout.short_id}/'
            f'comments/{new_comment.short_id}'
        )
        assert new_comment.remote_url == (
            f'https://{user_1.actor.domain.name}/'
            f'workouts/{remote_cycling_workout.short_id}/'
            f'comments/{new_comment.short_id}'
        )

    def test_it_does_not_call_sent_to_inbox_if_privacy_is_local_followers_only(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
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

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_does_not_call_sent_to_inbox_if_user_has_no_remote_followers(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
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

        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_fittrackee_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_remote_user_to_user_1: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(remote_user)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
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

        note_activity = WorkoutComment.query.first().get_activity(
            activity_type='Create'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_calls_sent_to_inbox_if_user_has_follower_from_remote_other_instance(  # noqa
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        remote_user_2.send_follow_request_to(user_1)
        user_1.approves_follow_request_from(remote_user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f"/api/workouts/{workout_cycling_user_2.short_id}/comments",
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

        note_activity = WorkoutComment.query.first().get_activity(
            activity_type='Create'
        )
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=note_activity,
            recipients=[remote_user_2.actor.shared_inbox_url],
        )


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
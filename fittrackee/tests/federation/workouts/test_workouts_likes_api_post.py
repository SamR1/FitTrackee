import json
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee import db
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ...mixins import ApiTestCaseMixin, BaseTestMixin


@patch('fittrackee.federation.utils.user.update_remote_user')
@patch('fittrackee.workouts.workouts.send_to_remote_inbox')
class TestWorkoutLikePost(ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/like'

    def test_it_creates_workout_like(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = (
            VisibilityLevel.FOLLOWERS_AND_REMOTE
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=remote_cycling_workout.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['id']
            == remote_cycling_workout.short_id
        )
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=remote_cycling_workout.id
            ).first()
            is not None
        )
        assert remote_cycling_workout.likes.all() == [user_1]

    def test_it_does_not_call_sent_to_inbox_if_workout_is_local(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_calls_sent_to_inbox_if_comment_is_remote(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(workout_uuid=remote_cycling_workout.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        like_activity = WorkoutLike.query.first().get_activity()
        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=like_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )


@patch('fittrackee.federation.utils.user.update_remote_user')
@patch('fittrackee.workouts.workouts.send_to_remote_inbox')
class TestWorkoutUndoLikePost(ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/like/undo'

    def test_it_removes_workout_like(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = (
            VisibilityLevel.FOLLOWERS_AND_REMOTE
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=remote_cycling_workout.id
        )
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=remote_cycling_workout.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['id']
            == remote_cycling_workout.short_id
        )
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=remote_cycling_workout.id
            ).first()
            is None
        )
        assert remote_cycling_workout.likes.all() == []

    def test_it_does_not_call_sent_to_inbox_if_workout_is_local(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    def test_it_calls_sent_to_inbox_if_like_is_remote(
        self,
        send_to_remote_inbox_mock: Mock,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = VisibilityLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_1.id, workout_id=remote_cycling_workout.id
        )
        db.session.add(like)
        db.session.commit()
        undo_activity = WorkoutLike.query.first().get_activity(is_undo=True)
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            self.route.format(workout_uuid=remote_cycling_workout.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_called_once_with(
            sender_id=user_1.actor.id,
            activity=undo_activity,
            recipients=[remote_user.actor.shared_inbox_url],
        )

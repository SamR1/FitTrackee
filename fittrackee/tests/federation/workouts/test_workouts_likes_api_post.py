import json

from flask import Flask

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ...mixins import ApiTestCaseMixin, BaseTestMixin


class TestWorkoutLikePost(ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/like'

    def test_it_creates_workout_like(
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


class TestWorkoutUndoLikePost(ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/like/undo'

    def test_it_removes_workout_like(
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

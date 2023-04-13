from datetime import datetime

from flask import Flask
from freezegun import freeze_time

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout, WorkoutLike


class TestWorkoutLikeModel:
    def test_workout_likes_model(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        created_at = datetime.utcnow()

        like = WorkoutLike(
            user_id=user_2.id,
            workout_id=workout_cycling_user_1.id,
            created_at=created_at,
        )

        assert like.user_id == user_2.id
        assert like.workout_id == workout_cycling_user_1.id
        assert like.created_at == created_at

    def test_created_date_is_initialized_on_creation_when_not_provided(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        now = datetime.utcnow()
        with freeze_time(now):
            like = WorkoutLike(
                user_id=user_2.id,
                workout_id=workout_cycling_user_1.id,
            )

        assert like.user_id == user_2.id
        assert like.workout_id == workout_cycling_user_1.id
        assert like.created_at == now

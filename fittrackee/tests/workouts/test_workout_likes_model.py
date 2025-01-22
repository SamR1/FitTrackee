from datetime import datetime, timezone

from flask import Flask
from time_machine import travel

from fittrackee import db
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
        created_at = datetime.now(timezone.utc)

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
        now = datetime.now(timezone.utc)
        with travel(now, tick=False):
            like = WorkoutLike(
                user_id=user_2.id,
                workout_id=workout_cycling_user_1.id,
            )

        assert like.user_id == user_2.id
        assert like.workout_id == workout_cycling_user_1.id
        assert like.created_at == now

    def test_it_deletes_workout_like_on_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id,
            workout_id=workout_cycling_user_1.id,
        )
        db.session.add(like)
        db.session.commit()
        like_id = like.id

        db.session.delete(user_2)

        assert WorkoutLike.query.filter_by(id=like_id).first() is None

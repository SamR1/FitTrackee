from datetime import datetime
from typing import Optional

from flask import Flask
from freezegun import freeze_time

from fittrackee import db
from fittrackee.users.models import User
from fittrackee.utils import encode_uuid
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from ..mixins import RandomMixin


class TestWorkoutCommentModel(RandomMixin):
    def create_comment(
        self,
        user: User,
        workout: Workout,
        text: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> WorkoutComment:
        text = self.random_string() if text is None else text
        comment = WorkoutComment(
            user_id=user.id,
            workout_id=workout.id,
            text=text,
            created_at=created_at,
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    def test_comment_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        text = self.random_string()
        created_at = datetime.utcnow()
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text=text,
            created_at=created_at,
        )

        assert comment.user_id == user_1.id
        assert comment.workout_id == workout_cycling_user_1.id
        assert comment.text == text
        assert comment.created_at == created_at

    def test_created_date_is_initialized_on_creation_when_not_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        now = datetime.utcnow()
        with freeze_time(now):

            comment = self.create_comment(
                user=user_1,
                workout=workout_cycling_user_1,
            )

        assert comment.created_at == now

    def test_short_id_returns_encoded_comment_uuid(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
        )

        assert comment.short_id == encode_uuid(comment.uuid)

    def test_it_returns_string_representation(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
        )

        assert str(comment) == f'<WorkoutComment {comment.id}>'

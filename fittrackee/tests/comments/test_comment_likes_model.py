from datetime import datetime

from flask import Flask
from freezegun import freeze_time

from fittrackee.comments.models import CommentLike
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from .utils import CommentMixin


class TestCommentLikeModel(CommentMixin):
    def test_workout_likes_model(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user=user_1, workout=workout_cycling_user_1
        )
        created_at = datetime.utcnow()

        like = CommentLike(
            user_id=user_2.id,
            comment_id=comment.id,
            created_at=created_at,
        )

        assert like.user_id == user_2.id
        assert like.comment_id == comment.id
        assert like.created_at == created_at

    def test_created_date_is_initialized_on_creation_when_not_provided(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user=user_1, workout=workout_cycling_user_1
        )
        now = datetime.utcnow()
        with freeze_time(now):
            like = CommentLike(user_id=user_2.id, comment_id=comment.id)

        assert like.user_id == user_2.id
        assert like.comment_id == comment.id
        assert like.created_at == now

from datetime import datetime

from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.comments.models import CommentLike
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from .mixins import CommentMixin


class TestCommentLikeModel(CommentMixin):
    def test_workout_likes_model(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
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
        comment = self.create_comment(user_1, workout_cycling_user_1)
        now = datetime.utcnow()
        with travel(now, tick=False):
            like = CommentLike(user_id=user_2.id, comment_id=comment.id)

        assert like.user_id == user_2.id
        assert like.comment_id == comment.id
        assert like.created_at == now

    def test_it_deletes_comment_like_on_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        like = CommentLike(user_id=user_2.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()
        like_id = like.id

        db.session.delete(user_2)

        assert CommentLike.query.filter_by(id=like_id).first() is None

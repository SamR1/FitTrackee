from datetime import datetime

from flask import Flask
from freezegun import freeze_time

from fittrackee.comments.models import Mention
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..workouts.utils import WorkoutCommentMixin


class TestMentionModel(WorkoutCommentMixin):
    def test_mention_model(
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
        created_at = datetime.utcnow()

        mention = Mention(
            comment_id=comment.id, user_id=user_1.id, created_at=created_at
        )

        assert mention.user_id == user_1.id
        assert mention.comment_id == comment.id
        assert mention.created_at == created_at

    def test_created_date_is_initialized_on_creation_when_not_provided(
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
        now = datetime.utcnow()
        with freeze_time(now):
            mention = Mention(comment_id=comment.id, user_id=user_1.id)

        assert mention.created_at == now

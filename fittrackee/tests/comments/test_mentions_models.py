from datetime import datetime

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Mention
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from .mixins import CommentMixin

ALL_VISIBILITIES = [
    PrivacyLevel.PUBLIC,
    PrivacyLevel.FOLLOWERS,
    PrivacyLevel.PRIVATE,
]


class TestMentionModel(CommentMixin):
    def test_mention_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
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
        comment = self.create_comment(user_1, workout_cycling_user_1)
        now = datetime.utcnow()
        with travel(now, tick=False):
            mention = Mention(comment_id=comment.id, user_id=user_1.id)

        assert mention.created_at == now

    def test_it_deletes_mention_on_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        mention = Mention(comment_id=comment.id, user_id=user_1.id)
        db.session.add(mention)
        db.session.commit()
        deleted_user_id = user_2.id

        db.session.delete(user_2)

        assert (
            Mention.query.filter_by(
                user_id=deleted_user_id, comment_id=comment.id
            ).first()
            is None
        )

    def test_it_deletes_mention_on_comment_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)
        mention = Mention(comment_id=comment.id, user_id=user_1.id)
        db.session.add(mention)
        db.session.commit()
        deleted_comment_id = comment.id

        db.session.delete(comment)

        assert (
            Mention.query.filter_by(
                user_id=user_2.id, comment_id=deleted_comment_id
            ).first()
            is None
        )


class TestCommentWithMentionSerializeVisibility(CommentMixin):
    @pytest.mark.parametrize('workout_visibility', ALL_VISIBILITIES)
    def test_public_comment_is_visible_to_all_users(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = workout_visibility
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text=f"@{user_2.username} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        comment.serialize(user_1)  # author
        comment.serialize(user_2)  # mentioned user
        comment.serialize(user_3)  # user
        comment.serialize()  # unauthenticated user

    @pytest.mark.parametrize('workout_visibility', ALL_VISIBILITIES)
    def test_comment_for_followers_is_visible_to_followers_and_mentioned_users(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = workout_visibility
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=PrivacyLevel.FOLLOWERS,
        )

        assert comment.serialize(user_1)  # author
        assert comment.serialize(user_2)  # follower
        assert comment.serialize(user_3)  # mentioned user
        with pytest.raises(CommentForbiddenException):
            assert comment.serialize(user_4)  # user
            assert comment.serialize()  # unauthenticated user

    @pytest.mark.parametrize('workout_visibility', ALL_VISIBILITIES)
    def test_private_comment_is_only_visible_to_author_and_mentioned_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        user_4: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        workout_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = workout_visibility
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=PrivacyLevel.PRIVATE,
        )

        assert comment.serialize(user_1)  # author
        assert comment.serialize(user_3)  # mentioned user
        with pytest.raises(CommentForbiddenException):
            assert comment.serialize(user_2)  # follower
            assert comment.serialize(user_4)  # user
            assert comment.serialize()  # unauthenticated user

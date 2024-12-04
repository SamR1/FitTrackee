from datetime import datetime

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment, CommentLike, Mention
from fittrackee.users.models import FollowRequest, User
from fittrackee.utils import encode_uuid
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ReportMixin
from .mixins import CommentMixin


class TestWorkoutCommentModel(ReportMixin, CommentMixin):
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
            user_1,
            workout_cycling_user_1,
            text=text,
            created_at=created_at,
        )

        assert comment.user_id == user_1.id
        assert comment.workout_id == workout_cycling_user_1.id
        assert comment.text == text
        assert comment.created_at == created_at
        assert comment.modification_date is None
        assert comment.text_visibility == VisibilityLevel.PRIVATE
        assert comment.suspended_at is None

    def test_created_date_is_initialized_on_creation_when_not_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        now = datetime.utcnow()
        with travel(now, tick=False):
            comment = self.create_comment(user_1, workout_cycling_user_1)

        assert comment.created_at == now

    def test_short_id_returns_encoded_comment_uuid(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_1, workout_cycling_user_1)

        assert comment.short_id == encode_uuid(comment.uuid)

    def test_it_returns_string_representation(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
        )

        assert str(comment) == f'<Comment {comment.id}>'

    def test_it_deletes_comment_on_user_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
        )
        comment_id = comment.id

        db.session.delete(user_2)

        assert Comment.query.filter_by(id=comment_id).first() is None

    def test_it_does_not_delete_comment_on_workout_delete(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
        )
        comment_id = comment.id

        db.session.delete(workout_cycling_user_1)

        assert Comment.query.filter_by(id=comment_id).first() is not None

    def test_suspension_action_is_none_when_no_suspension(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_2, workout_cycling_user_1)

        assert comment.suspension_action is None

    def test_suspension_action_is_last_suspension_action_when_comment_is_suspended(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_2, workout_cycling_user_1)
        expected_report_action = self.create_report_comment_actions(
            user_1_admin, user_2, comment
        )
        comment.suspended_at = datetime.utcnow()

        assert comment.suspension_action == expected_report_action

    def test_suspension_action_is_none_when_comment_is_unsuspended(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        comment = self.create_comment(user_2, workout_cycling_user_1)
        self.create_report_comment_action(
            user_1_admin, user_2, comment, "comment_suspension"
        )
        self.create_report_comment_action(
            user_1_admin, user_2, comment, "comment_unsuspension"
        )

        assert comment.suspension_action is None


class TestWorkoutCommentModelSerializeForCommentOwner(
    ReportMixin, CommentMixin
):
    @pytest.mark.parametrize('suspended', [True, False])
    @pytest.mark.parametrize(
        'input_visibility',
        [
            VisibilityLevel.PRIVATE,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PUBLIC,
        ],
    )
    def test_it_serializes_owner_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
        suspended: bool,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=input_visibility,
        )
        if suspended:
            comment.suspended_at = datetime.utcnow()
            suspended_at = {
                "suspended": True,
                "suspended_at": comment.suspended_at,
            }
        else:
            suspended_at = {"suspended_at": None}

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
            **suspended_at,
        }

    def test_it_serializes_owner_comment_when_workout_is_deleted(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(user_1, workout_cycling_user_2)
        db.session.delete(workout_cycling_user_2)

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'suspended_at': comment.suspended_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_owner_comment_when_workout_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        comment = self.create_comment(user_1, workout_cycling_user_2)

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'suspended_at': comment.suspended_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_owner_comment_when_comment_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        comment = self.create_comment(user_1, workout_cycling_user_2)
        expected_report_action = self.create_report_comment_actions(
            user_2_admin, user_1, comment
        )
        comment.suspended_at = datetime.utcnow()

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'suspended': True,
            'suspended_at': comment.suspended_at,
            'suspension': expected_report_action.serialize(user_1, full=False),
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelSerializeForFollower(CommentMixin):
    def test_it_raises_error_when_user_does_not_follow_comment_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    def test_it_raises_error_when_comment_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.FOLLOWERS
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PRIVATE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    @pytest.mark.parametrize(
        'input_visibility', [VisibilityLevel.FOLLOWERS, VisibilityLevel.PUBLIC]
    )
    def test_it_serializes_comment_for_follower_when_privacy_allows_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_visibility: VisibilityLevel,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = input_visibility
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_when_workout_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PRIVATE
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        db.session.delete(workout_cycling_user_1)

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelSerializeForUser(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_raises_error_when_comment_is_not_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    def test_it_serializes_comment_when_comment_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        # TODO: mentions
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_when_workout_is_deleted(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        db.session.delete(workout_cycling_user_1)
        db.session.commit()

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_when_workout_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PRIVATE
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelSerializeForModerator(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_raises_error_when_comment_is_visible(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_visibility,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1_moderator)

    @pytest.mark.parametrize('suspended', [True, False])
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_serializes_comment_when_report_flag_is_true(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_visibility: VisibilityLevel,
        suspended: bool,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=input_visibility,
            with_mentions=True,
        )
        if suspended:
            comment.suspended_at = datetime.utcnow()
            suspended_at = {
                "suspended": True,
                "suspended_at": comment.suspended_at,
            }
        else:
            suspended_at = {"suspended_at": None}

        serialized_comment = comment.serialize(
            user_1_moderator, for_report=True
        )

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_3.serialize(),
            'workout_id': workout_cycling_user_2.short_id,
            'text': comment.text,
            'text_html': comment.handle_mentions()[0],
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [user_2.serialize()],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
            **suspended_at,
        }

    def test_it_does_not_return_content_when_comment_is_suspended(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=True,
        )
        comment.suspended_at = datetime.utcnow()

        serialized_comment = comment.serialize(user_1_moderator)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_3.serialize(),
            'workout_id': workout_cycling_user_2.short_id,
            'text': None,
            'text_html': None,
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'suspended': True,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelSerializeForAdmin(CommentMixin):
    def test_it_raises_error_when_comment_is_visible(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1_admin)

    def test_it_serializes_comment_when_report_flag_is_true(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text=f"@{user_2.username}",
            text_visibility=VisibilityLevel.FOLLOWERS,
            with_mentions=True,
        )
        comment.suspended_at = datetime.utcnow()

        serialized_comment = comment.serialize(user_1_admin, for_report=True)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_3.serialize(),
            'workout_id': workout_cycling_user_2.short_id,
            'text': comment.text,
            'text_html': comment.handle_mentions()[0],
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [user_2.serialize()],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
            'suspended': True,
            'suspended_at': comment.suspended_at,
        }


class TestWorkoutCommentModelSerializeForUnauthenticatedUser(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_raises_error_when_comment_is_not_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize()

    def test_it_serializes_comment_when_comment_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        # TODO: mentions
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_comment = comment.serialize()

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_when_workout_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PRIVATE
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_comment = comment.serialize()

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelSerializeForReplies(CommentMixin):
    def test_it_serializes_comment_with_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )

        serialized_comment = parent_comment.serialize(user_1)

        assert serialized_comment == {
            'id': parent_comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': parent_comment.text,
            'text_html': parent_comment.text,  # no mention
            'text_visibility': parent_comment.text_visibility,
            'created_at': parent_comment.created_at,
            'mentions': [],
            'suspended_at': parent_comment.suspended_at,
            'modification_date': parent_comment.modification_date,
            'reply_to': None,
            'replies': [comment.serialize(user_1)],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_with_suspended_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        suspended_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )
        suspended_comment.suspended_at = datetime.utcnow()

        serialized_comment = parent_comment.serialize(user_1)

        assert serialized_comment == {
            'id': parent_comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': parent_comment.text,
            'text_html': parent_comment.text,  # no mention
            'text_visibility': parent_comment.text_visibility,
            'created_at': parent_comment.created_at,
            'mentions': [],
            'suspended_at': parent_comment.suspended_at,
            'modification_date': parent_comment.modification_date,
            'reply_to': None,
            'replies': [suspended_comment.serialize(user_1)],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_parent_comment_without_replies(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )

        serialized_comment = parent_comment.serialize(
            user_1, with_replies=False
        )

        assert serialized_comment == {
            'id': parent_comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': parent_comment.text,
            'text_html': parent_comment.text,  # no mention
            'text_visibility': parent_comment.text_visibility,
            'created_at': parent_comment.created_at,
            'mentions': [],
            'suspended_at': parent_comment.suspended_at,
            'modification_date': parent_comment.modification_date,
            'reply_to': None,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_2.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': parent_comment.short_id,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_reply_with_serialized_parent(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )

        serialized_comment = comment.serialize(user_1, get_parent_comment=True)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_2.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': parent_comment.serialize(user_1, with_replies=False),
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_serializes_comment_reply_when_workout_is_deleted(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )
        db.session.delete(workout_cycling_user_1)
        db.session.commit()

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_2.serialize(),
            'workout_id': None,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': parent_comment.short_id,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_returns_only_visible_replies_for_a_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_1.approves_follow_request_from(user_2)
        user_1.approves_follow_request_from(user_3)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        # replies
        self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PRIVATE,
            parent_comment=comment,
        )
        visible_replies = [
            self.create_comment(
                user_3,
                workout_cycling_user_1,
                text_visibility=VisibilityLevel.PUBLIC,
                parent_comment=comment,
            )
        ]
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
            parent_comment=comment,
        )
        visible_replies.append(
            self.create_comment(
                user_1,
                workout_cycling_user_1,
                text_visibility=VisibilityLevel.FOLLOWERS,
                parent_comment=comment,
            ),
        )

        serialized_comment = comment.serialize(user_3)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': None,
            'replies': [
                visible_reply.serialize(user_3)
                for visible_reply in visible_replies
            ],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_returns_only_visible_replies_for_unauthenticated_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_1.approves_follow_request_from(user_2)
        user_1.approves_follow_request_from(user_3)
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        # replies
        self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PRIVATE,
            parent_comment=comment,
        )
        visible_reply = self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=comment,
        )
        self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
            parent_comment=comment,
        )
        suspended_reply = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=comment,
        )
        suspended_reply.suspended_at = datetime.utcnow()

        serialized_comment = comment.serialize(user_3)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [],
            'modification_date': comment.modification_date,
            'reply_to': None,
            'replies': [
                visible_reply.serialize(user_3),
                suspended_reply.serialize(user_3),
            ],
            'likes_count': 0,
            'liked': False,
        }

    def test_it_returns_all_replies(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        visible_replies = []
        for _ in range(7):
            visible_replies.append(
                self.create_comment(
                    user_1,
                    workout_cycling_user_1,
                    text_visibility=VisibilityLevel.PUBLIC,
                    parent_comment=comment,
                ),
            )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment['replies'] == [
            visible_reply.serialize(user_1)
            for visible_reply in visible_replies
        ]


class TestWorkoutCommentModelSerializeForRepliesForAdmin(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_raises_error_when_comments_are_not_visible(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_3_to_user_2: FollowRequest,
        input_visibility: VisibilityLevel,
    ) -> None:
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS,
            parent_comment=parent_comment,
        )

        with pytest.raises(CommentForbiddenException):
            parent_comment.serialize(user_1_admin)

    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE],
    )
    def test_it_serializes_comment_with_reply(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_3_to_user_2: FollowRequest,
        input_visibility: VisibilityLevel,
    ) -> None:
        # for report only parent comment is returned
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        parent_comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=input_visibility,
        )
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=input_visibility,
            parent_comment=parent_comment,
        )

        serialized_comment = parent_comment.serialize(
            user_1_admin, for_report=True
        )

        assert serialized_comment == {
            'id': parent_comment.short_id,
            'user': user_2.serialize(),
            'workout_id': workout_cycling_user_2.short_id,
            'text': parent_comment.text,
            'text_html': parent_comment.text,  # no mention
            'text_visibility': parent_comment.text_visibility,
            'created_at': parent_comment.created_at,
            'mentions': [],
            'suspended_at': parent_comment.suspended_at,
            'modification_date': parent_comment.modification_date,
            'reply_to': None,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelWithMentions(CommentMixin):
    def test_it_returns_empty_set_when_no_mentions(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=self.random_string(),
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == set()

    def test_it_does_not_create_mentions_when_mentioned_user_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{self.random_string()} {self.random_string()}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=False,
        )

        comment.create_mentions()

        assert Mention.query.filter_by().first() is None

    def test_it_returns_empty_set_when_mentioned_user_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{self.random_string()} {self.random_string()}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == set()

    def test_it_creates_mentions_when_mentioned_user_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=False,
        )

        comment.create_mentions()

        mention = Mention.query.first()
        assert mention.comment_id == comment.id
        assert mention.user_id == user_3.id

    def test_it_returns_mentioned_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        mention = f"@{user_3.username}"
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"{mention} {self.random_string()}",
            text_visibility=VisibilityLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == {user_3}


class TestWorkoutCommentModelSerializeForMentions(CommentMixin):
    def test_it_serializes_comment_with_mentions_as_link(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["text"] == comment.text
        assert serialized_comment["text_html"] == comment.handle_mentions()[0]

    def test_it_serializes_comment_with_mentioned_users(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=(
                f"@{user_3.username} {self.random_string()} @{user_1.username}"
            ),
            text_visibility=VisibilityLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_2)

        assert len(serialized_comment["mentions"]) == 2
        assert user_1.serialize() in serialized_comment["mentions"]
        assert user_3.serialize() in serialized_comment["mentions"]


class TestWorkoutCommentModelSerializeForMentionedUser(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [
            VisibilityLevel.PUBLIC,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PRIVATE,
        ],
    )
    def test_it_serializes_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        # user_2 does not follow user_1
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text=f"@{user_2.username} {self.random_string()}",
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_2)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.handle_mentions()[0],
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'mentions': [user_2.serialize()],
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
            'likes_count': 0,
            'liked': False,
        }


class TestWorkoutCommentModelSerializeWithLikes(CommentMixin):
    def test_it_returns_like_count(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        for user in [user_1, user_3]:
            like = CommentLike(user_id=user.id, comment_id=comment.id)
            db.session.add(like)
        db.session.commit()

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["likes_count"] == 2

    def test_it_returns_if_user_liked_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        like = CommentLike(user_id=user_1.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["liked"] is True

    def test_it_returns_if_user_did_not_like_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        like = CommentLike(user_id=user_2.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["liked"] is False

    def test_it_returns_if_likes_info_for_unauthenticated_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        like = CommentLike(user_id=user_2.id, comment_id=comment.id)
        db.session.add(like)
        db.session.commit()

        serialized_comment = comment.serialize()

        assert serialized_comment["likes_count"] == 1
        assert serialized_comment["liked"] is False

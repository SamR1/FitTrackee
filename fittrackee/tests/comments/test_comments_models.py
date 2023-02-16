from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment, Mention
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.utils import encode_uuid
from fittrackee.workouts.models import Sport, Workout

from .utils import CommentMixin


class TestWorkoutCommentModel(CommentMixin):
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
        assert comment.modification_date is None
        assert comment.text_visibility == PrivacyLevel.PRIVATE

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

    def test_it_raises_error_when_privacy_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        text_visibility = PrivacyLevel.FOLLOWERS_AND_REMOTE
        with pytest.raises(
            InvalidVisibilityException,
            match=(
                f'invalid visibility: {text_visibility}, '
                'federation is disabled.'
            ),
        ):
            Comment(
                user_id=user_1.id,
                workout_id=workout_cycling_user_1.id,
                text=self.random_string(),
                text_visibility=text_visibility,
            )

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

        assert str(comment) == f'<Comment {comment.id}>'


class TestWorkoutCommentModelSerializeForCommentOwner(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_serializes_owner_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    def test_it_raises_error_when_privacy_does_not_allow_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_2)

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC]
    )
    def test_it_serializes_comment_for_follower_when_privacy_allows_it(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = input_visibility
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
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
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
        }


class TestWorkoutCommentModelSerializeForUser(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_raises_error_when_comment_is_not_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
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
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
        }


class TestWorkoutCommentModelSerializeForUnauthenticatedUser(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE]
    )
    def test_it_raises_error_when_comment_is_not_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
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
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        parent_comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
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
            'modification_date': parent_comment.modification_date,
            'reply_to': parent_comment.reply_to,
            'replies': [comment.serialize(user_1)],
        }

    def test_it_serializes_comment_reply(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        parent_comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
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
            'modification_date': comment.modification_date,
            'reply_to': parent_comment.short_id,
            'replies': [],
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        # replies
        self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
            parent_comment=comment,
        )
        visible_replies = [
            self.create_comment(
                user=user_3,
                workout=workout_cycling_user_1,
                text_visibility=PrivacyLevel.PUBLIC,
                parent_comment=comment,
            )
        ]
        self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=comment,
        )
        visible_replies.append(
            self.create_comment(
                user=user_1,
                workout=workout_cycling_user_1,
                text_visibility=PrivacyLevel.FOLLOWERS,
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
            'modification_date': comment.modification_date,
            'reply_to': None,
            'replies': [
                visible_reply.serialize(user_3)
                for visible_reply in visible_replies
            ],
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        # replies
        self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PRIVATE,
            parent_comment=comment,
        )
        visible_reply = self.create_comment(
            user=user_3,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=comment,
        )
        self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
            parent_comment=comment,
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
            'modification_date': comment.modification_date,
            'reply_to': None,
            'replies': [visible_reply.serialize()],
        }

    def test_it_returns_all_replies(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        visible_replies = []
        for _ in range(7):
            visible_replies.append(
                self.create_comment(
                    user=user_1,
                    workout=workout_cycling_user_1,
                    text_visibility=PrivacyLevel.PUBLIC,
                    parent_comment=comment,
                ),
            )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment['replies'] == [
            visible_reply.serialize(user_1)
            for visible_reply in visible_replies
        ]


class TestWorkoutCommentModelWithMentions(CommentMixin):
    def test_it_returns_empty_dict_when_no_mentions(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=self.random_string(),
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == {"local": set(), "remote": set()}

    @patch('fittrackee.federation.utils.user.fetch_account_from_webfinger')
    def test_it_does_not_create_mentions_when_mentioned_user_does_not_exist(
        self,
        fetch_mock: Mock,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{self.random_string()} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )
        fetch_mock.side_effect = Exception()

        comment.create_mentions()

        assert Mention.query.filter_by().first() is None

    def test_it_returns_empty_dict_when_mentioned_user_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{self.random_string()} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == {"local": set(), "remote": set()}

    def test_it_creates_mentions_when_mentioned_user_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        mention = f"@{user_3.username}"
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"{mention} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == {"local": {user_3}, "remote": set()}


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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{user_3.username} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["text"] == comment.text
        assert serialized_comment["text_html"] == comment.handle_mentions()[0]

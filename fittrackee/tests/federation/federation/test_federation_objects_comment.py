from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT
from fittrackee.federation.objects.comment import CommentObject
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ...comments.mixins import CommentMixin


class TestWorkoutCommentCreateObject(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_raises_error_when_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        # no mentioned users
        comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=input_visibility
        )
        with pytest.raises(
            InvalidVisibilityException,
            match=f"object visibility is: '{input_visibility.value}'",
        ):
            CommentObject(comment, 'Create')

    def test_it_raises_error_when_activity_type_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        invalid_activity_type = self.random_string()
        with pytest.raises(
            ValueError,
            match=f"'{invalid_activity_type}' is not a valid ActivityType",
        ):
            CommentObject(comment, invalid_activity_type)

    def test_it_generates_activity_when_visibility_is_followers_and_remote_only(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
        )
        published = comment.created_at.strftime(DATE_FORMAT)
        comment_object = CommentObject(comment, 'Create')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{comment.ap_id}/create",
            "type": "Create",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": [user_2.actor.followers_url],
            "cc": [],
            "object": {
                "id": comment.ap_id,
                "type": "Note",
                "published": published,
                "url": comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": comment.text,
                "to": [user_2.actor.followers_url],
                "cc": [],
            },
        }

    def test_it_generates_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        published = comment.created_at.strftime(DATE_FORMAT)
        comment_object = CommentObject(comment, 'Create')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{comment.ap_id}/create",
            "type": "Create",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_2.actor.followers_url],
            "object": {
                "id": comment.ap_id,
                "type": "Note",
                "published": published,
                "url": comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": comment.text,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_2.actor.followers_url],
            },
        }

    def test_it_generates_activity_when_comment_has_parent_comment(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        parent_comment = self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
            parent_comment=parent_comment,
        )
        published = comment.created_at.strftime(DATE_FORMAT)
        comment_object = CommentObject(comment, 'Create')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{comment.ap_id}/create",
            "type": "Create",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_2.actor.followers_url],
            "object": {
                "id": comment.ap_id,
                "type": "Note",
                "published": published,
                "url": comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": parent_comment.ap_id,
                "content": comment.text,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_2.actor.followers_url],
            },
        }


@patch('fittrackee.federation.utils.user.update_remote_user')
class TestWorkoutCommentWithMentionsCreateObject(CommentMixin):
    def test_it_generates_activity_for_public_comment(
        self,
        update_remote_user_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment_object = CommentObject(comment, 'Create')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = comment.handle_mentions()
        assert serialized_comment['to'] == [
            "https://www.w3.org/ns/activitystreams#Public"
        ]
        assert set(serialized_comment['cc']) == {
            user_2.actor.followers_url,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['to'] == [
            "https://www.w3.org/ns/activitystreams#Public"
        ]
        assert set(serialized_comment['object']['cc']) == {
            user_2.actor.followers_url,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }

    def test_it_generates_activity_with_followers_and_remote_visibility(
        self,
        update_remote_user_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
        )
        comment_object = CommentObject(comment, 'Create')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = comment.handle_mentions()
        assert serialized_comment['to'] == [user_2.actor.followers_url]
        assert set(serialized_comment['cc']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['to'] == [
            user_2.actor.followers_url
        ]
        assert set(serialized_comment['object']['cc']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }

    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_generates_activity_with_mentioned_users(
        self,
        update_remote_user_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=input_visibility,
        )
        comment_object = CommentObject(comment, 'Create')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = comment.handle_mentions()
        assert set(serialized_comment['to']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['cc'] == []
        assert set(serialized_comment['object']['to']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['cc'] == []


class TestWorkoutCommentUpdateObject(CommentMixin):
    def test_it_raises_error_when_activity_type_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        invalid_activity_type = self.random_string()
        with pytest.raises(
            ValueError,
            match=f"'{invalid_activity_type}' is not a valid ActivityType",
        ):
            CommentObject(comment, invalid_activity_type)

    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_generates_activity_when_visibility_is_private_or_for_local_followers(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        # case of mention removed
        comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=input_visibility
        )
        comment.modification_date = datetime.utcnow()
        published = comment.created_at.strftime(DATE_FORMAT)
        comment_object = CommentObject(comment, 'Update')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{comment.ap_id}/update",
            "type": "Update",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": [],  # mention removed
            "cc": [],
            "object": {
                "id": comment.ap_id,
                "type": "Note",
                "published": published,
                "url": comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": comment.text,
                "to": [],
                "cc": [],
                "updated": comment.modification_date.strftime(DATE_FORMAT),
            },
        }

    def test_it_generates_activity_when_visibility_is_followers_and_remote_only(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
        )
        comment.modification_date = datetime.utcnow()
        published = comment.created_at.strftime(DATE_FORMAT)
        comment_object = CommentObject(comment, 'Update')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{comment.ap_id}/update",
            "type": "Update",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": [user_2.actor.followers_url],
            "cc": [],
            "object": {
                "id": comment.ap_id,
                "type": "Note",
                "published": published,
                "url": comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": comment.text,
                "to": [user_2.actor.followers_url],
                "cc": [],
                "updated": comment.modification_date.strftime(DATE_FORMAT),
            },
        }

    def test_it_generates_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment.modification_date = datetime.utcnow()
        published = comment.created_at.strftime(DATE_FORMAT)
        comment_object = CommentObject(comment, 'Update')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{comment.ap_id}/update",
            "type": "Update",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_2.actor.followers_url],
            "object": {
                "id": comment.ap_id,
                "type": "Note",
                "published": published,
                "url": comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": comment.text,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_2.actor.followers_url],
                "updated": comment.modification_date.strftime(DATE_FORMAT),
            },
        }


@patch('fittrackee.federation.utils.user.update_remote_user')
class TestWorkoutCommentWithMentionsUpdateObject(CommentMixin):
    def test_it_generates_activity_for_public_comment(
        self,
        update_remote_user_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=VisibilityLevel.PUBLIC,
        )
        comment.modification_date = datetime.utcnow()
        comment_object = CommentObject(comment, 'Update')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = comment.handle_mentions()
        assert serialized_comment['to'] == [
            "https://www.w3.org/ns/activitystreams#Public"
        ]
        assert set(serialized_comment['cc']) == {
            user_2.actor.followers_url,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['to'] == [
            "https://www.w3.org/ns/activitystreams#Public"
        ]
        assert set(serialized_comment['object']['cc']) == {
            user_2.actor.followers_url,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }

    def test_it_generates_activity_with_followers_and_remote_visibility(
        self,
        update_remote_user_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
        )
        comment.modification_date = datetime.utcnow()
        comment_object = CommentObject(comment, 'Update')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = comment.handle_mentions()
        assert serialized_comment['to'] == [user_2.actor.followers_url]
        assert set(serialized_comment['cc']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['to'] == [
            user_2.actor.followers_url
        ]
        assert set(serialized_comment['object']['cc']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }

    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_generates_activity_for_private_comment_with_mentioned_users(
        self,
        update_remote_user_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=VisibilityLevel.PRIVATE,
        )
        comment.modification_date = datetime.utcnow()
        comment_object = CommentObject(comment, 'Update')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = comment.handle_mentions()
        assert set(serialized_comment['to']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['cc'] == []
        assert set(serialized_comment['object']['to']) == {
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['cc'] == []

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT
from fittrackee.federation.objects.comment import WorkoutCommentObject
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.workouts.utils import WorkoutCommentMixin
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout


class TestWorkoutCommentCreateObject(WorkoutCommentMixin):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_when_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=input_visibility
        )
        with pytest.raises(
            InvalidVisibilityException,
            match=f"object visibility is: '{input_visibility.value}'",
        ):
            WorkoutCommentObject(workout_comment, 'Create')

    def test_it_raises_error_when_activity_type_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )
        invalid_activity_type = self.random_string()
        with pytest.raises(
            ValueError,
            match=f"'{invalid_activity_type}' is not a valid ActivityType",
        ):
            WorkoutCommentObject(workout_comment, invalid_activity_type)

    def test_it_generates_activity_when_visibility_is_followers_and_remote_only(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        published = workout_comment.created_at.strftime(DATE_FORMAT)
        comment_object = WorkoutCommentObject(workout_comment, 'Create')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{workout_comment.ap_id}/create",
            "type": "Create",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": [user_2.actor.followers_url],
            "cc": [user_2.actor.activitypub_id],
            "object": {
                "id": workout_comment.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": workout_comment.text,
                "to": [user_2.actor.followers_url],
                "cc": [user_2.actor.activitypub_id],
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        published = workout_comment.created_at.strftime(DATE_FORMAT)
        comment_object = WorkoutCommentObject(workout_comment, 'Create')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{workout_comment.ap_id}/create",
            "type": "Create",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_2.actor.followers_url],
            "object": {
                "id": workout_comment.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": workout_comment.text,
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        parent_comment = self.create_comment(
            user_3,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=parent_comment,
        )
        published = workout_comment.created_at.strftime(DATE_FORMAT)
        comment_object = WorkoutCommentObject(workout_comment, 'Create')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{workout_comment.ap_id}/create",
            "type": "Create",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_2.actor.followers_url],
            "object": {
                "id": workout_comment.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": parent_comment.ap_id,
                "content": workout_comment.text,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_2.actor.followers_url],
            },
        }

    @patch('fittrackee.federation.utils.user.update_remote_user')
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
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=PrivacyLevel.PUBLIC,
        )
        comment_object = WorkoutCommentObject(workout_comment, 'Create')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = workout_comment.handle_mentions()
        assert set(serialized_comment['cc']) == {
            user_2.actor.followers_url,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert set(serialized_comment['object']['cc']) == {
            user_2.actor.followers_url,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['content'] == text_with_mentions


class TestWorkoutCommentUpdateObject(WorkoutCommentMixin):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_when_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=input_visibility
        )
        with pytest.raises(
            InvalidVisibilityException,
            match=f"object visibility is: '{input_visibility.value}'",
        ):
            WorkoutCommentObject(workout_comment, 'Update')

    def test_it_raises_error_when_activity_type_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )
        invalid_activity_type = self.random_string()
        with pytest.raises(
            ValueError,
            match=f"'{invalid_activity_type}' is not a valid ActivityType",
        ):
            WorkoutCommentObject(workout_comment, invalid_activity_type)

    def test_it_generates_activity_when_visibility_is_followers_and_remote_only(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        workout_comment.modification_date = datetime.utcnow()
        published = workout_comment.created_at.strftime(DATE_FORMAT)
        comment_object = WorkoutCommentObject(workout_comment, 'Update')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{workout_comment.ap_id}/update",
            "type": "Update",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": [user_2.actor.followers_url],
            "cc": [user_2.actor.activitypub_id],
            "object": {
                "id": workout_comment.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": workout_comment.text,
                "to": [user_2.actor.followers_url],
                "cc": [user_2.actor.activitypub_id],
                "updated": workout_comment.modification_date.strftime(
                    DATE_FORMAT
                ),
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )

        workout_comment.modification_date = datetime.utcnow()
        published = workout_comment.created_at.strftime(DATE_FORMAT)
        comment_object = WorkoutCommentObject(workout_comment, 'Update')

        serialized_comment = comment_object.get_activity()

        assert serialized_comment == {
            "@context": AP_CTX,
            "id": f"{workout_comment.ap_id}/update",
            "type": "Update",
            "actor": user_2.actor.activitypub_id,
            "published": published,
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "cc": [user_2.actor.followers_url],
            "object": {
                "id": workout_comment.ap_id,
                "type": "Note",
                "published": published,
                "url": workout_comment.remote_url,
                "attributedTo": user_2.actor.activitypub_id,
                "inReplyTo": workout_cycling_user_1.ap_id,
                "content": workout_comment.text,
                "to": ["https://www.w3.org/ns/activitystreams#Public"],
                "cc": [user_2.actor.followers_url],
                "updated": workout_comment.modification_date.strftime(
                    DATE_FORMAT
                ),
            },
        }

    @patch('fittrackee.federation.utils.user.update_remote_user')
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
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = self.random_string()
        workout_comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text=f"@{user_3.username} @{remote_user.fullname} great!",
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        workout_comment.modification_date = datetime.utcnow()
        comment_object = WorkoutCommentObject(workout_comment, 'Update')

        serialized_comment = comment_object.get_activity()

        text_with_mentions, _ = workout_comment.handle_mentions()
        assert set(serialized_comment['cc']) == {
            user_2.actor.activitypub_id,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert set(serialized_comment['object']['cc']) == {
            user_2.actor.activitypub_id,
            user_3.actor.activitypub_id,
            remote_user.actor.activitypub_id,
        }
        assert serialized_comment['object']['content'] == text_with_mentions

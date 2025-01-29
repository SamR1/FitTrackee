from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.constants import AP_CTX, PUBLIC_STREAM
from fittrackee.federation.objects.tombstone import TombstoneObject
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ...comments.mixins import CommentMixin


class TestTombstoneObjectForWorkout:
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_raises_error_when_visibility_is_private(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        workout_cycling_user_1.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts'
            f'/{workout_cycling_user_1.short_id}'
        )
        with pytest.raises(
            InvalidVisibilityException,
            match=f"object visibility is: '{input_visibility.value}'",
        ):
            TombstoneObject(workout_cycling_user_1)

    def test_it_generates_delete_activity_for_workout_with_public_visibility(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts'
            f'/{workout_cycling_user_1.short_id}'
        )
        tombstone = TombstoneObject(workout_cycling_user_1)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": f'{workout_cycling_user_1.ap_id}/delete',
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": workout_cycling_user_1.ap_id,
            },
            "to": [PUBLIC_STREAM],
            "cc": [user_1.actor.followers_url],
        }

    def test_it_generates_delete_activity_for_workout_with_follower_visibility(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = (
            VisibilityLevel.FOLLOWERS_AND_REMOTE
        )
        workout_cycling_user_1.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts'
            f'/{workout_cycling_user_1.short_id}'
        )
        tombstone = TombstoneObject(workout_cycling_user_1)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": f'{workout_cycling_user_1.ap_id}/delete',
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": workout_cycling_user_1.ap_id,
            },
            "to": [user_1.actor.followers_url],
            "cc": [],
        }


class TestTombstoneObjectForWorkoutComment(CommentMixin):
    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    def test_it_raises_error_when_comment_has_no_mention(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1, workout_cycling_user_1, text_visibility=input_visibility
        )
        with pytest.raises(
            InvalidVisibilityException,
            match=f"object visibility is: '{input_visibility.value}'",
        ):
            TombstoneObject(comment)

    def test_it_generates_delete_activity_for_comment_with_public_visibility(
        self,
        app_with_federation: Flask,
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
        tombstone = TombstoneObject(comment)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/comments/'
                f'{comment.short_id}/delete'
            ),
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}/comments/'
                    f'{comment.short_id}'
                ),
            },
            "to": [PUBLIC_STREAM],
            "cc": [user_1.actor.followers_url],
        }

    def test_it_generates_delete_activity_for_comment_with_follower_visibility(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS_AND_REMOTE,
        )
        tombstone = TombstoneObject(comment)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/comments/'
                f'{comment.short_id}/delete'
            ),
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}/comments/'
                    f'{comment.short_id}'
                ),
            },
            "to": [user_1.actor.followers_url],
            "cc": [],
        }

    @pytest.mark.parametrize(
        'input_visibility',
        [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS],
    )
    @patch('fittrackee.federation.utils.user.update_remote_user')
    def test_it_generates_delete_activity_for_comment_with_private_or_local_followers_visibility_and_mention(  # noqa
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: VisibilityLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text=f"@{remote_user.fullname}",
            text_visibility=input_visibility,
        )
        tombstone = TombstoneObject(comment)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/comments/'
                f'{comment.short_id}/delete'
            ),
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}/comments/'
                    f'{comment.short_id}'
                ),
            },
            "to": [remote_user.actor.activitypub_id],
            "cc": [],
        }

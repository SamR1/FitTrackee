import pytest
from flask import Flask

from fittrackee.federation.constants import AP_CTX, PUBLIC_STREAM
from fittrackee.federation.objects.exceptions import InvalidVisibilityException
from fittrackee.federation.objects.tombstone import TombstoneObject
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout


class TestTombstoneObjectForWorkout:
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_when_visibility_is_private(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        tombstone = TombstoneObject(workout_cycling_user_1)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/delete'
            ),
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
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
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        tombstone = TombstoneObject(workout_cycling_user_1)

        delete_activity = tombstone.get_activity()

        assert delete_activity == {
            "@context": AP_CTX,
            "id": (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/delete'
            ),
            "type": "Delete",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
            },
            "to": [user_1.actor.followers_url],
            "cc": [],
        }

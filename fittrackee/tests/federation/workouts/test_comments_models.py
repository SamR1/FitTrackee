import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import InvalidVisibilityException
from fittrackee.workouts.models import Sport, Workout, WorkoutComment

from ...mixins import RandomMixin


class TestWorkoutCommentModel(RandomMixin):
    @pytest.mark.parametrize(
        'input_workout_visibility, input_text_visibility',
        [
            (PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.FOLLOWERS),
            (
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
            ),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS_AND_REMOTE),
        ],
    )
    def test_it_initializes_text_visibility_when_workout_visibility_is_not_stricter(  # noqa
        self,
        input_workout_visibility: PrivacyLevel,
        input_text_visibility: PrivacyLevel,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        comment = WorkoutComment(
            user_id=user_1.id,
            workout_id=workout_cycling_user_1.id,
            workout_visibility=workout_cycling_user_1.workout_visibility,
            text=self.random_string(),
            text_visibility=input_text_visibility,
        )

        assert comment.text_visibility == input_text_visibility

    @pytest.mark.parametrize(
        'input_workout_visibility, input_text_visibility',
        [
            (PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS_AND_REMOTE),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS_AND_REMOTE),
        ],
    )
    def test_it_raises_when_workout_visibility_is_stricter(
        self,
        input_workout_visibility: PrivacyLevel,
        input_text_visibility: PrivacyLevel,
        app_with_federation: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        with pytest.raises(
            InvalidVisibilityException,
            match=(
                f'invalid visibility: {input_text_visibility} '
                f'\\(workout visibility: {input_workout_visibility}\\)'
            ),
        ):
            WorkoutComment(
                user_id=user_1.id,
                workout_id=workout_cycling_user_1.id,
                workout_visibility=workout_cycling_user_1.workout_visibility,
                text=self.random_string(),
                text_visibility=input_text_visibility,
            )

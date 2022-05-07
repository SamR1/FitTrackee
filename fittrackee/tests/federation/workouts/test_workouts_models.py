import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import PrivateWorkoutException
from fittrackee.workouts.models import Sport, Workout

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class TestWorkoutModelGetWorkoutActivity:
    def test_it_raises_error_if_visibility_is_private(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        with pytest.raises(PrivateWorkoutException):
            workout_cycling_user_1.get_activities()

    @pytest.mark.parametrize(
        'workout_visibility',
        [
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PUBLIC,
        ],
    )
    def test_it_returns_activities_when_visibility_is_not_private(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = workout_visibility.value

        workout, note = workout_cycling_user_1.get_activities()

        assert workout['type'] == 'Create'
        assert workout['object']['type'] == 'Workout'
        assert note['type'] == 'Create'
        assert note['object']['type'] == 'Note'

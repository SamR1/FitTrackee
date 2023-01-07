import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.workouts.test_workouts_model import WorkoutModelTestCase
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

from ...utils import random_string

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class TestWorkoutModelAsRemoteFollower(WorkoutModelTestCase):
    user_status = 'remote_follower'

    def test_it_raises_exception_when_workout_visibility_is_private(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PRIVATE

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user_status=self.user_status)

    def test_it_raises_exception_when_workout_visibility_is_local_follower_only(  # noqa
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user_status=self.user_status)

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
            ),
            (
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                PrivacyLevel.PUBLIC,
            ),
            (
                PrivacyLevel.PUBLIC,
                PrivacyLevel.PUBLIC,
            ),
        ],
    )
    def test_serializer_returns_map_related_data(
        self,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user_status=self.user_status)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == [
            workout_cycling_user_1_segment.serialize()
        ]

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
            ),
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
            ),
        ],
    )
    def test_serializer_does_not_return_map_related_data(
        self,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_status=self.user_status)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []


class TestWorkoutModelGetWorkoutCreateActivity:
    activity_type = 'Create'

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_if_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        with pytest.raises(InvalidVisibilityException):
            workout_cycling_user_1.get_activities(
                activity_type=self.activity_type
            )

    @pytest.mark.parametrize(
        'workout_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_returns_activities_when_visibility_is_valid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = workout_visibility

        create_workout, create_note = workout_cycling_user_1.get_activities(
            activity_type=self.activity_type
        )

        assert create_workout['type'] == self.activity_type
        assert create_workout['object']['type'] == 'Workout'
        assert create_note['type'] == self.activity_type
        assert create_note['object']['type'] == 'Note'


class TestWorkoutModelGetWorkoutUpdateActivity(
    TestWorkoutModelGetWorkoutCreateActivity
):
    activity_type = 'Update'


class TestWorkoutModelGetWorkoutDeleteActivity:
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_if_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        with pytest.raises(InvalidVisibilityException):
            workout_cycling_user_1.get_activities(activity_type='Delete')

    @pytest.mark.parametrize(
        'workout_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_returns_activities_when_visibility_is_valid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = workout_visibility

        delete_workout, _ = workout_cycling_user_1.get_activities(
            activity_type='Delete'
        )

        assert delete_workout['type'] == 'Delete'
        assert delete_workout['object']['type'] == 'Tombstone'
        assert delete_workout['object']['id'] == (
            f'{user_1.actor.activitypub_id}/workouts/'
            f'{workout_cycling_user_1.short_id}'
        )

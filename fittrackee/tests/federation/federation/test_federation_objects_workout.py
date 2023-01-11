from typing import Any

import pytest
from flask import Flask

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT
from fittrackee.federation.exceptions import InvalidWorkoutException
from fittrackee.federation.objects.workout import (
    WorkoutObject,
    convert_duration_string_to_seconds,
    convert_workout_activity,
)
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.mixins import RandomMixin
from fittrackee.users.models import User
from fittrackee.workouts.constants import WORKOUT_DATE_FORMAT
from fittrackee.workouts.models import Sport, Workout


class TestWorkoutObject(RandomMixin):
    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_when_visibility_is_invalid(
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
            WorkoutObject(workout_cycling_user_1, 'Create')

    def test_it_raises_error_when_activity_type_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        invalid_activity_type = self.random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        with pytest.raises(
            ValueError,
            match=f"'{invalid_activity_type}' is not a valid ActivityType",
        ):
            WorkoutObject(workout_cycling_user_1, invalid_activity_type)

    @pytest.mark.parametrize('input_activity_type', ['Create', 'Update'])
    def test_it_generates_activity_when_visibility_is_followers_and_remote_only(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_activity_type: str,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1, input_activity_type)

        serialized_workout = workout.get_activity()

        assert serialized_workout == {
            '@context': AP_CTX,
            'id': f'{workout_cycling_user_1.ap_id}/activity',
            'type': input_activity_type,
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'object': {
                'id': workout_cycling_user_1.ap_id,
                'type': 'Workout',
                'published': published,
                'url': workout_cycling_user_1.remote_url,
                'attributedTo': user_1.actor.activitypub_id,
                'to': [user_1.actor.followers_url],
                'cc': [],
                'ave_speed': float(workout_cycling_user_1.ave_speed),
                'distance': float(workout_cycling_user_1.distance),
                'duration': str(workout_cycling_user_1.duration),
                'max_speed': float(workout_cycling_user_1.max_speed),
                'moving': str(workout_cycling_user_1.moving),
                'sport_id': workout_cycling_user_1.sport_id,
                'title': workout_cycling_user_1.title,
                'workout_date': workout_cycling_user_1.workout_date.strftime(
                    WORKOUT_DATE_FORMAT
                ),
            },
        }

    @pytest.mark.parametrize('input_activity_type', ['Create', 'Update'])
    def test_it_generates_create_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_activity_type: str,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1, input_activity_type)

        serialized_workout = workout.get_activity()

        assert serialized_workout == {
            '@context': AP_CTX,
            'id': f'{workout_cycling_user_1.ap_id}/activity',
            'type': input_activity_type,
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': [user_1.actor.followers_url],
            'object': {
                'id': workout_cycling_user_1.ap_id,
                'type': 'Workout',
                'published': published,
                'url': workout_cycling_user_1.remote_url,
                'attributedTo': user_1.actor.activitypub_id,
                'to': ['https://www.w3.org/ns/activitystreams#Public'],
                'cc': [user_1.actor.followers_url],
                'ave_speed': float(workout_cycling_user_1.ave_speed),
                'distance': float(workout_cycling_user_1.distance),
                'duration': str(workout_cycling_user_1.duration),
                'max_speed': float(workout_cycling_user_1.max_speed),
                'moving': str(workout_cycling_user_1.moving),
                'sport_id': workout_cycling_user_1.sport_id,
                'title': workout_cycling_user_1.title,
                'workout_date': workout_cycling_user_1.workout_date.strftime(
                    WORKOUT_DATE_FORMAT
                ),
            },
        }


class TestWorkoutNoteObject(RandomMixin):
    @staticmethod
    def expected_workout_note(workout: Workout, expected_url: str) -> str:
        return f"""<p>New workout: <a href="{expected_url}" target="_blank" rel="noopener noreferrer">{workout.title}</a> ({workout.sport.label})

Distance: {workout.distance:.2f}km
Duration: {workout.duration}</p>
"""

    def test_it_returns_note_activity_when_visibility_is_followers_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1, 'Create')

        serialized_workout_note = workout.get_activity(is_note=True)

        assert serialized_workout_note == {
            '@context': AP_CTX,
            'id': f'{workout_cycling_user_1.ap_id}/note/activity',
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'object': {
                'id': workout_cycling_user_1.ap_id,
                'type': 'Note',
                'published': published,
                'url': workout_cycling_user_1.remote_url,
                'attributedTo': user_1.actor.activitypub_id,
                'content': self.expected_workout_note(
                    workout_cycling_user_1, workout_cycling_user_1.remote_url
                ),
                'to': [user_1.actor.followers_url],
                'cc': [],
            },
        }

    def test_it_returns_note_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1, 'Create')

        serialized_workout_note = workout.get_activity(is_note=True)

        assert serialized_workout_note == {
            '@context': AP_CTX,
            'id': f'{workout_cycling_user_1.ap_id}/note/activity',
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': [user_1.actor.followers_url],
            'object': {
                'id': workout_cycling_user_1.ap_id,
                'type': 'Note',
                'published': published,
                'url': workout_cycling_user_1.remote_url,
                'attributedTo': user_1.actor.activitypub_id,
                'content': self.expected_workout_note(
                    workout_cycling_user_1, workout_cycling_user_1.remote_url
                ),
                'to': ['https://www.w3.org/ns/activitystreams#Public'],
                'cc': [user_1.actor.followers_url],
            },
        }


class TestWorkoutConvertDurationStringToSeconds:
    @pytest.mark.parametrize(
        'input_duration,expected_seconds',
        [
            ('0:00:00', 0),
            ('1:00:00', 3600),
            ('01:00:00', 3600),
            ('00:30:00', 1800),
            ('00:00:10', 10),
            ('01:20:30', 4830),
        ],
    )
    def test_it_converts_duration_string_into_seconds(
        self, input_duration: str, expected_seconds: int
    ) -> None:
        assert (
            convert_duration_string_to_seconds(duration_str=input_duration)
            == expected_seconds
        )

    @pytest.mark.parametrize(
        'input_duration',
        ['', '1:00', 3600, None],
    )
    def test_it_raises_exception_if_duration_is_invalid(
        self, input_duration: Any
    ) -> None:
        with pytest.raises(
            InvalidWorkoutException,
            match='Invalid workout data: duration or moving format is invalid',
        ):
            convert_duration_string_to_seconds(duration_str=input_duration)


class TestWorkoutConvertWorkoutActivity(RandomMixin):
    def test_it_convert_workout_data_from_activity(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_activity_object = {
            'id': self.random_string(),
            'type': 'Workout',
            'published': workout_cycling_user_1.creation_date.strftime(
                DATE_FORMAT
            ),
            'url': self.random_string(),
            'attributedTo': user_1.actor.activitypub_id,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'ave_speed': float(workout_cycling_user_1.ave_speed),
            'distance': float(workout_cycling_user_1.distance),
            'duration': str(workout_cycling_user_1.duration),
            'max_speed': float(workout_cycling_user_1.max_speed),
            'moving': str(workout_cycling_user_1.moving),
            'sport_id': workout_cycling_user_1.sport_id,
            'title': workout_cycling_user_1.title,
            'workout_date': workout_cycling_user_1.workout_date.strftime(
                WORKOUT_DATE_FORMAT
            ),
            'workout_visibility': workout_cycling_user_1.workout_visibility,
        }

        assert convert_workout_activity(workout_activity_object) == {
            **workout_activity_object,
            'duration': workout_cycling_user_1.duration.seconds,
            'moving': workout_cycling_user_1.moving.seconds,
        }

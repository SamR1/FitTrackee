import pytest
from flask import Flask

from fittrackee.federation.activities.workout import WorkoutObject
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.mixins import RandomMixin
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import PrivateWorkoutException
from fittrackee.workouts.models import Sport, Workout


class WorkoutObjectTestCase(RandomMixin):
    @staticmethod
    def expected_url(user: User, workout: Workout) -> str:
        return (
            f'https://{user.actor.domain.name}/workouts/' f'{workout.short_id}'
        )


class TestWorkoutObject(WorkoutObjectTestCase):
    def test_it_raises_error_when_visibility_is_private(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        with pytest.raises(PrivateWorkoutException):
            WorkoutObject(workout_cycling_user_1)

    def test_it_generates_create_activity_when_visibility_is_followers_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)

        serialized_workout = workout.serialize()

        assert serialized_workout == {
            '@context': AP_CTX,
            'id': (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Workout',
                'published': published,
                'url': self.expected_url(user_1, workout_cycling_user_1),
                'attributedTo': user_1.actor.activitypub_id,
                'to': [user_1.actor.followers_url],
                'cc': [],
                'ascent': workout_cycling_user_1.ascent,
                'descent': workout_cycling_user_1.descent,
                'distance': workout_cycling_user_1.distance,
                'duration': workout_cycling_user_1.duration,
                'max_alt': workout_cycling_user_1.max_alt,
                'min_alt': workout_cycling_user_1.min_alt,
                'moving': workout_cycling_user_1.moving,
                'sport_id': workout_cycling_user_1.sport_id,
                'title': workout_cycling_user_1.title,
                'workout_date': workout_cycling_user_1.workout_date.strftime(
                    DATE_FORMAT
                ),
            },
        }

    def test_it_generates_create_activity_when_visibility_is_public(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)

        serialized_workout = workout.serialize()

        assert serialized_workout == {
            '@context': AP_CTX,
            'id': (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': [user_1.actor.followers_url],
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Workout',
                'published': published,
                'url': self.expected_url(user_1, workout_cycling_user_1),
                'attributedTo': user_1.actor.activitypub_id,
                'to': ['https://www.w3.org/ns/activitystreams#Public'],
                'cc': [user_1.actor.followers_url],
                'ascent': workout_cycling_user_1.ascent,
                'descent': workout_cycling_user_1.descent,
                'distance': workout_cycling_user_1.distance,
                'duration': workout_cycling_user_1.duration,
                'max_alt': workout_cycling_user_1.max_alt,
                'min_alt': workout_cycling_user_1.min_alt,
                'moving': workout_cycling_user_1.moving,
                'sport_id': workout_cycling_user_1.sport_id,
                'title': workout_cycling_user_1.title,
                'workout_date': workout_cycling_user_1.workout_date.strftime(
                    DATE_FORMAT
                ),
            },
        }


class TestWorkoutNoteObject(WorkoutObjectTestCase):
    @staticmethod
    def expected_workout_note(workout: Workout, expected_url: str) -> str:
        return f"""<p>New workout: <a href="{expected_url}" target="_blank" rel="noopener noreferrer">{workout.title}</a> ({workout.sport.label})

Distance: {workout.distance:.2f}km
Duration: {workout.duration}</p>
"""

    def test_it_raises_error_if_visibility_is_private(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        with pytest.raises(PrivateWorkoutException):
            WorkoutObject(workout_cycling_user_1)

    def test_it_returns_note_activity_when_visibility_is_followers_only(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = self.random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)
        expected_url = self.expected_url(user_1, workout_cycling_user_1)

        serialized_workout_note = workout.serialize(is_note=True)

        assert serialized_workout_note == {
            '@context': AP_CTX,
            'id': (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/note/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Note',
                'published': published,
                'url': expected_url,
                'attributedTo': user_1.actor.activitypub_id,
                'content': self.expected_workout_note(
                    workout_cycling_user_1, expected_url
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
        workout = WorkoutObject(workout_cycling_user_1)
        expected_url = self.expected_url(user_1, workout_cycling_user_1)

        serialized_workout_note = workout.serialize(is_note=True)

        assert serialized_workout_note == {
            '@context': AP_CTX,
            'id': (
                f'{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/note/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': [user_1.actor.followers_url],
            'object': {
                'id': (
                    f'{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Note',
                'published': published,
                'url': expected_url,
                'attributedTo': user_1.actor.activitypub_id,
                'content': self.expected_workout_note(
                    workout_cycling_user_1, expected_url
                ),
                'to': ['https://www.w3.org/ns/activitystreams#Public'],
                'cc': [user_1.actor.followers_url],
            },
        }

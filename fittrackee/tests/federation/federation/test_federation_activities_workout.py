import pytest
from flask import Flask

from fittrackee.federation.activities.workout import WorkoutObject
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import PrivateWorkoutException
from fittrackee.workouts.models import Sport, Workout


class TestWorkoutObject:
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)

        serialized_workout = workout.serialize()

        assert serialized_workout == {
            '@context': AP_CTX,
            'id': (
                f'https://{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'object': {
                'id': (
                    f'https://{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Workout',
                'published': published,
                'url': (
                    f'https://{user_1.actor.domain.name}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)

        serialized_workout = workout.serialize()

        assert serialized_workout == {
            '@context': AP_CTX,
            'id': (
                f'https://{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': [user_1.actor.followers_url],
            'object': {
                'id': (
                    f'https://{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Workout',
                'published': published,
                'url': (
                    f'https://{user_1.actor.domain.name}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
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


class TestWorkoutNoteObject:
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)
        expected_url = (
            f'https://{user_1.actor.domain.name}/workouts/'
            f'{workout_cycling_user_1.short_id}'
        )
        expected_content = f"""New workout "{workout_cycling_user_1.title}"'

Distance: {workout_cycling_user_1.distance}km
Duration: {workout_cycling_user_1.duration}

#fittrackee

link: {expected_url}
"""

        serialized_workout_note = workout.serialize(is_note=True)

        assert serialized_workout_note == {
            '@context': AP_CTX,
            'id': (
                f'https://{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/note/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': [user_1.actor.followers_url],
            'cc': [],
            'object': {
                'id': (
                    f'https://{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Note',
                'published': published,
                'url': expected_url,
                'attributedTo': user_1.actor.activitypub_id,
                'content': expected_content,
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
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        published = workout_cycling_user_1.creation_date.strftime(DATE_FORMAT)
        workout = WorkoutObject(workout_cycling_user_1)
        expected_url = (
            f'https://{user_1.actor.domain.name}/workouts/'
            f'{workout_cycling_user_1.short_id}'
        )
        expected_content = f"""New workout "{workout_cycling_user_1.title}"'

Distance: {workout_cycling_user_1.distance}km
Duration: {workout_cycling_user_1.duration}

#fittrackee

link: {expected_url}
"""

        serialized_workout_note = workout.serialize(is_note=True)

        assert serialized_workout_note == {
            '@context': AP_CTX,
            'id': (
                f'https://{user_1.actor.activitypub_id}/workouts/'
                f'{workout_cycling_user_1.short_id}/note/activity'
            ),
            'type': 'Create',
            'actor': user_1.actor.activitypub_id,
            'published': published,
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'cc': [user_1.actor.followers_url],
            'object': {
                'id': (
                    f'https://{user_1.actor.activitypub_id}/workouts/'
                    f'{workout_cycling_user_1.short_id}'
                ),
                'type': 'Note',
                'published': published,
                'url': expected_url,
                'attributedTo': user_1.actor.activitypub_id,
                'content': expected_content,
                'to': ['https://www.w3.org/ns/activitystreams#Public'],
                'cc': [user_1.actor.followers_url],
            },
        }

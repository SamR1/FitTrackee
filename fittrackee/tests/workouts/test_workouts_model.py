import datetime
from datetime import timedelta
from typing import List, Optional

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.utils import encode_uuid
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..utils import random_string
from .utils import add_follower


class WorkoutModelTestCase:
    @staticmethod
    def update_workout(
        workout: Workout,
        map_id: Optional[str] = None,
        gpx_path: Optional[str] = None,
        bounds: Optional[List[float]] = None,
    ) -> Workout:
        workout.map_id = map_id
        workout.map = random_string() if map_id is None else map_id
        workout.gpx = random_string() if gpx_path is None else gpx_path
        workout.bounds = [1.0, 2.0, 3.0, 4.0] if bounds is None else bounds
        workout.pauses = timedelta(minutes=15)
        return workout


class TestWorkoutModelForOwner(WorkoutModelTestCase):
    def test_sport_label_and_date_are_in_string_value(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = 'Test'
        db.session.commit()
        assert '<Workout \'Cycling\' - 2018-01-01 00:00:00>' == str(
            workout_cycling_user_1
        )

    def test_short_id_returns_encoded_workout_uuid(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        assert workout_cycling_user_1.short_id == encode_uuid(
            workout_cycling_user_1.uuid
        )

    def test_serialize_for_workout_without_gpx(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout = workout_cycling_user_1

        serialized_workout = workout.serialize(user_1)
        assert serialized_workout['ascent'] is None
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == []
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] is None
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['id'] == workout.short_id
        assert serialized_workout['likes_count'] == 0
        assert serialized_workout['liked'] is False
        assert serialized_workout['map'] is None
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(workout.max_speed)
        assert serialized_workout['min_alt'] is None
        assert serialized_workout['suspended_at'] is None
        assert serialized_workout['modification_date'] is None
        assert serialized_workout['moving'] == str(workout.moving)
        assert serialized_workout['next_workout'] is None
        assert serialized_workout['notes'] is None
        assert serialized_workout['pauses'] is None
        assert serialized_workout['previous_workout'] is None
        assert serialized_workout['records'] == [
            record.serialize() for record in workout.records
        ]
        assert serialized_workout['segments'] == []
        assert serialized_workout['sport_id'] == workout.sport_id
        assert serialized_workout['title'] == workout.title
        assert serialized_workout['user'] == user_1.serialize()
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['with_gpx'] is False
        assert str(serialized_workout['workout_date']) == '2018-01-01 00:00:00'

    def test_serialize_for_workout_without_gpx_and_with_ascent_and_descent(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout = workout_cycling_user_1
        workout.ascent = 0
        workout.descent = 10

        serialized_workout = workout.serialize(user_1)
        assert serialized_workout['ascent'] == workout.ascent
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == []
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] == workout.descent
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['id'] == workout.short_id
        assert serialized_workout['map'] is None
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(workout.max_speed)
        assert serialized_workout['min_alt'] is None
        assert serialized_workout['suspended_at'] is None
        assert serialized_workout['modification_date'] is not None
        assert serialized_workout['moving'] == str(workout.moving)
        assert serialized_workout['next_workout'] is None
        assert serialized_workout['notes'] is None
        assert serialized_workout['pauses'] is None
        assert serialized_workout['previous_workout'] is None
        assert serialized_workout['records'] == [
            record.serialize() for record in workout.records
        ]
        assert serialized_workout['segments'] == []
        assert serialized_workout['sport_id'] == workout.sport_id
        assert serialized_workout['title'] == workout.title
        assert serialized_workout['user'] == user_1.serialize()
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['with_gpx'] is False
        assert str(serialized_workout['workout_date']) == '2018-01-01 00:00:00'

    def test_serialize_for_workout_with_gpx(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: Workout,
    ) -> None:
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_1)
        assert serialized_workout['ascent'] is None
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == [
            float(bound) for bound in workout.bounds
        ]
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] is None
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['id'] == workout.short_id
        assert serialized_workout['map'] is None
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(workout.max_speed)
        assert serialized_workout['min_alt'] is None
        assert serialized_workout['suspended_at'] is None
        assert serialized_workout['modification_date'] is not None
        assert serialized_workout['moving'] == str(workout.moving)
        assert serialized_workout['next_workout'] is None
        assert serialized_workout['notes'] is None
        assert serialized_workout['pauses'] == str(workout.pauses)
        assert serialized_workout['previous_workout'] is None
        assert serialized_workout['records'] == [
            record.serialize() for record in workout.records
        ]
        assert serialized_workout['segments'] == [
            segment.serialize() for segment in workout.segments
        ]
        assert serialized_workout['sport_id'] == workout.sport_id
        assert serialized_workout['title'] == workout.title
        assert serialized_workout['user'] == user_1.serialize()
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['with_gpx'] is True
        assert str(serialized_workout['workout_date']) == '2018-01-01 00:00:00'

    def test_serializer_returns_map_related_data(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user_1)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility,'
        'expected_map_visibility',
        [
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PRIVATE,
            ),
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.FOLLOWERS,
            ),
            (
                PrivacyLevel.PUBLIC,
                PrivacyLevel.PUBLIC,
                PrivacyLevel.PUBLIC,
            ),
            (
                PrivacyLevel.PUBLIC,
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PRIVATE,
            ),
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PRIVATE,
            ),
            (
                PrivacyLevel.PUBLIC,
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.FOLLOWERS,
            ),
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.PUBLIC,
                PrivacyLevel.FOLLOWERS,
            ),
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.PRIVATE,
            ),
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PUBLIC,
                PrivacyLevel.PRIVATE,
            ),
        ],
    )
    def test_workout_visibility_overrides_map_visibility_when_stricter(
        self,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
        expected_map_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        assert (
            workout_cycling_user_1.calculated_map_visibility
            == expected_map_visibility
        )
        serialized_workout = workout_cycling_user_1.serialize(user_1)
        assert (
            serialized_workout['map_visibility']
            == expected_map_visibility.value
        )

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_serializes_suspended_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.suspended_at = datetime.datetime.utcnow()

        serialized_workout = workout_cycling_user_1.serialize(user_1)

        assert (
            serialized_workout["suspended_at"]
            == workout_cycling_user_1.suspended_at
        )

    def test_workout_segment_model(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: Workout,
    ) -> None:
        assert (
            f'<Segment \'{workout_cycling_user_1_segment.segment_id}\' '
            f'for workout \'{workout_cycling_user_1.short_id}\'>'
            == str(workout_cycling_user_1_segment)
        )

    def test_it_returns_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        serialized_workout = workout_running_user_1.serialize(user_1)

        assert (
            serialized_workout['previous_workout']
            == workout_cycling_user_1.short_id
        )

    def test_it_returns_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        serialized_workout = workout_cycling_user_1.serialize(user_1)

        assert (
            serialized_workout['next_workout']
            == workout_running_user_1.short_id
        )

    def test_it_returns_likes_count(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        user_3: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        for user in [user_2, user_3]:
            like = WorkoutLike(
                user_id=user.id, workout_id=workout_cycling_user_1.id
            )
            db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(user_1)

        assert serialized_workout['likes_count'] == 2

    def test_it_returns_if_workout_is_not_liked_by_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(user_1)

        assert serialized_workout['liked'] is False

    def test_it_returns_if_workout_is_liked_by_user(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize(user_1)

        assert serialized_workout['liked'] is True


class TestWorkoutModelAsFollower(WorkoutModelTestCase):
    def test_it_raises_exception_when_workout_visibility_is_private(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PRIVATE
        add_follower(user_1, user_2)

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user_2)

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        add_follower(user_1, user_2)
        serialized_workout = workout_cycling_user_1.serialize(user_2)

        assert serialized_workout['notes'] is None

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.FOLLOWERS,
            ),
            (
                PrivacyLevel.FOLLOWERS,
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
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        add_follower(user_1, user_2)
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user_2)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.FOLLOWERS,
            ),
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PUBLIC,
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
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        add_follower(user_1, user_2)
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_2)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        add_follower(user_1, user_2)
        serialized_workout = workout_cycling_user_1.serialize(user_2)

        assert serialized_workout['next_workout'] is None

    def test_serializer_does_not_return_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        add_follower(user_1, user_2)

        serialized_workout = workout_running_user_1.serialize(user_2)

        assert serialized_workout['previous_workout'] is None

    def test_serializer_does_not_return_suspended_at(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        add_follower(user_1, user_2)

        serialized_workout = workout_cycling_user_1.serialize(user_2)

        assert 'suspended_at' not in serialized_workout

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        add_follower(user_1, user_2)
        workout_cycling_user_1.suspended_at = datetime.datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user_2)


class TestWorkoutModelAsUser(WorkoutModelTestCase):
    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', PrivacyLevel.FOLLOWERS),
            ('visibility: private', PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_raises_exception_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user_2)

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(user_2)

        assert serialized_workout['notes'] is None

    def test_serializer_returns_map_related_data_when_visibility_is_public(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.map_visibility = PrivacyLevel.PUBLIC
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize(user_2)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == PrivacyLevel.PUBLIC
        assert serialized_workout['workout_visibility'] == PrivacyLevel.PUBLIC
        assert serialized_workout['segments'] == []

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PUBLIC,
            ),
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.PUBLIC,
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
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_2)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(user_2)

        assert serialized_workout['next_workout'] is None

    def test_serializer_does_not_return_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_running_user_1.serialize(user_2)

        assert serialized_workout['previous_workout'] is None

    def test_serializer_does_not_return_suspended_at(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize(user_2)

        assert 'suspended_at' not in serialized_workout

    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.suspended_at = datetime.datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize(user_2)


class TestWorkoutModelAsUnauthenticatedUser(WorkoutModelTestCase):
    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', PrivacyLevel.FOLLOWERS),
            ('visibility: private', PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_raises_exception_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize()

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize()

        assert serialized_workout['notes'] is None

    def test_serializer_returns_map_related_data_when_visibility_is_public(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.map_visibility = PrivacyLevel.PUBLIC
        workout = self.update_workout(
            workout_cycling_user_1, map_id=random_string()
        )

        serialized_workout = workout.serialize()

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert serialized_workout['map_visibility'] == PrivacyLevel.PUBLIC
        assert serialized_workout['workout_visibility'] == PrivacyLevel.PUBLIC
        assert serialized_workout['segments'] == []

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (
                PrivacyLevel.PRIVATE,
                PrivacyLevel.PUBLIC,
            ),
            (
                PrivacyLevel.FOLLOWERS,
                PrivacyLevel.PUBLIC,
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
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize()

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['map_visibility'] == input_map_visibility
        assert (
            serialized_workout['workout_visibility']
            == input_workout_visibility
        )
        assert serialized_workout['segments'] == []

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize()

        assert serialized_workout['next_workout'] is None

    def test_serializer_does_not_return_previous_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_running_user_1.serialize()

        assert serialized_workout['previous_workout'] is None

    def test_it_returns_likes_count(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        like = WorkoutLike(
            user_id=user_2.id, workout_id=workout_cycling_user_1.id
        )
        db.session.add(like)
        db.session.commit()

        serialized_workout = workout_cycling_user_1.serialize()

        assert serialized_workout['liked'] is False
        assert serialized_workout['likes_count'] == 1

    def test_serializer_does_not_return_suspended_at(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC

        serialized_workout = workout_cycling_user_1.serialize()

        assert 'suspended_at' not in serialized_workout

    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_2: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.suspended_at = datetime.datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_1.serialize()


class TestWorkoutModelAsAdmin(WorkoutModelTestCase):
    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', PrivacyLevel.FOLLOWERS),
            ('visibility: private', PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_raises_exception_when_workout_is_not_visible(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_2.serialize(user_1_admin)

    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', PrivacyLevel.FOLLOWERS),
            ('visibility: private', PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_returns_workout_when_report_flag_is_true(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility

        serialized_workout = workout_cycling_user_2.serialize(
            user_1_admin, for_report=True
        )

        assert serialized_workout['ascent'] == workout_cycling_user_2.ascent
        assert serialized_workout['ave_speed'] == float(
            workout_cycling_user_2.ave_speed
        )
        assert serialized_workout['bounds'] == []
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] == workout_cycling_user_2.descent
        assert serialized_workout['distance'] == float(
            workout_cycling_user_2.distance
        )
        assert serialized_workout['duration'] == str(
            workout_cycling_user_2.duration
        )
        assert serialized_workout['id'] == workout_cycling_user_2.short_id
        assert serialized_workout['map'] is None
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(
            workout_cycling_user_2.max_speed
        )
        assert serialized_workout['min_alt'] is None
        assert serialized_workout['modification_date'] is not None
        assert serialized_workout['moving'] == str(
            workout_cycling_user_2.moving
        )
        assert serialized_workout['next_workout'] is None
        assert serialized_workout['notes'] is None
        assert serialized_workout['pauses'] is None
        assert serialized_workout['previous_workout'] is None
        assert serialized_workout['records'] == []
        assert serialized_workout['segments'] == []
        assert (
            serialized_workout['sport_id'] == workout_cycling_user_2.sport_id
        )
        assert serialized_workout['title'] == workout_cycling_user_2.title
        assert serialized_workout['user'] == user_2.serialize()
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['with_gpx'] is False
        assert str(serialized_workout['workout_date']) == '2018-01-23 00:00:00'

    @pytest.mark.parametrize(
        'input_desc, input_workout_visibility',
        [
            ('visibility: follower', PrivacyLevel.FOLLOWERS),
            ('visibility: private', PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_returns_workout_with_map_when_report_flag_is_true(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.map_visibility = input_workout_visibility
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        map_id = random_string()
        workout_cycling_user_2 = self.update_workout(
            workout_cycling_user_2, map_id=map_id
        )

        serialized_workout = workout_cycling_user_2.serialize(
            user_1_admin, for_report=True
        )

        assert serialized_workout['ascent'] == workout_cycling_user_2.ascent
        assert serialized_workout['ave_speed'] == float(
            workout_cycling_user_2.ave_speed
        )
        assert serialized_workout['bounds'] == workout_cycling_user_2.bounds
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] == workout_cycling_user_2.descent
        assert serialized_workout['distance'] == float(
            workout_cycling_user_2.distance
        )
        assert serialized_workout['duration'] == str(
            workout_cycling_user_2.duration
        )
        assert serialized_workout['id'] == workout_cycling_user_2.short_id
        assert serialized_workout['map'] == map_id
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(
            workout_cycling_user_2.max_speed
        )
        assert serialized_workout['min_alt'] is None
        assert serialized_workout['suspended_at'] is None
        assert serialized_workout['modification_date'] is not None
        assert serialized_workout['moving'] == str(
            workout_cycling_user_2.moving
        )
        assert serialized_workout['next_workout'] is None
        assert serialized_workout['notes'] is None
        assert serialized_workout['pauses'] == '0:15:00'
        assert serialized_workout['previous_workout'] is None
        assert serialized_workout['records'] == []
        assert serialized_workout['segments'] == []
        assert (
            serialized_workout['sport_id'] == workout_cycling_user_2.sport_id
        )
        assert serialized_workout['title'] == workout_cycling_user_2.title
        assert serialized_workout['user'] == user_2.serialize()
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['with_gpx'] is True
        assert str(serialized_workout['workout_date']) == '2018-01-23 00:00:00'

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_raises_exception_when_workout_is_suspended(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        workout_cycling_user_2.suspended_at = datetime.datetime.utcnow()

        with pytest.raises(WorkoutForbiddenException):
            workout_cycling_user_2.serialize(user_1_admin)

    @pytest.mark.parametrize(
        "input_workout_visibility",
        [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC],
    )
    def test_it_serializes_suspended_workout_for_report(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1_admin: User,
        user_2: User,
        workout_cycling_user_2: Workout,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        workout_cycling_user_2.suspended_at = datetime.datetime.utcnow()

        serialized_workout = workout_cycling_user_2.serialize(
            user_1_admin, for_report=True
        )

        assert (
            serialized_workout["suspended_at"]
            == workout_cycling_user_2.suspended_at
        )

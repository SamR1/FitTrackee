from datetime import timedelta
from typing import List, Optional

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.utils.short_id import encode_uuid

from ..utils import random_string


class WorkoutModelTestCase:
    @staticmethod
    def update_workout(
        workout: Workout,
        map_id: Optional[str] = None,
        gpx_path: Optional[str] = None,
        bounds: Optional[List[float]] = None,
    ) -> Workout:
        workout.map_id = random_string() if map_id is None else map_id
        workout.map = None if map_id is None else random_string()
        workout.gpx = random_string() if gpx_path is None else gpx_path
        workout.bounds = [1.0, 2.0, 3.0, 4.0] if bounds is None else bounds
        workout.pauses = timedelta(minutes=15)
        return workout


class TestWorkoutModelForOwner(WorkoutModelTestCase):
    user_status = 'owner'

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

        serialized_workout = workout.serialize(user_status=self.user_status)
        assert serialized_workout['ascent'] is None
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == []
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] is None
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['id'] == workout.short_id
        assert serialized_workout['map'] is None
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(workout.max_speed)
        assert serialized_workout['min_alt'] is None
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

    def test_serialize_for_workout_with_gpx(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: Workout,
    ) -> None:
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_status=self.user_status)
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
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_status=self.user_status)

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
        serialized_workout = workout_cycling_user_1.serialize(
            user_status=self.user_status
        )
        assert (
            serialized_workout['map_visibility']
            == expected_map_visibility.value
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
        serialized_workout = workout_running_user_1.serialize(self.user_status)

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
        serialized_workout = workout_cycling_user_1.serialize(self.user_status)

        assert (
            serialized_workout['next_workout']
            == workout_running_user_1.short_id
        )


class TestWorkoutModelAsFollower(WorkoutModelTestCase):
    user_status = 'follower'

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

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        serialized_workout = workout_cycling_user_1.serialize(
            user_status=self.user_status
        )

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
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_status=self.user_status)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert 'map_visibility' not in serialized_workout
        assert 'workout_visibility' not in serialized_workout

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
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.map_visibility = input_map_visibility
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_status=self.user_status)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert 'map_visibility' not in serialized_workout
        assert 'workout_visibility' not in serialized_workout

    def test_serializer_does_not_return_next_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        serialized_workout = workout_cycling_user_1.serialize(
            user_status=self.user_status
        )

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
        workout_running_user_1.workout_visibility = PrivacyLevel.FOLLOWERS
        serialized_workout = workout_running_user_1.serialize(
            user_status=self.user_status
        )

        assert serialized_workout['previous_workout'] is None


class TestWorkoutModelAsOther(WorkoutModelTestCase):
    user_status = 'other'

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
            workout_cycling_user_1.serialize(user_status=self.user_status)

    def test_serializer_does_not_return_notes(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.notes = random_string()
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        serialized_workout = workout_cycling_user_1.serialize(
            user_status=self.user_status
        )

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
        workout = self.update_workout(workout_cycling_user_1)

        serialized_workout = workout.serialize(user_status=self.user_status)

        assert serialized_workout['map'] == workout.map
        assert serialized_workout['bounds'] == workout.bounds
        assert serialized_workout['with_gpx'] is True
        assert 'map_visibility' not in serialized_workout
        assert 'workout_visibility' not in serialized_workout

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

        serialized_workout = workout.serialize(user_status=self.user_status)

        assert serialized_workout['map'] is None
        assert serialized_workout['bounds'] == []
        assert serialized_workout['with_gpx'] is False
        assert 'map_visibility' not in serialized_workout
        assert 'workout_visibility' not in serialized_workout

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
        serialized_workout = workout_cycling_user_1.serialize(
            user_status=self.user_status
        )

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
        serialized_workout = workout_running_user_1.serialize(
            user_status=self.user_status
        )

        assert serialized_workout['previous_workout'] is None
        assert 'map_visibility' not in serialized_workout
        assert 'workout_visibility' not in serialized_workout

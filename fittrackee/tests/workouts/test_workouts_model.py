from uuid import UUID

from flask import Flask

from fittrackee import db
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.utils_id import decode_short_id


class TestWorkoutModel:
    def test_workout_model(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = 'Test'
        db.session.commit()

        assert 1 == workout_cycling_user_1.id
        assert workout_cycling_user_1.uuid is not None
        assert 1 == workout_cycling_user_1.user_id
        assert 1 == workout_cycling_user_1.sport_id
        assert '2018-01-01 00:00:00' == str(
            workout_cycling_user_1.workout_date
        )
        assert 10.0 == float(workout_cycling_user_1.distance)
        assert '1:00:00' == str(workout_cycling_user_1.duration)
        assert 'Test' == workout_cycling_user_1.title
        assert '<Workout \'Cycling\' - 2018-01-01 00:00:00>' == str(
            workout_cycling_user_1
        )

        serialized_workout = workout_cycling_user_1.serialize()
        assert isinstance(decode_short_id(serialized_workout['id']), UUID)
        assert 'test' == serialized_workout['user']
        assert 1 == serialized_workout['sport_id']
        assert serialized_workout['title'] == 'Test'
        assert 'creation_date' in serialized_workout
        assert serialized_workout['modification_date'] is not None
        assert str(serialized_workout['workout_date']) == '2018-01-01 00:00:00'
        assert serialized_workout['duration'] == '1:00:00'
        assert serialized_workout['pauses'] is None
        assert serialized_workout['moving'] == '1:00:00'
        assert serialized_workout['distance'] == 10.0
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['descent'] is None
        assert serialized_workout['ascent'] is None
        assert serialized_workout['max_speed'] == 10.0
        assert serialized_workout['ave_speed'] == 10.0
        assert serialized_workout['with_gpx'] is False
        assert serialized_workout['bounds'] == []
        assert serialized_workout['previous_workout'] is None
        assert serialized_workout['next_workout'] is None
        assert serialized_workout['segments'] == []
        assert serialized_workout['records'] != []
        assert serialized_workout['map'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['notes'] is None

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

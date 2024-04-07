from datetime import timedelta

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.short_id import encode_uuid
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..utils import random_string


class TestWorkoutModel:
    def test_sport_label_and_date_are_in_string_value(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.title = 'Test'
        db.session.commit()
        assert (
            f'<Workout \'{sport_1_cycling.label}\' - 2018-01-01 00:00:00>'
            == str(workout_cycling_user_1)
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

        serialized_workout = workout.serialize()
        assert serialized_workout['ascent'] is None
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == []
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] is None
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['id'] == workout.short_id
        assert serialized_workout['equipments'] == []
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
        assert serialized_workout['user'] == workout.user.username
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

        serialized_workout = workout.serialize()
        assert serialized_workout['ascent'] == workout.ascent
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == []
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] == workout.descent
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['equipments'] == []
        assert serialized_workout['id'] == workout.short_id
        assert serialized_workout['map'] is None
        assert serialized_workout['max_alt'] is None
        assert serialized_workout['max_speed'] == float(workout.max_speed)
        assert serialized_workout['min_alt'] is None
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
        assert serialized_workout['user'] == workout.user.username
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
        workout = workout_cycling_user_1
        workout.bounds = [1, 2, 3, 4]
        workout.gpx = random_string()
        workout.map = random_string()
        workout.pauses = timedelta(minutes=15)

        serialized_workout = workout.serialize()
        assert serialized_workout['ascent'] is None
        assert serialized_workout['ave_speed'] == float(workout.ave_speed)
        assert serialized_workout['bounds'] == [
            float(bound) for bound in workout.bounds
        ]
        assert 'creation_date' in serialized_workout
        assert serialized_workout['descent'] is None
        assert serialized_workout['distance'] == float(workout.distance)
        assert serialized_workout['duration'] == str(workout.duration)
        assert serialized_workout['equipments'] == []
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
        assert serialized_workout['user'] == workout.user.username
        assert serialized_workout['weather_end'] is None
        assert serialized_workout['weather_start'] is None
        assert serialized_workout['with_gpx'] is True
        assert str(serialized_workout['workout_date']) == '2018-01-01 00:00:00'

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
        serialized_workout = workout_running_user_1.serialize()

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
        serialized_workout = workout_cycling_user_1.serialize()

        assert (
            serialized_workout['next_workout']
            == workout_running_user_1.short_id
        )

    def test_it_returns_equipments(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]

        serialized_workout = workout_cycling_user_1.serialize()

        assert serialized_workout['equipments'] == [
            equipment_bike_user_1.serialize()
        ]

    def test_it_raises_exception_when_workout_is_deleted_before_removing_equipment(  # noqa
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()

        db.session.delete(workout_cycling_user_1)
        with pytest.raises(
            Exception, match="equipments exists, remove them first"
        ):
            db.session.commit()

        equipment_bike_user_1.total_workouts = 1

    def test_it_updates_equipments_totals(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()

        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()
        assert equipment_bike_user_1.total_workouts == 0
        assert (
            equipment_shoes_user_1.total_distance
            == workout_running_user_1.distance
        )
        assert (
            equipment_shoes_user_1.total_duration
            == workout_running_user_1.duration
        )
        assert (
            equipment_shoes_user_1.total_moving
            == workout_running_user_1.moving
        )
        assert equipment_shoes_user_1.total_workouts == 1

        all_equipments = [equipment_bike_user_1, equipment_shoes_user_1]
        workout_cycling_user_1.equipments = all_equipments
        db.session.commit()

        assert (
            equipment_bike_user_1.total_distance
            == workout_cycling_user_1.distance
        )
        assert (
            equipment_bike_user_1.total_duration
            == workout_cycling_user_1.duration
        )
        assert (
            equipment_bike_user_1.total_moving == workout_cycling_user_1.moving
        )
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_shoes_user_1.total_distance == (
            workout_running_user_1.distance + workout_cycling_user_1.distance
        )
        assert equipment_shoes_user_1.total_duration == (
            workout_running_user_1.duration + workout_cycling_user_1.duration
        )
        assert equipment_shoes_user_1.total_moving == (
            workout_running_user_1.moving + workout_cycling_user_1.moving
        )
        assert equipment_shoes_user_1.total_workouts == 2

        workout_running_user_1.equipments = []
        db.session.commit()

        for equipment in all_equipments:
            assert equipment.total_distance == workout_cycling_user_1.distance
            assert equipment.total_duration == workout_cycling_user_1.duration
            assert equipment.total_moving == workout_cycling_user_1.moving
            assert equipment.total_workouts == 1

        workout_cycling_user_1.equipments = []
        db.session.commit()

        for equipment in all_equipments:
            assert equipment.total_distance == 0.0
            assert equipment.total_duration == timedelta()
            assert equipment.total_moving == timedelta()
            assert equipment.total_workouts == 0

import datetime

from flask import Flask

from fittrackee.users.models import User
from fittrackee.workouts.models import Record, Sport, Workout


class TestRecordModel:
    def test_record_model(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_ld = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='LD',
        ).first()
        assert 'test' == record_ld.user.username
        assert 1 == record_ld.sport_id
        assert 1 == record_ld.workout_id
        assert 'LD' == record_ld.record_type
        assert '2018-01-01 00:00:00' == str(record_ld.workout_date)
        assert '<Record Cycling - LD - 2018-01-01>' == str(record_ld)

        record_serialize = record_ld.serialize()
        assert 'id' in record_serialize
        assert 'user' in record_serialize
        assert 'sport_id' in record_serialize
        assert 'workout_id' in record_serialize
        assert 'record_type' in record_serialize
        assert 'workout_date' in record_serialize
        assert 'value' in record_serialize

    def test_record_model_with_none_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_ld = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='LD',
        ).first()
        record_ld.value = None
        assert 'test' == record_ld.user.username
        assert 1 == record_ld.sport_id
        assert 1 == record_ld.workout_id
        assert 'LD' == record_ld.record_type
        assert '2018-01-01 00:00:00' == str(record_ld.workout_date)
        assert '<Record Cycling - LD - 2018-01-01>' == str(record_ld)
        assert record_ld.value is None

        record_serialize = record_ld.serialize()
        assert record_serialize['value'] is None

    def test_average_speed_records(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_as = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='AS',
        ).first()

        assert isinstance(record_as.value, float)
        assert record_as.value == 10.0
        assert record_as._value == 1000

        record_serialize = record_as.serialize()
        assert record_serialize.get('value') == 10.0
        assert isinstance(record_serialize.get('value'), float)

    def test_add_farest_distance_records(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_fd = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='FD',
        ).first()

        assert isinstance(record_fd.value, float)
        assert record_fd.value == 10.0
        assert record_fd._value == 10000

        record_serialize = record_fd.serialize()
        assert record_serialize.get('value') == 10.0
        assert isinstance(record_serialize.get('value'), float)

    def test_add_longest_duration_records(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_ld = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='LD',
        ).first()

        assert isinstance(record_ld.value, datetime.timedelta)
        assert str(record_ld.value) == '1:00:00'
        assert record_ld._value == 3600

        record_serialize = record_ld.serialize()
        assert record_serialize.get('value') == '1:00:00'
        assert isinstance(record_serialize.get('value'), str)

    def test_add_longest_duration_records_with_zero(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_ld = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='LD',
        ).first()
        record_ld.value = datetime.timedelta(seconds=0)

        assert isinstance(record_ld.value, datetime.timedelta)
        assert str(record_ld.value) == '0:00:00'
        assert record_ld._value == 0

        record_serialize = record_ld.serialize()
        assert record_serialize.get('value') == '0:00:00'
        assert isinstance(record_serialize.get('value'), str)

    def test_max_speed_records_no_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        record_ms = Record.query.filter_by(
            user_id=workout_cycling_user_1.user_id,
            sport_id=workout_cycling_user_1.sport_id,
            record_type='MS',
        ).first()

        assert isinstance(record_ms.value, float)
        assert record_ms.value == 10.0
        assert record_ms._value == 1000

        record_serialize = record_ms.serialize()
        assert record_serialize.get('value') == 10.0
        assert isinstance(record_serialize.get('value'), float)

import datetime

from mpwo_api.tests.utils import add_activity, add_record, add_sport, add_user


def test_add_record(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    record = add_record(1, 1, activity, 'LD')

    assert 1 == record.id
    assert 1 == record.user_id
    assert 1 == record.sport_id
    assert 1 == record.activity_id
    assert 'LD' == record.record_type
    assert '2018-01-01 13:36:00' == str(record.activity_date)
    assert '<Record cycling - LD - 2018-01-01>' == str(record)

    record_serialize = record.serialize()
    assert 'id' in record_serialize
    assert 'user_id' in record_serialize
    assert 'sport_id' in record_serialize
    assert 'activity_id' in record_serialize
    assert 'record_type' in record_serialize
    assert 'activity_date' in record_serialize
    assert 'value' in record_serialize


def test_add_records_no_value(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    record = add_record(1, 1, activity, 'AS')

    assert record.value is None
    assert record._value is None

    record_serialize = record.serialize()
    assert record_serialize.get('value') is None


def test_add_as_records(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    record = add_record(1, 1, activity, 'AS')
    # record.value = 4.6
    record.value = 4.61

    assert isinstance(record.value, float)
    assert record.value == 4.61
    assert record._value == 461

    record_serialize = record.serialize()
    assert record_serialize.get('value') == 4.61
    assert isinstance(record_serialize.get('value'), float)


def test_add_fd_records(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    record = add_record(1, 1, activity, 'FD')
    record.value = 0.322

    assert isinstance(record.value, float)
    assert record.value == 0.322
    assert record._value == 322

    record_serialize = record.serialize()
    assert record_serialize.get('value') == 0.322
    assert isinstance(record_serialize.get('value'), float)


def test_add_ld_records(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    record = add_record(1, 1, activity, 'LD')
    record.value = activity.duration

    assert isinstance(record.value, datetime.timedelta)
    assert str(record.value) == '0:17:04'
    assert record._value == 1024

    record_serialize = record.serialize()
    assert record_serialize.get('value') == '0:17:04'
    assert isinstance(record_serialize.get('value'), str)


def test_add_ld_records_zero(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=0)
    )
    record = add_record(1, 1, activity, 'LD')
    record.value = activity.duration

    assert isinstance(record.value, datetime.timedelta)
    assert str(record.value) == '0:00:00'
    assert record._value == 0

    record_serialize = record.serialize()
    assert record_serialize.get('value') == '0:00:00'
    assert isinstance(record_serialize.get('value'), str)


def test_add_ms_records_no_value(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    record = add_record(1, 1, activity, 'MS')
    record.value = 23.5

    assert isinstance(record.value, float)
    assert record.value == 23.5
    assert record._value == 2350

    record_serialize = record.serialize()
    assert record_serialize.get('value') == 23.5
    assert isinstance(record_serialize.get('value'), float)

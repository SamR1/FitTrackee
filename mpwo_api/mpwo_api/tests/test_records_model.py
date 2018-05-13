import datetime


def test_record_model(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_ld
):
    assert 1 == record_ld.id
    assert 1 == record_ld.user_id
    assert 1 == record_ld.sport_id
    assert 1 == record_ld.activity_id
    assert 'LD' == record_ld.record_type
    assert '2018-01-01 00:00:00' == str(record_ld.activity_date)
    assert '<Record Cycling - LD - 2018-01-01>' == str(record_ld)

    record_serialize = record_ld.serialize()
    assert 'id' in record_serialize
    assert 'user_id' in record_serialize
    assert 'sport_id' in record_serialize
    assert 'activity_id' in record_serialize
    assert 'record_type' in record_serialize
    assert 'activity_date' in record_serialize
    assert 'value' in record_serialize


def test_add_record_no_value(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_as
):
    assert record_as.value is None
    assert record_as._value is None

    record_serialize = record_as.serialize()
    assert record_serialize.get('value') is None


def test_add_as_records(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_as
):
    # record.value = 4.6
    record_as.value = 4.61

    assert isinstance(record_as.value, float)
    assert record_as.value == 4.61
    assert record_as._value == 461

    record_serialize = record_as.serialize()
    assert record_serialize.get('value') == 4.61
    assert isinstance(record_serialize.get('value'), float)


def test_add_fd_records(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_fd
):
    record_fd.value = 0.322

    assert isinstance(record_fd.value, float)
    assert record_fd.value == 0.322
    assert record_fd._value == 322

    record_serialize = record_fd.serialize()
    assert record_serialize.get('value') == 0.322
    assert isinstance(record_serialize.get('value'), float)


def test_add_ld_records(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_ld
):
    record_ld.value = activity_cycling_user_1.duration

    assert isinstance(record_ld.value, datetime.timedelta)
    assert str(record_ld.value) == '0:17:04'
    assert record_ld._value == 1024

    record_serialize = record_ld.serialize()
    assert record_serialize.get('value') == '0:17:04'
    assert isinstance(record_serialize.get('value'), str)


def test_add_ld_records_zero(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_ld
):
    activity_cycling_user_1.duration = datetime.timedelta(seconds=0)
    record_ld.value = activity_cycling_user_1.duration

    assert isinstance(record_ld.value, datetime.timedelta)
    assert str(record_ld.value) == '0:00:00'
    assert record_ld._value == 0

    record_serialize = record_ld.serialize()
    assert record_serialize.get('value') == '0:00:00'
    assert isinstance(record_serialize.get('value'), str)


def test_add_ms_records_no_value(
    app,  user_1, sport_1_cycling, activity_cycling_user_1, record_ms
):
    record_ms.value = 23.5

    assert isinstance(record_ms.value, float)
    assert record_ms.value == 23.5
    assert record_ms._value == 2350

    record_serialize = record_ms.serialize()
    assert record_serialize.get('value') == 23.5
    assert isinstance(record_serialize.get('value'), float)

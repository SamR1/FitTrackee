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
    assert 'cycling - LD - 2018-01-01' == str(record)

import datetime

from mpwo_api.tests.utils import add_activity, add_sport, add_user


def test_add_activity(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018 13:36', '%d/%m/%Y %H:%M'),  # noqa
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )

    assert 1 == activity.id
    assert 1 == activity.user_id
    assert 1 == activity.sport_id
    assert '2018-01-01 13:36:00' == str(activity.activity_date)
    assert 10.0 == float(activity.distance)
    assert '0:17:04' == str(activity.duration)
    assert 'cycling - 2018-01-01 13:36:00' == str(activity)

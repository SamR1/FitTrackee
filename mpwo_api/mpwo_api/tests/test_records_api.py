import datetime
import json

from mpwo_api.tests.utils import add_activity, add_record, add_sport, add_user


def test_get_all_activities_for_authenticated_user(app):
    add_user('test', 'test@test.com', '12345678')
    add_user('toto', 'toto@toto.com', '12345678')
    add_sport('cycling')
    add_sport('running')

    activity = add_activity(
        user_id=1,
        sport_id=2,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    add_record(1, 2, activity, 'LD')

    activity = add_activity(
        user_id=2,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/01/2018', '%d/%m/%Y'),
        distance=15,
        duration=datetime.timedelta(seconds=3600),
    )
    add_record(2, 1, activity, 'MS')

    activity = add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=12,
        duration=datetime.timedelta(seconds=6000)
    )
    add_record(1, 1, activity, 'FD')

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.get(
        '/api/records',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert len(data['data']['records']) == 2

    assert 'Sun, 01 Apr 2018 00:00:00 GMT' == data['data']['records'][0]['activity_date']  # noqa
    assert 1 == data['data']['records'][0]['user_id']
    assert 1 == data['data']['records'][0]['sport_id']
    assert 3 == data['data']['records'][0]['activity_id']
    assert 'FD' == data['data']['records'][0]['record_type']
    assert 'value_interval' in data['data']['records'][0]
    assert 'value_float' in data['data']['records'][0]

    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['records'][1]['activity_date']  # noqa
    assert 1 == data['data']['records'][1]['user_id']
    assert 2 == data['data']['records'][1]['sport_id']
    assert 1 == data['data']['records'][1]['activity_id']
    assert 'LD' == data['data']['records'][1]['record_type']
    assert 'value_interval' in data['data']['records'][1]
    assert 'value_float' in data['data']['records'][1]

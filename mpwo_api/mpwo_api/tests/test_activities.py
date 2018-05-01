import datetime
import json

from mpwo_api.tests.utils import add_activity, add_sport, add_user


def test_get_all_activities(app):
    add_user('test', 'test@test.com', '12345678')
    add_user('toto', 'toto@toto.com', '12345678')
    add_sport('cycling')
    add_sport('running')
    add_activity(
        1,
        2,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))
    add_activity(
        2,
        1,
        datetime.datetime.strptime('23/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=3600))

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
        '/api/activities',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert len(data['data']['activities']) == 2
    assert 'creation_date' in data['data']['activities'][0]
    assert 'creation_date' in data['data']['activities'][1]
    assert 'Tue, 23 Jan 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa
    assert 'creation_date' in data['data']['activities'][1]
    assert 2 == data['data']['activities'][0]['user_id']
    assert 1 == data['data']['activities'][1]['user_id']
    assert 1 == data['data']['activities'][0]['sport_id']
    assert 2 == data['data']['activities'][1]['sport_id']
    assert 3600 == data['data']['activities'][0]['duration']
    assert 1024 == data['data']['activities'][1]['duration']


import datetime
import json

from mpwo_api.tests.utils import add_activity, add_sport, add_user


def test_get_all_activities_for_authenticated_user(app):
    add_user('test', 'test@test.com', '12345678')
    add_user('toto', 'toto@toto.com', '12345678')
    add_sport('cycling')
    add_sport('running')
    add_activity(
        user_id=1,
        sport_id=2,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    add_activity(
        user_id=2,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/01/2018', '%d/%m/%Y'),
        distance=15,
        duration=datetime.timedelta(seconds=3600),
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=12,
        duration=datetime.timedelta(seconds=6000)
    )

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
    assert 'Sun, 01 Apr 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 1 == data['data']['activities'][0]['user_id']
    assert 1 == data['data']['activities'][0]['sport_id']
    assert 12.0 == data['data']['activities'][0]['distance']
    assert '1:40:00' == data['data']['activities'][0]['duration']

    assert 'creation_date' in data['data']['activities'][1]
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa
    assert 1 == data['data']['activities'][1]['user_id']
    assert 2 == data['data']['activities'][1]['sport_id']
    assert 10.0 == data['data']['activities'][1]['distance']
    assert '0:17:04' == data['data']['activities'][1]['duration']


def test_get_activities_for_authenticated_user_no_activity(app):
    add_user('test', 'test@test.com', '12345678')
    add_user('toto', 'toto@toto.com', '12345678')
    add_sport('cycling')
    add_sport('running')
    add_activity(
        user_id=1,
        sport_id=2,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=12,
        duration=datetime.timedelta(seconds=6000)
    )

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='toto@toto.com',
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
    assert len(data['data']['activities']) == 0


def test_get_activities_for_authenticated_user_no_authentication(app):
    client = app.test_client()
    response = client.get('/api/activities')
    data = json.loads(response.data.decode())

    assert response.status_code == 403
    assert 'error' in data['status']
    assert 'Provide a valid auth token.' in data['message']


def test_get_activities_pagination(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        distance=8,
        duration=datetime.timedelta(seconds=6000)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('20/03/2017', '%d/%m/%Y'),
        distance=5,
        duration=datetime.timedelta(seconds=1024)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('09/05/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3000)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/06/2017', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=3456)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        distance=1,
        duration=datetime.timedelta(seconds=600)
    )
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1000)
    )

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
    assert len(data['data']['activities']) == 5
    assert 'creation_date' in data['data']['activities'][0]
    assert 'Wed, 09 May 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert '0:50:00' == data['data']['activities'][0]['duration']
    assert 'creation_date' in data['data']['activities'][4]
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][4]['activity_date']  # noqa
    assert '0:17:04' == data['data']['activities'][4]['duration']

    response = client.get(
        '/api/activities?page=1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert len(data['data']['activities']) == 5
    assert 'creation_date' in data['data']['activities'][0]
    assert 'Wed, 09 May 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert '0:50:00' == data['data']['activities'][0]['duration']
    assert 'creation_date' in data['data']['activities'][4]
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][4]['activity_date']  # noqa
    assert '0:17:04' == data['data']['activities'][4]['duration']

    response = client.get(
        '/api/activities?page=2',
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
    assert 'Thu, 01 Jun 2017 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert '0:57:36' == data['data']['activities'][0]['duration']
    assert 'creation_date' in data['data']['activities'][1]
    assert 'Mon, 20 Mar 2017 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa
    assert '0:17:04' == data['data']['activities'][1]['duration']

    response = client.get(
        '/api/activities?page=3',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert len(data['data']['activities']) == 0

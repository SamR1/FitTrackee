import datetime
import json

from mpwo_api.tests.utils import add_activity, add_admin, add_sport, add_user


def test_get_all_sports(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_sport('running')

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
        '/api/sports',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['sports']) == 2
    assert 'cycling' in data['data']['sports'][0]['label']
    assert 'running' in data['data']['sports'][1]['label']


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


def test_get_a_sport(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

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
        '/api/sports/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['sports']) == 1
    assert 'cycling' in data['data']['sports'][0]['label']


def test_add_a_sport(app):
    add_admin()

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='admin@example.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.post(
        '/api/sports',
        content_type='application/json',
        data=json.dumps(dict(
            label='surfing'
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert 'created' in data['status']

    assert len(data['data']['sports']) == 1
    assert 'surfing' in data['data']['sports'][0]['label']


def test_add_a_sport_not_admin(app):
    add_user('test', 'test@test.com', '12345678')

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.post(
        '/api/sports',
        content_type='application/json',
        data=json.dumps(dict(
            label='surfing'
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 401
    assert 'created' not in data['status']
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_update_a_sport(app):
    add_admin()
    add_sport('cycling')

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='admin@example.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.patch(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict(
            label='cycling updated'
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['sports']) == 1
    assert 'cycling updated' in data['data']['sports'][0]['label']


def test_update_a_sport_not_admin(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.patch(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict(
            label='cycling updated'
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 401
    assert 'success' not in data['status']
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_delete_a_sport(app):
    add_admin()
    add_sport('cycling')

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='admin@example.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.delete(
        '/api/sports/1',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    assert response.status_code == 204


def test_delete_a_sport_not_admin(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='test@test.com',
            password='12345678'
        )),
        content_type='application/json'
    )
    response = client.delete(
        '/api/sports/1',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())
    assert response.status_code == 401
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']

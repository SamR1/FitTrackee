import datetime
import json
from io import BytesIO

from mpwo_api.tests.utils import add_activity, add_sport, add_user
from mpwo_api.tests.utils_gpx import gpx_file


def test_edit_an_activity_with_gpx(app):
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
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=2,
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
    assert len(data['data']['activities']) == 1

    assert 'creation_date' in data['data']['activities'][0]
    assert 'Tue, 13 Mar 2018 12:44:45 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 1 == data['data']['activities'][0]['user_id']
    assert 2 == data['data']['activities'][0]['sport_id']
    assert '0:04:10' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] == 0.4
    assert data['data']['activities'][0]['ave_speed'] == 4.602
    assert data['data']['activities'][0]['descent'] == 23.4
    assert data['data']['activities'][0]['distance'] == 0.32
    assert data['data']['activities'][0]['max_alt'] == 998.0
    assert data['data']['activities'][0]['max_speed'] == 5.086
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:04:10'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is True


def test_edit_an_activity_with_gpx_invalid_payload(app):
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
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict()),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'error' in data['status']
    assert 'Invalid payload.' in data['message']


def test_edit_an_activity_with_gpx_incorrect_data(app):
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
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=2,
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error. Please try again or contact the administrator.' in data['message']  # noqa


def test_edit_an_activity_wo_gpx(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
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
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=1,
            duration=3600,
            activity_date='2018-05-15 14:05',
            distance=10
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
    assert len(data['data']['activities']) == 1
    assert 'creation_date' in data['data']['activities'][0]
    assert data['data']['activities'][0]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'  # noqa
    assert data['data']['activities'][0]['user_id'] == 1
    assert data['data']['activities'][0]['sport_id'] == 1
    assert data['data']['activities'][0]['duration'] == '1:00:00'
    assert data['data']['activities'][0]['ascent'] is None
    assert data['data']['activities'][0]['ave_speed'] == 10.0
    assert data['data']['activities'][0]['descent'] is None
    assert data['data']['activities'][0]['distance'] == 10.0
    assert data['data']['activities'][0]['max_alt'] is None
    assert data['data']['activities'][0]['max_speed'] == 10.0
    assert data['data']['activities'][0]['min_alt'] is None
    assert data['data']['activities'][0]['moving'] == '1:00:00'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is False


def test_edit_an_activity_wo_gpx_partial(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
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
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=1,
            distance=10
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
    assert len(data['data']['activities']) == 1
    assert 'creation_date' in data['data']['activities'][0]
    assert data['data']['activities'][0]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'  # noqa
    assert data['data']['activities'][0]['user_id'] == 1
    assert data['data']['activities'][0]['sport_id'] == 1
    assert data['data']['activities'][0]['duration'] == '0:17:04'
    assert data['data']['activities'][0]['ascent'] is None
    assert data['data']['activities'][0]['ave_speed'] == 35.156
    assert data['data']['activities'][0]['descent'] is None
    assert data['data']['activities'][0]['distance'] == 10.0
    assert data['data']['activities'][0]['max_alt'] is None
    assert data['data']['activities'][0]['max_speed'] == 35.156
    assert data['data']['activities'][0]['min_alt'] is None
    assert data['data']['activities'][0]['moving'] is None  # no calculated
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is False


def test_edit_an_activity_wo_gpx_invalid_payload(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
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
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict()),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'error' in data['status']
    assert 'Invalid payload.' in data['message']


def test_edit_an_activity_wo_gpx_incorrect_data(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        user_id=1,
        sport_id=1,
        activity_date=datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        distance=10,
        duration=datetime.timedelta(seconds=1024)
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
    response = client.patch(
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=1,
            duration=3600,
            activity_date='15/2018',
            distance=10
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error. Please try again or contact the administrator.' \
           in data['message']


def test_edit_an_activity_no_activity(app):
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
        '/api/activities/1',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=1,
            duration=3600,
            activity_date='2018-05-15 14:05',
            distance=10
        )),
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert len(data['data']['activities']) == 0

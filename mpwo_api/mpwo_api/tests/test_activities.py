import datetime
import json
import os
from io import BytesIO

from mpwo_api.tests.utils import (
    add_activity, add_sport, add_user, get_gpx_filepath
)
from mpwo_api.tests.utils_gpx import gpx_file


def test_get_all_activities_for_authenticated_user(app):
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
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=6000))

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
    assert '1:40:00' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['with_gpx'] is False

    assert 'creation_date' in data['data']['activities'][1]
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa
    assert 1 == data['data']['activities'][1]['user_id']
    assert 2 == data['data']['activities'][1]['sport_id']
    assert '0:17:04' == data['data']['activities'][1]['duration']
    assert data['data']['activities'][1]['with_gpx'] is False


def test_get_activities_for_authenticated_user_no_activity(app):
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
        1,
        1,
        datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=6000))

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
        1,
        1,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/04/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=6000))
    add_activity(
        1,
        1,
        datetime.datetime.strptime('20/03/2017', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))
    add_activity(
        1,
        1,
        datetime.datetime.strptime('09/05/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=3000))
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/06/2017', '%d/%m/%Y'),
        datetime.timedelta(seconds=3456))
    add_activity(
        1,
        1,
        datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=600))
    add_activity(
        1,
        1,
        datetime.datetime.strptime('23/02/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1000))

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


def test_add_an_activity_gpx(app):
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
    response = client.post(
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
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert 'created' in data['status']
    assert len(data['data']['activities']) == 1
    assert 'creation_date' in data['data']['activities'][0]
    assert 'Tue, 13 Mar 2018 12:44:45 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 1 == data['data']['activities'][0]['user_id']
    assert 1 == data['data']['activities'][0]['sport_id']
    assert '0:04:10' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] == 0.4
    assert data['data']['activities'][0]['ave_speed'] == 4.6
    assert data['data']['activities'][0]['descent'] == 23.4
    assert data['data']['activities'][0]['distance'] == 0.32
    assert data['data']['activities'][0]['max_alt'] == 998.0
    assert data['data']['activities'][0]['max_speed'] == 5.09
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:04:10'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is True


def test_add_an_activity_gpx_invalid_file(app):
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
    response = client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.png'),
            data='{"sport_id": 1}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert data['status'] == 'fail'
    assert data['message'] == 'File extension not allowed.'


def test_add_an_activity_gpx_no_sport_id(app):
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
    response = client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid payload.'


def test_add_an_activity_gpx_no_file(app):
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
    response = client.post(
        '/api/activities',
        data=dict(
            data='{}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert data['status'] == 'fail'
    assert data['message'] == 'No file part.'


def test_add_an_activity_no_gpx(app):
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
    response = client.post(
        '/api/activities/no_gpx',
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

    assert response.status_code == 201
    assert 'created' in data['status']
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


def test_add_an_activity_no_gpx_invalid_payload(app):
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
    response = client.post(
        '/api/activities/no_gpx',
        content_type='application/json',
        data=json.dumps(dict(
            sport_id=1,
            duration=3600,
            distance=10
        )),
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


def test_add_an_activity_no_gpx_error(app):
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
    response = client.post(
        '/api/activities/no_gpx',
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
    assert 'fail' in data['status']
    assert 'Error during activity save.' in data['message']


def test_get_an_activity_without_gpx(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))

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
        '/api/activities/1',
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
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 1 == data['data']['activities'][0]['user_id']
    assert 1 == data['data']['activities'][0]['sport_id']
    assert '0:17:04' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] is None
    assert data['data']['activities'][0]['ave_speed'] is None
    assert data['data']['activities'][0]['descent'] is None
    assert data['data']['activities'][0]['distance'] is None
    assert data['data']['activities'][0]['max_alt'] is None
    assert data['data']['activities'][0]['max_speed'] is None
    assert data['data']['activities'][0]['min_alt'] is None
    assert data['data']['activities'][0]['moving'] is None
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is False


def test_get_an_activity_with_gpx(app):
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
    response = client.get(
        '/api/activities/1',
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
    assert 1 == data['data']['activities'][0]['sport_id']
    assert '0:04:10' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] == 0.4
    assert data['data']['activities'][0]['ave_speed'] == 4.6
    assert data['data']['activities'][0]['descent'] == 23.4
    assert data['data']['activities'][0]['distance'] == 0.32
    assert data['data']['activities'][0]['max_alt'] == 998.0
    assert data['data']['activities'][0]['max_speed'] == 5.09
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:04:10'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is True


def test_edit_an_activity_wo_gpx(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))

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


def test_edit_an_activity_with_gpx(app):
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

    assert response.status_code == 500
    assert 'error' in data['status']
    assert ('You can not modify an activity with gpx file. '
            'Please delete and re-import the gpx file.') in data['message']


def test_edit_an_activity_wo_gpx_invalid_payload(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))

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

    assert response.status_code == 400
    assert 'error' in data['status']
    assert 'Invalid payload.' in data['message']


def test_edit_an_activity_wo_gpx_incorrect_data(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))

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


def test_delete_an_activity_with_gpx(app):
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
    response = client.delete(
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    assert response.status_code == 204


def test_delete_an_activity_wo_gpx(app):
    add_user('test', 'test@test.com', '12345678')
    add_sport('cycling')
    add_activity(
        1,
        1,
        datetime.datetime.strptime('01/01/2018', '%d/%m/%Y'),
        datetime.timedelta(seconds=1024))

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
        '/api/activities/1',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    assert response.status_code == 204


def test_delete_an_activity_no_activityy(app):
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
    response = client.delete(
        '/api/activities/9999',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']


def test_delete_an_activity_with_gpx_invalid_file(app):
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

    gpx_filepath = get_gpx_filepath(1)
    os.remove(gpx_filepath)

    response = client.delete(
        '/api/activities/1',
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

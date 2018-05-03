import datetime
import json
from io import BytesIO

from mpwo_api.tests.utils import add_activity, add_sport, add_user

gpx_file = (
    '<?xml version=\'1.0\' encoding=\'UTF-8\'?>'
    '<gpx xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns="http://www.topografix.com/GPX/1/1">'  # noqa
    '  <metadata/>'
    '  <trk>'
    '    <trkseg>'
    '      <trkpt lat="77.2261324" lon="-42.1223054">'
    '        <time>2015-09-20T13:48:44+00:00</time>'
    '      </trkpt>'
    '      <trkpt lat="77.2261324" lon="-42.1223054">'
    '        <time>2015-09-20T13:48:46+00:00</time>'
    '        <ele>223.28399658203125</ele>'
    '      </trkpt>'
    '      <trkpt lat="77.2261324" lon="-42.1223054">'
    '        <time>2015-09-20T13:48:46+00:00</time>'
    '      </trkpt>'
    '    </trkseg>'
    '  </trk>'
    '</gpx>'
)


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
    assert '1:00:00' == data['data']['activities'][0]['duration']
    assert '0:17:04' == data['data']['activities'][1]['duration']


def test_add_an_activity(app):
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


def test_add_an_activity_invalid_file(app):
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


def test_add_an_activity_no_sport_id(app):
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


def test_add_an_activity_no_file(app):
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

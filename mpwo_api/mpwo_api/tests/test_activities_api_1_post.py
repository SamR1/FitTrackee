import json
from io import BytesIO


def assert_activity_data_with_gpx(data):
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
    assert data['data']['activities'][0]['max_speed'] == 5.11
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:04:10'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is True
    assert len(data['data']['activities'][0]['segments']) == 1

    segment = data['data']['activities'][0]['segments'][0]
    assert segment['activity_id'] == 1
    assert segment['segment_id'] == 0
    assert segment['duration'] == '0:04:10'
    assert segment['ascent'] == 0.4
    assert segment['ave_speed'] == 4.6
    assert segment['descent'] == 23.4
    assert segment['distance'] == 0.32
    assert segment['max_alt'] == 998.0
    assert segment['max_speed'] == 5.11
    assert segment['min_alt'] == 975.0
    assert segment['moving'] == '0:04:10'
    assert segment['pauses'] is None

    records = data['data']['activities'][0]['records']
    assert len(records) == 4
    assert records[0]['sport_id'] == 1
    assert records[0]['activity_id'] == 1
    assert records[0]['record_type'] == 'MS'
    assert records[0]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == 5.11
    assert records[1]['sport_id'] == 1
    assert records[1]['activity_id'] == 1
    assert records[1]['record_type'] == 'LD'
    assert records[1]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == '0:04:10'
    assert records[2]['sport_id'] == 1
    assert records[2]['activity_id'] == 1
    assert records[2]['record_type'] == 'FD'
    assert records[2]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[2]['value'] == 0.32
    assert records[3]['sport_id'] == 1
    assert records[3]['activity_id'] == 1
    assert records[3]['record_type'] == 'AS'
    assert records[3]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 4.6


def assert_activity_data_wo_gpx(data):
    assert 'creation_date' in data['data']['activities'][0]
    assert data['data']['activities'][0]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'  # noqa
    assert data['data']['activities'][0]['user_id'] == 1
    assert data['data']['activities'][0]['sport_id'] == 1
    assert data['data']['activities'][0]['duration'] == '1:00:00'
    assert data['data']['activities'][0]['title'] == 'Cycling - 2018-05-15 14:05:00'  # noqa
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

    assert len(data['data']['activities'][0]['segments']) == 0

    records = data['data']['activities'][0]['records']
    assert len(records) == 4
    assert records[0]['sport_id'] == 1
    assert records[0]['activity_id'] == 1
    assert records[0]['record_type'] == 'MS'
    assert records[0]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[0]['value'] == 10.0
    assert records[1]['sport_id'] == 1
    assert records[1]['activity_id'] == 1
    assert records[1]['record_type'] == 'LD'
    assert records[1]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[1]['value'] == '1:00:00'
    assert records[2]['sport_id'] == 1
    assert records[2]['activity_id'] == 1
    assert records[2]['record_type'] == 'FD'
    assert records[2]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[2]['value'] == 10.0
    assert records[3]['sport_id'] == 1
    assert records[3]['activity_id'] == 1
    assert records[3]['record_type'] == 'AS'
    assert records[3]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[3]['value'] == 10.0


def test_add_an_activity_gpx(app, user_1, sport_1_cycling, gpx_file):
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
    assert 'just an activity' == data['data']['activities'][0]['title']
    assert_activity_data_with_gpx(data)


def test_add_an_activity_with_gpx(app, user_1, sport_1_cycling, gpx_file):
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
    assert 'just an activity' == data['data']['activities'][0]['title']
    assert_activity_data_with_gpx(data)


def test_add_an_activity_with_gpx_without_name(
    app, user_1, sport_1_cycling, gpx_file_wo_name
):
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
            file=(BytesIO(str.encode(gpx_file_wo_name)), 'example.gpx'),
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
    assert 'Cycling - 2018-03-13 12:44:45' == data['data']['activities'][0]['title']  # noqa
    assert_activity_data_with_gpx(data)


def test_add_an_activity_with_gpx_invalid_file(
    app, user_1, sport_1_cycling, gpx_file_wo_track
):
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
            file=(BytesIO(str.encode(gpx_file_wo_track)), 'example.gpx'),
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

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error during gpx file parsing.' in data['message']
    assert 'data' not in data


def test_add_an_activity_gpx_invalid_extension(
    app, user_1, sport_1_cycling, gpx_file
):
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


def test_add_an_activity_gpx_no_sport_id(
    app, user_1, sport_1_cycling, gpx_file
):
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


def test_add_an_activity_gpx_incorrect_sport_id(
    app, user_1, sport_1_cycling, gpx_file
):
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
            data='{"sport_id": 2}'
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert data['status'] == 'error'
    assert data['message'] == \
        'Error during activity file save.'


def test_add_an_activity_gpx_no_file(app, user_1, sport_1_cycling):
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


def test_add_an_activity_no_gpx(app, user_1, sport_1_cycling):
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
    assert_activity_data_wo_gpx(data)


def test_get_an_activity_wo_gpx(app, user_1, sport_1_cycling):
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
    assert_activity_data_wo_gpx(data)


def test_add_an_activity_no_gpx_invalid_payload(app, user_1, sport_1_cycling):
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


def test_add_an_activity_no_gpx_error(app, user_1, sport_1_cycling):
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


def test_add_activity_zero_value(
    app, user_1, sport_1_cycling, sport_2_running
):
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
            duration=0,
            activity_date='2018-05-14 14:05',
            distance=0,
            title='Activity test'
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
    assert data['data']['activities'][0]['activity_date'] == 'Mon, 14 May 2018 14:05:00 GMT'  # noqa
    assert data['data']['activities'][0]['user_id'] == 1
    assert data['data']['activities'][0]['sport_id'] == 1
    assert data['data']['activities'][0]['duration'] is None
    assert data['data']['activities'][0]['title'] == 'Activity test'  # noqa
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

    assert len(data['data']['activities'][0]['segments']) == 0
    assert len(data['data']['activities'][0]['records']) == 0

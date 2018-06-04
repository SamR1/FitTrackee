import json


def test_get_all_activities_for_authenticated_user(
    app, user_1, user_2, sport_1_cycling, sport_2_running,
    activity_cycling_user_1, activity_cycling_user_2, activity_running_user_1,
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
    assert 2 == data['data']['activities'][0]['sport_id']
    assert 12.0 == data['data']['activities'][0]['distance']
    assert '1:40:00' == data['data']['activities'][0]['duration']

    assert 'creation_date' in data['data']['activities'][1]
    assert 'Mon, 01 Jan 2018 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa
    assert 1 == data['data']['activities'][1]['user_id']
    assert 1 == data['data']['activities'][1]['sport_id']
    assert 10.0 == data['data']['activities'][1]['distance']
    assert '0:17:04' == data['data']['activities'][1]['duration']


def test_get_activities_for_authenticated_user_no_activity(
    app, user_1, user_2, sport_1_cycling, sport_2_running,
    activity_cycling_user_1, activity_running_user_1,
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(
            email='toto@toto.com',
            password='87654321'
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

    assert response.status_code == 401
    assert 'error' in data['status']
    assert 'Provide a valid auth token.' in data['message']


def test_get_activities_pagination(
    app, user_1, sport_1_cycling, seven_activities_user_1
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


def test_get_activities_pagination_error(
    app, user_1, sport_1_cycling, seven_activities_user_1
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
    response = client.get(
        '/api/activities?page=A',
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


def test_get_activities_date_filter(
    app, user_1, sport_1_cycling, seven_activities_user_1
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
    response = client.get(
        '/api/activities?from=2018-02-01&to=2018-02-28',
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
    assert 'Fri, 23 Feb 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert '0:10:00' == data['data']['activities'][0]['duration']
    assert 'creation_date' in data['data']['activities'][1]
    assert 'Fri, 23 Feb 2018 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa
    assert '0:16:40' == data['data']['activities'][1]['duration']


def test_get_activities_date_filter_no_results(
    app, user_1, sport_1_cycling, seven_activities_user_1
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
    response = client.get(
        '/api/activities?from=2018-03-01&to=2018-03-30',
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


def test_get_activities_date_filter_from(
    app, user_1, sport_1_cycling, seven_activities_user_1
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
    response = client.get(
        '/api/activities?from=2018-04-01',
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
    assert 'Wed, 09 May 2018 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 'Sun, 01 Apr 2018 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa


def test_get_activities_date_filter_to(
    app, user_1, sport_1_cycling, seven_activities_user_1
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
    response = client.get(
        '/api/activities?to=2017-12-31',
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
    assert 'Thu, 01 Jun 2017 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 'Mon, 20 Mar 2017 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa


def test_get_activities_date_filter_paginate(
    app, user_1, sport_1_cycling, seven_activities_user_1
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
    response = client.get(
        '/api/activities?from=2017-01-01&page=2',
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
    assert 'Thu, 01 Jun 2017 00:00:00 GMT' == data['data']['activities'][0]['activity_date']  # noqa
    assert 'Mon, 20 Mar 2017 00:00:00 GMT' == data['data']['activities'][1]['activity_date']  # noqa


def test_get_an_activity(
    app, user_1, sport_1_cycling, activity_cycling_user_1
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
    assert 10.0 == data['data']['activities'][0]['distance']
    assert '0:17:04' == data['data']['activities'][0]['duration']


def test_get_an_activity_invalid_id(app, user_1):
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
        '/api/activities/11',
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


def test_get_an_activity_no_actvity_no_gpx(app, user_1):
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
        '/api/activities/11/gpx',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'Activity not found (id: 11)' in data['message']
    assert data['data']['gpx'] == ''

    response = client.get(
        '/api/activities/11/chart_data',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'Activity not found (id: 11)' in data['message']
    assert data['data']['chart_data'] == ''


def test_get_an_activity_activity_no_gpx(
        app, user_1, sport_1_cycling, activity_cycling_user_1
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
    response = client.get(
        '/api/activities/1/gpx',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'fail' in data['status']
    assert 'No gpx file for this activity (id: 1)' in data['message']

    response = client.get(
        '/api/activities/1/chart_data',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'fail' in data['status']
    assert 'No gpx file for this activity (id: 1)' in data['message']


def test_get_an_activity_activity_invalid_gpx(
        app, user_1, sport_1_cycling, activity_cycling_user_1
):
    activity_cycling_user_1.gpx = "some path"
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
        '/api/activities/1/gpx',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'internal error' in data['message']
    assert data['data']['gpx'] == ''

    response = client.get(
        '/api/activities/1/chart_data',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'internal error' in data['message']
    assert data['data']['chart_data'] == ''


def test_get_map_no_activity(
        app, user_1
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
    response = client.get(
        '/api/activities/map/123',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'Map does not exist' in data['message']

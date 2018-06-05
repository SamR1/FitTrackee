import json


def test_get_stats_no_activities(app, user_1):
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
        f'/api/stats/{user_1.id}/by_week',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == {}


def test_get_stats_no_user(app, user_1):
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
        f'/api/stats/1000/by_week',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist.' in data['message']


def test_get_stats_all_activities(
    app, user_1, sport_1_cycling, sport_2_running,
    activity_cycling_user_1, activity_running_user_1
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
        f'/api/stats/{user_1.id}/by_week',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics']['W00'] == \
        {
            'Cycling':
                {
                    'nb_activities': 1,
                    'total_distance': 10.0,
                    'total_duration': 1024
                }
        }

    assert data['data']['statistics']['W13'] == \
        {
            'Running':
                {
                    'nb_activities': 1,
                    'total_distance': 12.0,
                    'total_duration': 6000
                }
        }


def test_get_stats_all_activities_week_13(
    app, user_1, sport_1_cycling, sport_2_running,
    activity_cycling_user_1, activity_running_user_1
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
        f'/api/stats/{user_1.id}/by_week?from=2018-04-01&to=2018-04-30',
        headers=dict(
            Authorization='Bearer ' + json.loads(
                resp_login.data.decode()
            )['auth_token']
        )
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['statistics'] == \
        {
            'W13':
                {
                    'Running':
                        {
                            'nb_activities': 1,
                            'total_distance': 12.0,
                            'total_duration': 6000
                        }
                }
        }


def test_get_stats_all_activities_error(
    app, user_1, sport_1_cycling, sport_2_running,
    activity_cycling_user_1, activity_running_user_1
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
        f'/api/stats/{user_1.id}/by_week?from="2018-04-01&to=2018-04-30',
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

import json

expected_sport_1_cycling_result = {
    'id': 1,
    'label': 'Cycling',
    'img': None,
    '_can_be_deleted': True,
}

expected_sport_2_running_result = {
    'id': 2,
    'label': 'Running',
    'img': None,
    '_can_be_deleted': True,
}


def test_get_all_sports(app, user_1, sport_1_cycling, sport_2_running):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/sports',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['sports']) == 2
    assert data['data']['sports'][0] == expected_sport_1_cycling_result
    assert data['data']['sports'][1] == expected_sport_2_running_result


def test_get_a_sport(app, user_1, sport_1_cycling):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/sports/1',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['sports']) == 1
    assert data['data']['sports'][0] == expected_sport_1_cycling_result


def test_get_a_sport_invalid(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/sports/1',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert len(data['data']['sports']) == 0


def test_add_a_sport(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/sports',
        content_type='application/json',
        data=json.dumps(dict(label='Cycling')),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert 'created' in data['status']

    assert len(data['data']['sports']) == 1
    assert data['data']['sports'][0] == expected_sport_1_cycling_result


def test_add_a_sport_not_admin(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/sports',
        content_type='application/json',
        data=json.dumps(dict(label='surfing')),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 403
    assert 'created' not in data['status']
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_add_a_sport_invalid_payload(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/sports',
        content_type='application/json',
        data=json.dumps(dict()),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'error' in data['status']
    assert 'Invalid payload.' in data['message']


def test_update_a_sport(app, user_1_admin, sport_1_cycling):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict(label='cycling updated')),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['sports']) == 1
    assert 'cycling updated' in data['data']['sports'][0]['label']


def test_update_a_sport_not_admin(app, user_1, sport_1_cycling):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict(label='cycling updated')),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 403
    assert 'success' not in data['status']
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_update_a_sport_invalid_payload(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict()),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 400
    assert 'error' in data['status']
    assert 'Invalid payload.' in data['message']


def test_update_a_sport_invalid_id(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict(label='cycling updated')),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert len(data['data']['sports']) == 0


def test_delete_a_sport(app, user_1_admin, sport_1_cycling):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/sports/1',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    assert response.status_code == 204


def test_delete_a_sport_not_admin(app, user_1, sport_1_cycling):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/sports/1',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    data = json.loads(response.data.decode())
    assert response.status_code == 403
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_delete_a_sport_invalid_id(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/sports/1',
        content_type='application/json',
        data=json.dumps(dict()),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert len(data['data']['sports']) == 0


def test_delete_a_sport_with_an_activity(
    app, user_1_admin, sport_1_cycling, activity_cycling_user_1
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/sports/1',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error. Associated activities exist.' in data['message']

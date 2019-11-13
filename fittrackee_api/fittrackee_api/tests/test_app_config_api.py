import json


def test_get_config(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/config',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert data['data']['gpx_limit_import'] == 10
    assert data['data']['is_registration_enabled'] is True
    assert data['data']['max_single_file_size'] == 1048576
    assert data['data']['max_zip_file_size'] == 10485760
    assert data['data']['max_users'] == 100


def test_get_config_no_config(app_no_config, user_1_admin):
    client = app_no_config.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/config',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error on getting configuration.' in data['message']


def test_get_config_several_config(app, app_config, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/config',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error on getting configuration.' in data['message']


def test_update_config_as_admin(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/config',
        content_type='application/json',
        data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['gpx_limit_import'] == 100
    assert data['data']['is_registration_enabled'] is True
    assert data['data']['max_single_file_size'] == 1048576
    assert data['data']['max_zip_file_size'] == 10485760
    assert data['data']['max_users'] == 10


def test_update_full_config_as_admin(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/config',
        content_type='application/json',
        data=json.dumps(
            dict(
                gpx_limit_import=20,
                max_single_file_size=10000,
                max_zip_file_size=25000,
                max_users=50,
            )
        ),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert data['data']['gpx_limit_import'] == 20
    assert data['data']['is_registration_enabled'] is True
    assert data['data']['max_single_file_size'] == 10000
    assert data['data']['max_zip_file_size'] == 25000
    assert data['data']['max_users'] == 50


def test_update_config_not_admin(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/config',
        content_type='application/json',
        data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
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


def test_update_config_invalid_payload(app, user_1_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/config',
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


def test_update_config_no_config(app_no_config, user_1_admin):
    client = app_no_config.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/config',
        content_type='application/json',
        data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert 'Error on updating configuration.' in data['message']

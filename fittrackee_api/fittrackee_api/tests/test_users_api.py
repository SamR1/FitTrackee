import json

from fittrackee_api.users.models import User


def test_ping(app):
    """ => Ensure the /ping route behaves correctly."""
    client = app.test_client()
    response = client.get('/api/ping')
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert 'pong' in data['message']
    assert 'success' in data['status']


def test_single_user(app, user_1):
    """=> Get single user details"""
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        f'/api/users/{user_1.id}',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['data'] is not None
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert data['data']['created_at']
    assert not data['data']['admin']
    assert data['data']['first_name'] is None
    assert data['data']['last_name'] is None
    assert data['data']['birth_date'] is None
    assert data['data']['bio'] is None
    assert data['data']['location'] is None
    assert data['data']['timezone'] is None
    assert data['data']['nb_activities'] == 0
    assert data['data']['nb_sports'] == 0
    assert data['data']['total_distance'] == 0
    assert data['data']['total_duration'] == '0:00:00'


def test_single_user_with_activities(
    app,
    user_1,
    sport_1_cycling,
    sport_2_running,
    activity_cycling_user_1,
    activity_running_user_1,
):
    """=> Get single user details"""
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        f'/api/users/{user_1.id}',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert data['data'] is not None
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert data['data']['created_at']
    assert not data['data']['admin']
    assert data['data']['first_name'] is None
    assert data['data']['last_name'] is None
    assert data['data']['birth_date'] is None
    assert data['data']['bio'] is None
    assert data['data']['location'] is None
    assert data['data']['timezone'] is None
    assert data['data']['nb_activities'] == 2
    assert data['data']['nb_sports'] == 2
    assert data['data']['total_distance'] == 22
    assert data['data']['total_duration'] == '1:57:04'


def test_single_user_no_id(app, user_1):
    """=> Ensure error is thrown if an id is not provided."""
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/users/blah',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist.' in data['message']


def test_single_user_wrong_id(app, user_1):
    """=> Ensure error is thrown if the id does not exist."""
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/users/99999999999',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist.' in data['message']


def test_users_list(app, user_1, user_2):
    """=> Ensure get single user behaves correctly."""

    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/users',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert len(data['data']['users']) == 2
    assert 'created_at' in data['data']['users'][0]
    assert 'created_at' in data['data']['users'][1]
    assert 'test' in data['data']['users'][0]['username']
    assert 'toto' in data['data']['users'][1]['username']
    assert 'test@test.com' in data['data']['users'][0]['email']
    assert 'toto@toto.com' in data['data']['users'][1]['email']
    assert data['data']['users'][0]['timezone'] is None
    assert data['data']['users'][0]['nb_activities'] == 0
    assert data['data']['users'][0]['nb_sports'] == 0
    assert data['data']['users'][0]['total_distance'] == 0
    assert data['data']['users'][0]['total_duration'] == '0:00:00'
    assert data['data']['users'][1]['timezone'] is None
    assert data['data']['users'][1]['nb_activities'] == 0
    assert data['data']['users'][1]['nb_sports'] == 0
    assert data['data']['users'][1]['total_distance'] == 0
    assert data['data']['users'][1]['total_duration'] == '0:00:00'


def test_encode_auth_token(app, user_1):
    """=> Ensure correct auth token generation"""
    auth_token = user_1.encode_auth_token(user_1.id)
    assert isinstance(auth_token, bytes)


def test_decode_auth_token(app, user_1):
    auth_token = user_1.encode_auth_token(user_1.id)
    assert isinstance(auth_token, bytes)
    assert User.decode_auth_token(auth_token) == user_1.id


def test_user_no_picture(app, user_1):
    client = app.test_client()
    response = client.get('/api/users/1/picture')
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'No picture.' in data['message']


def test_user_picture_no_user(app, user_1):
    client = app.test_client()
    response = client.get('/api/users/2/picture')
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist.' in data['message']

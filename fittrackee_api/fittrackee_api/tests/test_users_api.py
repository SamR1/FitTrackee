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


def test_single_user(app, user_1, user_2):
    """=> Get single user details"""
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        f'/api/users/{user_2.username}',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['data']['users']) == 1

    user = data['data']['users'][0]
    assert user['username'] == 'toto'
    assert user['email'] == 'toto@toto.com'
    assert user['created_at']
    assert not user['admin']
    assert user['first_name'] is None
    assert user['last_name'] is None
    assert user['birth_date'] is None
    assert user['bio'] is None
    assert user['location'] is None
    assert user['timezone'] is None
    assert user['weekm'] is False
    assert user['language'] is None
    assert user['nb_activities'] == 0
    assert user['nb_sports'] == 0
    assert user['sports_list'] == []
    assert user['total_distance'] == 0
    assert user['total_duration'] == '0:00:00'


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
        f'/api/users/{user_1.username}',
        content_type='application/json',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['data']['users']) == 1

    user = data['data']['users'][0]
    assert user['username'] == 'test'
    assert user['email'] == 'test@test.com'
    assert user['created_at']
    assert not user['admin']
    assert user['first_name'] is None
    assert user['last_name'] is None
    assert user['birth_date'] is None
    assert user['bio'] is None
    assert user['location'] is None
    assert user['timezone'] is None
    assert user['weekm'] is False
    assert user['language'] is None
    assert user['nb_activities'] == 2
    assert user['nb_sports'] == 2
    assert user['sports_list'] == [1, 2]
    assert user['total_distance'] == 22
    assert user['total_duration'] == '1:57:04'


def test_single_user_no_existing(app, user_1):
    """=> Ensure error is thrown if the id does not exist."""
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/users/not_existing',
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


def test_users_list(app, user_1, user_2, user_3):
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

    assert len(data['data']['users']) == 3
    assert 'created_at' in data['data']['users'][0]
    assert 'created_at' in data['data']['users'][1]
    assert 'created_at' in data['data']['users'][2]
    assert 'test' in data['data']['users'][0]['username']
    assert 'toto' in data['data']['users'][1]['username']
    assert 'sam' in data['data']['users'][2]['username']
    assert 'test@test.com' in data['data']['users'][0]['email']
    assert 'toto@toto.com' in data['data']['users'][1]['email']
    assert 'sam@test.com' in data['data']['users'][2]['email']
    assert data['data']['users'][0]['timezone'] is None
    assert data['data']['users'][0]['weekm'] is False
    assert data['data']['users'][0]['language'] is None
    assert data['data']['users'][0]['nb_activities'] == 0
    assert data['data']['users'][0]['nb_sports'] == 0
    assert data['data']['users'][0]['sports_list'] == []
    assert data['data']['users'][0]['total_distance'] == 0
    assert data['data']['users'][0]['total_duration'] == '0:00:00'
    assert data['data']['users'][1]['timezone'] is None
    assert data['data']['users'][1]['weekm'] is False
    assert data['data']['users'][1]['language'] is None
    assert data['data']['users'][1]['nb_activities'] == 0
    assert data['data']['users'][1]['nb_sports'] == 0
    assert data['data']['users'][1]['sports_list'] == []
    assert data['data']['users'][1]['total_distance'] == 0
    assert data['data']['users'][1]['total_duration'] == '0:00:00'
    assert data['data']['users'][2]['timezone'] is None
    assert data['data']['users'][2]['weekm'] is True
    assert data['data']['users'][2]['language'] is None
    assert data['data']['users'][2]['nb_activities'] == 0
    assert data['data']['users'][2]['nb_sports'] == 0
    assert data['data']['users'][2]['sports_list'] == []
    assert data['data']['users'][2]['total_distance'] == 0
    assert data['data']['users'][2]['total_duration'] == '0:00:00'


def test_users_list_with_activities(
    app,
    user_1,
    user_2,
    user_3,
    sport_1_cycling,
    activity_cycling_user_1,
    sport_2_running,
    activity_running_user_1,
    activity_cycling_user_2,
):

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

    assert len(data['data']['users']) == 3
    assert 'created_at' in data['data']['users'][0]
    assert 'created_at' in data['data']['users'][1]
    assert 'created_at' in data['data']['users'][2]
    assert 'test' in data['data']['users'][0]['username']
    assert 'toto' in data['data']['users'][1]['username']
    assert 'sam' in data['data']['users'][2]['username']
    assert 'test@test.com' in data['data']['users'][0]['email']
    assert 'toto@toto.com' in data['data']['users'][1]['email']
    assert 'sam@test.com' in data['data']['users'][2]['email']
    assert data['data']['users'][0]['timezone'] is None
    assert data['data']['users'][0]['weekm'] is False
    assert data['data']['users'][0]['nb_activities'] == 2
    assert data['data']['users'][0]['nb_sports'] == 2
    assert data['data']['users'][0]['sports_list'] == [1, 2]
    assert data['data']['users'][0]['total_distance'] == 22.0
    assert data['data']['users'][0]['total_duration'] == '1:57:04'
    assert data['data']['users'][1]['timezone'] is None
    assert data['data']['users'][1]['weekm'] is False
    assert data['data']['users'][1]['nb_activities'] == 1
    assert data['data']['users'][1]['nb_sports'] == 1
    assert data['data']['users'][1]['sports_list'] == [1]
    assert data['data']['users'][1]['total_distance'] == 15
    assert data['data']['users'][1]['total_duration'] == '1:00:00'
    assert data['data']['users'][2]['timezone'] is None
    assert data['data']['users'][2]['weekm'] is True
    assert data['data']['users'][2]['nb_activities'] == 0
    assert data['data']['users'][2]['nb_sports'] == 0
    assert data['data']['users'][2]['sports_list'] == []
    assert data['data']['users'][2]['total_distance'] == 0
    assert data['data']['users'][2]['total_duration'] == '0:00:00'


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
    response = client.get(f'/api/users/{user_1.username}/picture')
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'No picture.' in data['message']


def test_user_picture_no_user(app, user_1):
    client = app.test_client()
    response = client.get('/api/users/not_existing/picture')
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist.' in data['message']

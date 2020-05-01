import json
from io import BytesIO

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


def test_it_adds_admin_rights_to_a_user(app, user_1_admin, user_2):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/users/toto',
        content_type='application/json',
        data=json.dumps(dict(admin=True)),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert len(data['data']['users']) == 1

    user = data['data']['users'][0]
    assert user['email'] == 'toto@toto.com'
    assert user['admin'] is True


def test_it_removes_admin_rights_to_a_user(app, user_1_admin, user_2):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/users/toto',
        content_type='application/json',
        data=json.dumps(dict(admin=False)),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']
    assert len(data['data']['users']) == 1

    user = data['data']['users'][0]
    assert user['email'] == 'toto@toto.com'
    assert user['admin'] is False


def test_it_returns_error_if_payload_for_admin_rights_is_empty(
    app, user_1_admin, user_2
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/users/toto',
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


def test_it_returns_error_if_payload_for_admin_rights_is_invalid(
    app, user_1_admin, user_2
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/users/toto',
        content_type='application/json',
        data=json.dumps(dict(admin="")),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert 'error' in data['status']
    assert (
        'Error. Please try again or contact the administrator.'
        in data['message']
    )


def test_it_returns_error_if_user_can_not_change_admin_rights(
    app, user_1, user_2
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.patch(
        '/api/users/toto',
        content_type='application/json',
        data=json.dumps(dict(admin=True)),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())

    assert response.status_code == 403
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_user_can_delete_its_own_account(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/users/test',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    assert response.status_code == 204


def test_user_with_activity_can_delete_its_own_account(
    app, user_1, sport_1_cycling, gpx_file
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    client.post(
        '/api/activities',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}',
        ),
        headers=dict(
            content_type='multipart/form-data',
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token'],
        ),
    )
    response = client.delete(
        '/api/users/test',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    assert response.status_code == 204


def test_user_with_picture_can_delete_its_own_account(
    app, user_1, sport_1_cycling, gpx_file
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    client.post(
        '/api/auth/picture',
        data=dict(file=(BytesIO(b'avatar'), 'avatar.png')),
        headers=dict(
            content_type='multipart/form-data',
            authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token'],
        ),
    )
    response = client.delete(
        '/api/users/test',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    assert response.status_code == 204


def test_user_can_not_delete_another_user_account(app, user_1, user_2):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/users/toto',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    data = json.loads(response.data.decode())
    assert response.status_code == 403
    assert 'error' in data['status']
    assert 'You do not have permissions.' in data['message']


def test_it_returns_error_when_deleting_non_existing_user(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/users/not_existing',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    data = json.loads(response.data.decode())
    assert response.status_code == 404
    assert 'not found' in data['status']
    assert 'User does not exist.' in data['message']


def test_admin_can_delete_another_user_account(app, user_1_admin, user_2):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/users/toto',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    assert response.status_code == 204


def test_admin_can_delete_its_own_account(app, user_1_admin, user_2_admin):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/users/admin',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    assert response.status_code == 204


def test_admin_can_not_delete_its_own_account_if_no_other_admin(
    app, user_1_admin, user_2
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    response = client.delete(
        '/api/users/admin',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    data = json.loads(response.data.decode())
    assert response.status_code == 403
    assert 'error' in data['status']
    assert (
        'You can not delete your account, no other user has admin rights.'
        in data['message']
    )

import json

from mpwo_api.tests.utils import add_user
from mpwo_api.users.models import User


def test_ping(app):
    """ => Ensure the /ping route behaves correctly."""
    client = app.test_client()
    response = client.get('/api/ping')
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert 'pong' in data['message']
    assert 'success' in data['status']


def test_single_user(app):
    """=> Get single user details"""
    user = add_user('test', 'test@test.com', 'test')
    client = app.test_client()

    response = client.get(f'/api/users/{user.id}')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert 'success' in data['status']

    assert 'created_at' in data['data']
    assert 'test' in data['data']['username']
    assert 'test@test.com' in data['data']['email']


def test_single_user_no_id(app):
    """=> Ensure error is thrown if an id is not provided."""
    client = app.test_client()
    response = client.get(f'/api/users/blah')
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist' in data['message']


def test_single_user_wrong_id(app):
    """=> Ensure error is thrown if the id does not exist."""
    client = app.test_client()
    response = client.get(f'/api/users/99999999999')
    data = json.loads(response.data.decode())

    assert response.status_code == 404
    assert 'fail' in data['status']
    assert 'User does not exist' in data['message']


def test_users_list(app):
    """=> Ensure get single user behaves correctly."""
    add_user('test', 'test@test.com', 'test')
    add_user('toto', 'toto@toto.com', 'toto')

    client = app.test_client()
    response = client.get('/api/users')
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


def test_encode_auth_token(app):
    """=> Ensure correct auth token generation"""
    user = add_user('test', 'test@test.com', 'test')
    auth_token = user.encode_auth_token(user.id)
    assert isinstance(auth_token, bytes)


def test_decode_auth_token(app):
    user = add_user('test', 'test@test.com', 'test')
    auth_token = user.encode_auth_token(user.id)
    assert isinstance(auth_token, bytes)
    assert User.decode_auth_token(auth_token) == user.id

import json
import time
from io import BytesIO


def test_user_registration(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='justatest',
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'Successfully registered.'
    assert data['auth_token']
    assert response.content_type == 'application/json'
    assert response.status_code == 201


def test_user_registration_user_already_exists(app, user_1):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='test',
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Sorry. That user already exists.'
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_user_registration_invalid_short_username(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='t',
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == "Username: 3 to 12 characters required.\n"
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_user_registration_invalid_long_username(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='testestestestestest',
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == "Username: 3 to 12 characters required.\n"
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_user_registration_invalid_email(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='test',
                email='test@test',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == "Valid email must be provided.\n"
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_user_registration_invalid_short_password(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='test',
                email='test@test.com',
                password='1234567',
                password_conf='1234567',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == "Password: 8 characters required.\n"
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_user_registration_mismatched_password(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='test',
                email='test@test.com',
                password='12345678',
                password_conf='87654321',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert (
        data['message'] == "Password and password confirmation don\'t match.\n"
    )
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_user_registration_invalid_json(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(dict()),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert response.status_code, 400
    assert 'Invalid payload.', data['message']
    assert 'error', data['status']


def test_user_registration_invalid_json_keys_no_username(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert 'Invalid payload.' in data['message']
    assert 'error' in data['status']


def test_user_registration_invalid_json_keys_no_email(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='test', password='12345678', password_conf='12345678'
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert 'Invalid payload.' in data['message']
    assert 'error' in data['status']


def test_user_registration_invalid_json_keys_no_password(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='test',
                email='test@test.com',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert 'Invalid payload.', data['message']
    assert 'error', data['status']


def test_user_registration_invalid_json_keys_no_password_conf(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(username='test', email='test@test.com', password='12345678')
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert 'Invalid payload.' in data['message']
    assert 'error' in data['status']


def test_user_registration_invalid_data(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username=1,
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 500
    assert (
        'Error. Please try again or contact the administrator.'
        in data['message']
    )
    assert 'error' in data['status']


def test_user_registration_max_users_exceeded(
    app, user_1_admin, user_2, user_3
):
    client = app.test_client()

    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='admin@example.com', password='12345678')),
        content_type='application/json',
    )
    client.patch(
        '/api/config',
        content_type='application/json',
        data=json.dumps(dict(max_users=3, registration=True)),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )

    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='user4',
                email='user4@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )

    assert response.content_type == 'application/json'
    assert response.status_code == 403
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Error. Registration is disabled.'


def test_login_registered_user(app, user_1):
    client = app.test_client()
    response = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'Successfully logged in.'
    assert data['auth_token']
    assert response.content_type == 'application/json'
    assert response.status_code == 200


def test_login_no_registered_user(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid credentials.'
    assert response.content_type == 'application/json'
    assert response.status_code == 404


def test_login_invalid_payload(app):
    client = app.test_client()
    response = client.post(
        '/api/auth/login',
        data=json.dumps(dict()),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid payload.'
    assert response.content_type == 'application/json'
    assert response.status_code == 400


def test_login_registered_user_invalid_password(app, user_1):
    client = app.test_client()
    response = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='123456789')),
        content_type='application/json',
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid credentials.'
    assert response.content_type == 'application/json'
    assert response.status_code == 404


def test_logout(app, user_1):
    client = app.test_client()
    # user login
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    # valid token logout
    response = client.get(
        '/api/auth/logout',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'Successfully logged out.'
    assert response.status_code == 200


def test_logout_expired_token(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    # invalid token logout
    time.sleep(4)
    response = client.get(
        '/api/auth/logout',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Signature expired. Please log in again.'
    assert response.status_code == 401


def test_logout_invalid(app):
    client = app.test_client()
    response = client.get(
        '/api/auth/logout', headers=dict(Authorization='Bearer invalid')
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid token. Please log in again.'
    assert response.status_code == 401


def test_logout_invalid_headers(app):
    client = app.test_client()
    response = client.get('/api/auth/logout', headers=dict())
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Provide a valid auth token.'
    assert response.status_code == 401


def test_user_profile_minimal(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/auth/profile',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['data'] is not None
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert data['data']['created_at']
    assert not data['data']['admin']
    assert data['data']['timezone'] is None
    assert data['data']['weekm'] is False
    assert data['data']['language'] is None
    assert data['data']['nb_activities'] == 0
    assert data['data']['nb_sports'] == 0
    assert data['data']['sports_list'] == []
    assert data['data']['total_distance'] == 0
    assert data['data']['total_duration'] == '0:00:00'
    assert response.status_code == 200


def test_user_profile_full(app, user_1_full):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/auth/profile',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['data'] is not None
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert data['data']['created_at']
    assert not data['data']['admin']
    assert data['data']['first_name'] == 'John'
    assert data['data']['last_name'] == 'Doe'
    assert data['data']['birth_date']
    assert data['data']['bio'] == 'just a random guy'
    assert data['data']['location'] == 'somewhere'
    assert data['data']['timezone'] == 'America/New_York'
    assert data['data']['weekm'] is False
    assert data['data']['language'] == 'en'
    assert data['data']['nb_activities'] == 0
    assert data['data']['nb_sports'] == 0
    assert data['data']['sports_list'] == []
    assert data['data']['total_distance'] == 0
    assert data['data']['total_duration'] == '0:00:00'
    assert response.status_code == 200


def test_user_profile_with_activities(
    app,
    user_1,
    sport_1_cycling,
    sport_2_running,
    activity_cycling_user_1,
    activity_running_user_1,
):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.get(
        '/api/auth/profile',
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['data'] is not None
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert data['data']['created_at']
    assert not data['data']['admin']
    assert data['data']['timezone'] is None
    assert data['data']['nb_activities'] == 2
    assert data['data']['nb_sports'] == 2
    assert data['data']['sports_list'] == [1, 2]
    assert data['data']['total_distance'] == 22
    assert data['data']['total_duration'] == '1:57:04'
    assert response.status_code == 200


def test_invalid_profile(app):
    client = app.test_client()
    response = client.get(
        '/api/auth/profile', headers=dict(Authorization='Bearer invalid')
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid token. Please log in again.'
    assert response.status_code == 401


def test_user_profile_valid_update(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/profile/edit',
        content_type='application/json',
        data=json.dumps(
            dict(
                first_name='John',
                last_name='Doe',
                location='Somewhere',
                bio='Nothing to tell',
                birth_date='1980-01-01',
                password='87654321',
                password_conf='87654321',
                timezone='America/New_York',
                weekm=True,
                language='fr',
            )
        ),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'User profile updated.'
    assert response.status_code == 200
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert not data['data']['admin']
    assert data['data']['created_at']
    assert data['data']['first_name'] == 'John'
    assert data['data']['last_name'] == 'Doe'
    assert data['data']['birth_date']
    assert data['data']['bio'] == 'Nothing to tell'
    assert data['data']['location'] == 'Somewhere'
    assert data['data']['timezone'] == 'America/New_York'
    assert data['data']['weekm'] is True
    assert data['data']['language'] == 'fr'
    assert data['data']['nb_activities'] == 0
    assert data['data']['nb_sports'] == 0
    assert data['data']['sports_list'] == []
    assert data['data']['total_distance'] == 0
    assert data['data']['total_duration'] == '0:00:00'


def test_user_profile_valid_update_without_password(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/profile/edit',
        content_type='application/json',
        data=json.dumps(
            dict(
                first_name='John',
                last_name='Doe',
                location='Somewhere',
                bio='Nothing to tell',
                birth_date='1980-01-01',
                timezone='America/New_York',
                weekm=True,
                language='fr',
            )
        ),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'User profile updated.'
    assert response.status_code == 200
    assert data['data']['username'] == 'test'
    assert data['data']['email'] == 'test@test.com'
    assert not data['data']['admin']
    assert data['data']['created_at']
    assert data['data']['first_name'] == 'John'
    assert data['data']['last_name'] == 'Doe'
    assert data['data']['birth_date']
    assert data['data']['bio'] == 'Nothing to tell'
    assert data['data']['location'] == 'Somewhere'
    assert data['data']['timezone'] == 'America/New_York'
    assert data['data']['weekm'] is True
    assert data['data']['language'] == 'fr'
    assert data['data']['nb_activities'] == 0
    assert data['data']['nb_sports'] == 0
    assert data['data']['sports_list'] == []
    assert data['data']['total_distance'] == 0
    assert data['data']['total_duration'] == '0:00:00'


def test_user_profile_invalid_update_with_missing_fields(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/profile/edit',
        content_type='application/json',
        data=json.dumps(dict(first_name='John')),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Invalid payload.'
    assert response.status_code == 400


def test_user_profile_update_invalid_json(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/profile/edit',
        content_type='application/json',
        data=json.dumps(dict()),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert 'Invalid payload.' in data['message']
    assert 'error' in data['status']


def test_user_profile_invalid_password(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/profile/edit',
        content_type='application/json',
        data=json.dumps(
            dict(
                first_name='John',
                last_name='Doe',
                location='Somewhere',
                bio='just a random guy',
                birth_date='1980-01-01',
                password='87654321',
                password_conf='876543210',
                timezone='America/New_York',
                weekm=True,
                language='en',
            )
        ),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert (
        data['message'] == 'Password and password confirmation don\'t match.\n'
    )
    assert response.status_code == 400


def test_user_profile_missing_password_conf(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/profile/edit',
        content_type='application/json',
        data=json.dumps(
            dict(
                first_name='John',
                last_name='Doe',
                location='Somewhere',
                bio='just a random guy',
                birth_date='1980-01-01',
                password='87654321',
                timezone='America/New_York',
                weekm=True,
                language='en',
            )
        ),
        headers=dict(
            Authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token']
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert (
        data['message'] == 'Password and password confirmation don\'t match.\n'
    )
    assert response.status_code == 400


def test_update_user_picture(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/picture',
        data=dict(file=(BytesIO(b'avatar'), 'avatar.png')),
        headers=dict(
            content_type='multipart/form-data',
            authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token'],
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'User picture updated.'
    assert response.status_code == 200
    assert 'avatar.png' in user_1.picture

    response = client.post(
        '/api/auth/picture',
        data=dict(file=(BytesIO(b'avatar2'), 'avatar2.png')),
        headers=dict(
            content_type='multipart/form-data',
            authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token'],
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'success'
    assert data['message'] == 'User picture updated.'
    assert response.status_code == 200
    assert 'avatar.png' not in user_1.picture
    assert 'avatar2.png' in user_1.picture


def test_update_user_no_picture(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/picture',
        headers=dict(
            content_type='multipart/form-data',
            authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token'],
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'fail'
    assert data['message'] == 'No file part.'
    assert response.status_code == 400


def test_update_user_invalid_picture(app, user_1):
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/picture',
        data=dict(file=(BytesIO(b'avatar'), 'avatar.bmp')),
        headers=dict(
            content_type='multipart/form-data',
            authorization='Bearer '
            + json.loads(resp_login.data.decode())['auth_token'],
        ),
    )
    data = json.loads(response.data.decode())
    assert data['status'] == 'fail'
    assert data['message'] == 'File extension not allowed.'
    assert response.status_code == 400


def test_it_disables_registration_on_user_registration(
    app_no_config, app_config, user_1_admin, user_2
):
    app_config.max_users = 3
    client = app_no_config.test_client()
    client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='sam',
                email='sam@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='new',
                email='new@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    assert response.status_code == 403
    data = json.loads(response.data.decode())
    assert data['status'] == 'error'
    assert data['message'] == 'Error. Registration is disabled.'


def test_it_does_not_disable_registration_on_user_registration(
    app_no_config, app_config, user_1_admin, user_2,
):
    app_config.max_users = 4
    client = app_no_config.test_client()
    client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='sam',
                email='sam@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    response = client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username='new',
                email='new@test.com',
                password='12345678',
                password_conf='12345678',
            )
        ),
        content_type='application/json',
    )
    assert response.status_code == 201

import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import Mock, patch

from flask import Flask
from freezegun import freeze_time

from fittrackee.users.models import User
from fittrackee.users.utils_token import get_user_token
from fittrackee.workouts.models import Sport, Workout


class TestUserRegistration:
    def test_user_can_register(self, app: Flask) -> None:
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

    def test_it_returns_error_if_user_already_exists(
        self, app: Flask, user_1: User
    ) -> None:
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

    def test_it_returns_error_if_username_is_too_short(
        self, app: Flask
    ) -> None:
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

    def test_it_returns_error_if_username_is_too_long(
        self, app: Flask
    ) -> None:
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

    def test_it_returns_error_if_email_is_invalid(self, app: Flask) -> None:
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

    def test_it_returns_error_if_password_is_too_short(
        self, app: Flask
    ) -> None:
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

    def test_it_returns_error_if_passwords_mismatch(self, app: Flask) -> None:
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
            data['message']
            == "Password and password confirmation don\'t match.\n"
        )
        assert response.content_type == 'application/json'
        assert response.status_code == 400

    def test_it_returns_error_if_payload_is_invalid(self, app: Flask) -> None:
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

    def test_it_returns_error_if_username_is_missing(self, app: Flask) -> None:
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

    def test_it_returns_error_if_email_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username='test',
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

    def test_it_returns_error_if_password_is_missing(self, app: Flask) -> None:
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

    def test_it_returns_error_if_password_confirmation_is_missing(
        self, app: Flask
    ) -> None:
        client = app.test_client()
        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username='test', email='test@test.com', password='12345678'
                )
            ),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'Invalid payload.' in data['message']
        assert 'error' in data['status']

    def test_it_returns_error_if_username_is_invalid(self, app: Flask) -> None:
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


class TestUserLogin:
    def test_user_can_register(self, app: Flask, user_1: User) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        assert response.content_type == 'application/json'
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Successfully logged in.'
        assert data['auth_token']

    def test_it_returns_error_if_user_does_not_exists(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        assert response.content_type == 'application/json'
        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid credentials.'

    def test_it_returns_error_on_invalid_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        assert response.content_type == 'application/json'
        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid payload.'

    def test_it_returns_error_if_password_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='123456789')),
            content_type='application/json',
        )

        assert response.content_type == 'application/json'
        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid credentials.'


class TestUserLogout:
    def test_user_can_logout(self, app: Flask, user_1: User) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

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

    def test_it_returns_error_with_expired_token(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()
        now = datetime.utcnow()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        with freeze_time(now + timedelta(seconds=4)):
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

    def test_it_returns_error_with_invalid_token(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            '/api/auth/logout', headers=dict(Authorization='Bearer invalid')
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid token. Please log in again.'
        assert response.status_code == 401

    def test_it_returns_error_with_invalid_headers(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get('/api/auth/logout', headers=dict())
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Provide a valid auth token.'
        assert response.status_code == 401


class TestUserProfile:
    def test_it_returns_user_minimal_profile(
        self, app: Flask, user_1: User
    ) -> None:
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
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'
        assert response.status_code == 200

    def test_it_returns_user_full_profile(
        self, app: Flask, user_1_full: User
    ) -> None:
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
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'
        assert response.status_code == 200

    def test_it_returns_user_profile_with_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
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
        assert data['data']['nb_sports'] == 2
        assert data['data']['nb_workouts'] == 2
        assert data['data']['sports_list'] == [1, 2]
        assert data['data']['total_distance'] == 22
        assert data['data']['total_duration'] == '2:40:00'
        assert response.status_code == 200

    def test_it_returns_error_if_headers_are_invalid(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            '/api/auth/profile', headers=dict(Authorization='Bearer invalid')
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid token. Please log in again.'
        assert response.status_code == 401


class TestUserProfileUpdate:
    def test_it_updates_user_profile(self, app: Flask, user_1: User) -> None:
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
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'

    def test_it_updates_user_profile_without_password(
        self, app: Flask, user_1: User
    ) -> None:
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
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'

    def test_it_returns_error_if_fields_are_missing(
        self, app: Flask, user_1: User
    ) -> None:
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

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
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

    def test_it_returns_error_if_passwords_mismatch(
        self, app: Flask, user_1: User
    ) -> None:
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
            data['message']
            == 'Password and password confirmation don\'t match.\n'
        )
        assert response.status_code == 400

    def test_it_returns_error_if_password_confirmation_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
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
            data['message']
            == 'Password and password confirmation don\'t match.\n'
        )
        assert response.status_code == 400


class TestUserPicture:
    def test_it_updates_user_picture(self, app: Flask, user_1: User) -> None:
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

    def test_it_returns_error_if_file_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
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

    def test_it_returns_error_if_file_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
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


class TestRegistrationConfiguration:
    def test_it_returns_error_if_it_exceeds_max_users(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client = app.test_client()

        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email='admin@example.com', password='12345678')
            ),
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

    def test_it_disables_registration_on_user_registration(
        self,
        app_no_config: Flask,
        app_config: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
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
        self,
        app_no_config: Flask,
        app_config: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
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


class TestPasswordResetRequest:
    @patch('smtplib.SMTP_SSL')
    @patch('smtplib.SMTP')
    def test_it_requests_password_reset_when_user_exists(
        self, mock_smtp: Mock, mock_smtp_ssl: Mock, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()
        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(email='test@test.com')),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Password reset request processed.'

    def test_it_does_not_return_error_when_user_does_not_exist(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(email='test@test.com')),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Password reset request processed.'

    def test_it_returns_error_on_invalid_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(usernmae='test')),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['message'] == 'Invalid payload.'
        assert data['status'] == 'error'

    def test_it_returns_error_on_empty_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['message'] == 'Invalid payload.'
        assert data['status'] == 'error'


class TestPasswordUpdate:
    def test_it_returns_error_if_payload_is_empty(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token='xxx',
                    password='1234567',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid payload.'

    def test_it_returns_error_if_token_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid payload.'

    def test_it_returns_error_if_password_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token='xxx',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid payload.'

    def test_it_returns_error_if_password_confirmation_is_missing(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token='xxx',
                    password='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid payload.'

    def test_it_returns_error_if_token_is_invalid(self, app: Flask) -> None:
        token = get_user_token(1)
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token=token,
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid token. Please request a new token.'

    def test_it_returns_error_if_token_is_expired(
        self, app: Flask, user_1: User
    ) -> None:
        now = datetime.utcnow()
        token = get_user_token(user_1.id, password_reset=True)
        client = app.test_client()

        with freeze_time(now + timedelta(seconds=4)):
            response = client.post(
                '/api/auth/password/update',
                data=json.dumps(
                    dict(
                        token=token,
                        password='12345678',
                        password_conf='12345678',
                    )
                ),
                content_type='application/json',
            )

            assert response.status_code == 401
            data = json.loads(response.data.decode())
            assert data['status'] == 'error'
            assert (
                data['message'] == 'Invalid token. Please request a new token.'
            )

    def test_it_returns_error_if_password_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        token = get_user_token(user_1.id, password_reset=True)
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token=token,
                    password='1234567',
                    password_conf='1234567',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'Password: 8 characters required.\n'

    def test_it_update_password(self, app: Flask, user_1: User) -> None:
        token = get_user_token(user_1.id, password_reset=True)
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token=token,
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'Password updated.'

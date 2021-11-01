import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import Mock, patch

from flask import Flask
from freezegun import freeze_time

from fittrackee.users.models import User
from fittrackee.users.utils_token import get_user_token
from fittrackee.workouts.models import Sport, Workout

from ..api_test_case import ApiTestCaseMixin


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
        assert data['message'] == 'successfully registered'
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
        assert data['message'] == 'sorry, that user already exists'
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
        assert data['message'] == "username: 3 to 12 characters required\n"
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
        assert data['message'] == "username: 3 to 12 characters required\n"
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
        assert data['message'] == "email: valid email must be provided\n"
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
        assert data['message'] == "password: 8 characters required\n"
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
            == "password: password and password confirmation do not match\n"
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
        assert 'invalid payload', data['message']
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
        assert 'invalid payload' in data['message']
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
        assert 'invalid payload' in data['message']
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
        assert 'invalid payload', data['message']
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
        assert 'invalid payload' in data['message']
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
            'error, please try again or contact the administrator'
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
        assert data['message'] == 'successfully logged in'
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
        assert data['message'] == 'invalid credentials'

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
        assert data['message'] == 'invalid payload'

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
        assert data['message'] == 'invalid credentials'


class TestUserLogout(ApiTestCaseMixin):
    def test_user_can_logout(self, app: Flask, user_1: User) -> None:

        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/auth/logout',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'successfully logged out'
        assert response.status_code == 200

    def test_it_returns_error_with_expired_token(
        self, app: Flask, user_1: User
    ) -> None:
        now = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(app)

        with freeze_time(now + timedelta(seconds=4)):
            response = client.get(
                '/api/auth/logout',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )
            data = json.loads(response.data.decode())
            assert data['status'] == 'error'
            assert data['message'] == 'signature expired, please log in again'
            assert response.status_code == 401

    def test_it_returns_error_with_invalid_token(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            '/api/auth/logout', headers=dict(Authorization='Bearer invalid')
        )
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'invalid token, please log in again'
        assert response.status_code == 401

    def test_it_returns_error_with_invalid_headers(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get('/api/auth/logout', headers=dict())
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'provide a valid auth token'
        assert response.status_code == 401


class TestUserProfile(ApiTestCaseMixin):
    def test_it_returns_user_minimal_profile(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/auth/profile',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['data']['records'] == []
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'
        assert response.status_code == 200

    def test_it_returns_user_full_profile(
        self, app: Flask, user_1_full: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/auth/profile',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['data']['records'] == []
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
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/auth/profile',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert len(data['data']['records']) == 6
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
        assert data['message'] == 'invalid token, please log in again'
        assert response.status_code == 401


class TestUserProfileUpdate(ApiTestCaseMixin):
    def test_it_updates_user_profile(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

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
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user profile updated'
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
        assert data['data']['timezone'] is None
        assert data['data']['weekm'] is False
        assert data['data']['language'] is None
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['records'] == []
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'

    def test_it_updates_user_profile_without_password(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

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
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user profile updated'
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
        assert data['data']['timezone'] is None
        assert data['data']['weekm'] is False
        assert data['data']['language'] is None
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['records'] == []
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'

    def test_it_returns_error_if_fields_are_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            data=json.dumps(dict(first_name='John')),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'invalid payload'
        assert response.status_code == 400

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'invalid payload' in data['message']
        assert 'error' in data['status']

    def test_it_returns_error_if_passwords_mismatch(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

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
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert (
            data['message']
            == 'password: password and password confirmation do not match\n'
        )
        assert response.status_code == 400

    def test_it_returns_error_if_password_confirmation_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

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
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert (
            data['message']
            == 'password: password and password confirmation do not match\n'
        )
        assert response.status_code == 400


class TestUserPreferencesUpdate(ApiTestCaseMixin):
    def test_it_updates_user_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(
                dict(
                    timezone='America/New_York',
                    weekm=True,
                    language='fr',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user preferences updated'
        assert response.status_code == 200
        assert data['data']['username'] == 'test'
        assert data['data']['email'] == 'test@test.com'
        assert not data['data']['admin']
        assert data['data']['created_at']
        assert data['data']['first_name'] is None
        assert data['data']['last_name'] is None
        assert data['data']['birth_date'] is None
        assert data['data']['bio'] is None
        assert data['data']['location'] is None
        assert data['data']['timezone'] == 'America/New_York'
        assert data['data']['weekm'] is True
        assert data['data']['language'] == 'fr'
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['records'] == []
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'

    def test_it_returns_error_if_fields_are_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(dict(weekm=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'invalid payload'
        assert response.status_code == 400

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'invalid payload' in data['message']
        assert 'error' in data['status']


class TestUserPicture(ApiTestCaseMixin):
    def test_it_updates_user_picture(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/picture',
            data=dict(file=(BytesIO(b'avatar'), 'avatar.png')),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user picture updated'
        assert response.status_code == 200
        assert 'avatar.png' in user_1.picture

        response = client.post(
            '/api/auth/picture',
            data=dict(file=(BytesIO(b'avatar2'), 'avatar2.png')),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user picture updated'
        assert response.status_code == 200
        assert 'avatar.png' not in user_1.picture
        assert 'avatar2.png' in user_1.picture

    def test_it_returns_error_if_file_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/picture',
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'fail'
        assert data['message'] == 'no file part'
        assert response.status_code == 400

    def test_it_returns_error_if_file_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            '/api/auth/picture',
            data=dict(file=(BytesIO(b'avatar'), 'avatar.bmp')),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'fail'
        assert data['message'] == 'file extension not allowed'
        assert response.status_code == 400

    def test_it_returns_error_if_image_size_exceeds_file_limit(
        self,
        app_with_max_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size
        )

        response = client.post(
            '/api/auth/picture',
            data=dict(
                file=(BytesIO(b'test_file_for_avatar' * 50), 'avatar.jpg')
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        print('data', data)
        assert response.status_code == 413
        assert 'fail' in data['status']
        assert (
            'Error during picture upload, file size (1.2KB) exceeds 1.0KB.'
            in data['message']
        )
        assert 'data' not in data

    def test_it_returns_error_if_image_size_exceeds_archive_limit(
        self,
        app_with_max_zip_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_zip_file_size
        )

        response = client.post(
            '/api/auth/picture',
            data=dict(
                file=(BytesIO(b'test_file_for_avatar' * 50), 'avatar.jpg')
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        print('data', data)
        assert response.status_code == 413
        assert 'fail' in data['status']
        assert (
            'Error during picture upload, file size (1.2KB) exceeds 1.0KB.'
            in data['message']
        )
        assert 'data' not in data


class TestRegistrationConfiguration:
    def test_it_returns_error_if_it_exceeds_max_users(
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client = app_with_3_users_max.test_client()

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
        assert data['message'] == 'error, registration is disabled'

    def test_it_disables_registration_on_user_registration(
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        client = app_with_3_users_max.test_client()
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
        assert data['message'] == 'error, registration is disabled'

    def test_it_does_not_disable_registration_on_user_registration(
        self,
        app_with_3_users_max: Flask,
        user_1: User,
    ) -> None:
        client = app_with_3_users_max.test_client()
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
        assert data['message'] == 'password reset request processed'

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
        assert data['message'] == 'password reset request processed'

    def test_it_returns_error_on_invalid_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(usernmae='test')),
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['message'] == 'invalid payload'
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
        assert data['message'] == 'invalid payload'
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
        assert data['message'] == 'invalid payload'

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
        assert data['message'] == 'invalid payload'

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
        assert data['message'] == 'invalid payload'

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
        assert data['message'] == 'invalid payload'

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
        assert data['message'] == 'invalid token, please request a new token'

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
                data['message'] == 'invalid token, please request a new token'
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
        assert data['message'] == 'password: 8 characters required\n'

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
        assert data['message'] == 'password updated'

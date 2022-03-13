import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee.users.models import User, UserSportPreference
from fittrackee.users.utils.token import get_user_token
from fittrackee.workouts.models import Sport, Workout

from ..api_test_case import ApiTestCaseMixin


class TestUserRegistration(ApiTestCaseMixin):
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

    @pytest.mark.parametrize(
        'input_username',
        ['test', 'TEST'],
    )
    def test_it_returns_error_if_user_already_exists_with_same_username(
        self, app: Flask, user_1: User, input_username: str
    ) -> None:
        client = app.test_client()
        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=input_username,
                    email='another_email@test.com',
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'sorry, that user already exists')

    @pytest.mark.parametrize(
        'input_email',
        ['test@test.com', 'TEST@TEST.COM'],
    )
    def test_it_returns_error_if_user_already_exists_with_same_email(
        self, app: Flask, user_1: User, input_email: str
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

        self.assert_400(response, 'sorry, that user already exists')

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

        self.assert_400(response, "username: 3 to 12 characters required\n")

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

        self.assert_400(response, "username: 3 to 12 characters required\n")

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

        self.assert_400(response, "email: valid email must be provided\n")

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

        self.assert_400(response, "password: 8 characters required\n")

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

        self.assert_400(
            response,
            "password: password and password confirmation do not match\n",
        )

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

        self.assert_400(response)

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

        self.assert_400(response)

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

        self.assert_400(response)

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

        self.assert_400(response)

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

        self.assert_500(response)


class TestUserLogin(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        'input_email',
        ['test@test.com', 'TEST@TEST.COM'],
    )
    def test_user_can_login(
        self, app: Flask, user_1: User, input_email: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email=input_email, password='12345678')),
            content_type='application/json',
        )

        assert response.content_type == 'application/json'
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'successfully logged in'
        assert data['auth_token']

    @pytest.mark.parametrize(
        'input_email',
        ['test@test.com', 'TEST@TEST.COM'],
    )
    def test_user_can_login_when_user_email_is_uppercase(
        self, app: Flask, user_1_upper: User, input_email: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email=input_email, password='12345678')),
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

        self.assert_401(response, 'invalid credentials')

    def test_it_returns_error_on_invalid_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_password_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='123456789')),
            content_type='application/json',
        )

        self.assert_401(response, 'invalid credentials')


class TestUserLogout(ApiTestCaseMixin):
    def test_user_can_logout(self, app: Flask, user_1: User) -> None:

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with freeze_time(now + timedelta(seconds=4)):

            response = client.get(
                '/api/auth/logout',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

            self.assert_401(response, 'signature expired, please log in again')

    def test_it_returns_error_with_invalid_token(self, app: Flask) -> None:
        client = app.test_client()

        response = client.get(
            '/api/auth/logout', headers=dict(Authorization='Bearer invalid')
        )

        self.assert_401(response, 'invalid token, please log in again')

    def test_it_returns_error_with_invalid_headers(self, app: Flask) -> None:
        client = app.test_client()

        response = client.get('/api/auth/logout', headers=dict())

        self.assert_401(response, 'provide a valid auth token')


class TestUserProfile(ApiTestCaseMixin):
    def test_it_returns_user_minimal_profile(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        assert data['data']['imperial_units'] is False
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_full.email
        )

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
        assert data['data']['imperial_units'] is False
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        assert data['data']['imperial_units'] is False
        assert data['data']['nb_sports'] == 2
        assert data['data']['nb_workouts'] == 2
        assert len(data['data']['records']) == 8
        assert data['data']['sports_list'] == [1, 2]
        assert data['data']['total_distance'] == 22
        assert data['data']['total_duration'] == '2:40:00'
        assert response.status_code == 200

    def test_it_returns_error_if_headers_are_invalid(self, app: Flask) -> None:
        client = app.test_client()

        response = client.get(
            '/api/auth/profile', headers=dict(Authorization='Bearer invalid')
        )

        self.assert_401(response, 'invalid token, please log in again')


class TestUserProfileUpdate(ApiTestCaseMixin):
    def test_it_updates_user_profile(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
        assert data['data']['imperial_units'] is False
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
        assert data['data']['imperial_units'] is False
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            data=json.dumps(dict(first_name='John')),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_passwords_mismatch(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response,
            'password: password and password confirmation do not match\n',
        )

    def test_it_returns_error_if_password_confirmation_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response,
            'password: password and password confirmation do not match\n',
        )


class TestUserPreferencesUpdate(ApiTestCaseMixin):
    def test_it_updates_user_preferences(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(
                dict(
                    timezone='America/New_York',
                    weekm=True,
                    language='fr',
                    imperial_units=True,
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
        assert data['data']['imperial_units']
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(dict(weekm=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)


class TestUserSportPreferencesUpdate(ApiTestCaseMixin):
    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_sport_id_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(dict(is_active=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_sport_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(dict(sport_id=1, is_active=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_entity(response, 'sport')

    def test_it_returns_error_if_payload_contains_only_sport_id(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(dict(sport_id=1)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_color_is_invalid(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_1_cycling.id,
                    color='invalid',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'invalid hexadecimal color')

    @pytest.mark.parametrize(
        'input_color',
        ['#000000', '#FFF'],
    )
    def test_it_updates_sport_color_for_auth_user(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        input_color: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_2_running.id,
                    color=input_color,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user sport preferences updated'
        assert response.status_code == 200
        assert data['data']['user_id'] == user_1.id
        assert data['data']['sport_id'] == sport_2_running.id
        assert data['data']['color'] == input_color
        assert data['data']['is_active'] is True
        assert data['data']['stopped_speed_threshold'] == 0.1

    def test_it_disables_sport_for_auth_user(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_1_cycling.id,
                    is_active=False,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user sport preferences updated'
        assert response.status_code == 200
        assert data['data']['user_id'] == user_1.id
        assert data['data']['sport_id'] == sport_1_cycling.id
        assert data['data']['color'] is None
        assert data['data']['is_active'] is False
        assert data['data']['stopped_speed_threshold'] == 1

    def test_it_updates_stopped_speed_threshold_for_auth_user(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_1_cycling.id,
                    stopped_speed_threshold=0.5,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user sport preferences updated'
        assert response.status_code == 200
        assert data['data']['user_id'] == user_1.id
        assert data['data']['sport_id'] == sport_1_cycling.id
        assert data['data']['color'] is None
        assert data['data']['is_active']
        assert data['data']['stopped_speed_threshold'] == 0.5


class TestUserSportPreferencesReset(ApiTestCaseMixin):
    def test_it_returns_error_if_sport_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            '/api/auth/profile/reset/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_entity(response, 'sport')

    def test_it_resets_sport_preferences(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f'/api/auth/profile/reset/sports/{sport_1_cycling.id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        assert (
            UserSportPreference.query.filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
            ).first()
            is None
        )

    def test_it_does_not_raise_error_if_sport_preferences_do_not_exist(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f'/api/auth/profile/reset/sports/{sport_1_cycling.id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204


class TestUserPicture(ApiTestCaseMixin):
    def test_it_updates_user_picture(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/picture',
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response, 'no file part', 'fail')

    def test_it_returns_error_if_file_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/picture',
            data=dict(file=(BytesIO(b'avatar'), 'avatar.bmp')),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response, 'file extension not allowed', 'fail')

    def test_it_returns_error_if_image_size_exceeds_file_limit(
        self,
        app_with_max_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size, user_1.email
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

        data = self.assert_413(
            response,
            'Error during picture upload, file size (1.2KB) exceeds 1.0KB.',
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
            app_with_max_zip_file_size, user_1.email
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

        data = self.assert_413(
            response,
            'Error during picture upload, file size (1.2KB) exceeds 1.0KB.',
        )
        assert 'data' not in data


class TestRegistrationConfiguration(ApiTestCaseMixin):
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

        self.assert_403(response, 'error, registration is disabled')

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

        self.assert_403(response, 'error, registration is disabled')

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


class TestPasswordResetRequest(ApiTestCaseMixin):
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

        self.assert_400(response)

    def test_it_returns_error_on_empty_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)


class TestPasswordUpdate(ApiTestCaseMixin):
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

        self.assert_400(response)

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

        self.assert_400(response)

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

        self.assert_400(response)

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

        self.assert_400(response)

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

        self.assert_401(response, 'invalid token, please request a new token')

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

            self.assert_401(
                response, 'invalid token, please request a new token'
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

        self.assert_400(response, 'password: 8 characters required\n')

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

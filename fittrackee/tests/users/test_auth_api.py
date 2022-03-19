import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee.users.models import User, UserSportPreference
from fittrackee.users.utils.token import get_user_token
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin

USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0'
)


class TestUserRegistration(ApiTestCaseMixin):
    def test_it_returns_error_if_payload_is_empty(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_username_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'input_username_length',
        [1, 31],
    )
    def test_it_returns_error_if_username_length_is_invalid(
        self, app: Flask, input_username_length: int
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(length=input_username_length),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'username: 3 to 30 characters required\n')

    @pytest.mark.parametrize(
        'input_description,input_username',
        [
            ('account_handle', '@sam@example.com'),
            ('with special characters', 'sam*'),
        ],
    )
    def test_it_returns_error_if_username_is_invalid(
        self, app: Flask, input_description: str, input_username: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=input_username,
                    email=self.random_email(),
                    password=self.random_email(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(
            response,
            'username: only alphanumeric characters and '
            'the underscore character "_" allowed\n',
        )

    @pytest.mark.parametrize(
        'text_transformation',
        ['upper', 'lower'],
    )
    def test_it_returns_error_if_user_already_exists_with_same_username(
        self, app: Flask, user_1: User, text_transformation: str
    ) -> None:
        client = app.test_client()
        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=(
                        user_1.username.upper()
                        if text_transformation == 'upper'
                        else user_1.username.lower()
                    ),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'sorry, that user already exists')

    def test_it_returns_error_if_password_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_password_is_too_short(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(length=7),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'password: 8 characters required\n')

    def test_it_returns_error_if_email_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_email_is_invalid(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_string(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'email: valid email must be provided\n')

    @pytest.mark.parametrize(
        'text_transformation',
        ['upper', 'lower'],
    )
    def test_it_returns_error_if_user_already_exists_with_same_email(
        self, app: Flask, user_1: User, text_transformation: str
    ) -> None:
        client = app.test_client()
        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=(
                        user_1.email.upper()
                        if text_transformation == 'upper'
                        else user_1.email.lower()
                    ),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'sorry, that user already exists')

    def test_user_can_register(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 201
        assert response.content_type == 'application/json'
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'successfully registered'
        assert data['auth_token']


class TestUserLogin(ApiTestCaseMixin):
    def test_it_returns_error_if_payload_is_empty(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_user_does_not_exists(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email=self.random_email(), password=self.random_string())
            ),
            content_type='application/json',
        )

        self.assert_401(response, 'invalid credentials')

    def test_it_returns_error_if_password_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email=user_1.email, password=self.random_email())
            ),
            content_type='application/json',
        )

        self.assert_401(response, 'invalid credentials')

    @pytest.mark.parametrize(
        'text_transformation',
        ['upper', 'lower'],
    )
    def test_user_can_login_regardless_username_case(
        self, app: Flask, user_1: User, text_transformation: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(
                    email=(
                        user_1.email.upper()
                        if text_transformation == 'upper'
                        else user_1.email.lower()
                    ),
                    password='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'successfully logged in'
        assert data['auth_token']


class TestUserProfile(ApiTestCaseMixin):
    def test_it_returns_error_if_auth_token_is_missing(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get('/api/auth/profile')

        self.assert_401(response, 'provide a valid auth token')

    def test_it_returns_error_if_auth_token_is_invalid(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(
            '/api/auth/profile', headers=dict(Authorization='Bearer invalid')
        )

        self.assert_401(response, 'invalid token, please log in again')

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

        assert response.status_code == 200
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

        assert response.status_code == 200
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

        assert response.status_code == 200
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


class TestUserProfileUpdate(ApiTestCaseMixin):
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

    def test_it_returns_error_if_fields_are_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            data=json.dumps(dict(first_name=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_updates_user_profile(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        first_name = self.random_string()
        last_name = self.random_string()
        location = self.random_string()
        bio = self.random_string()
        birth_date = '1980-01-01'

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            data=json.dumps(
                dict(
                    first_name=first_name,
                    last_name=last_name,
                    location=location,
                    bio=bio,
                    birth_date=birth_date,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user profile updated'
        assert data['data']['username'] == user_1.username
        assert data['data']['email'] == user_1.email
        assert not data['data']['admin']
        assert data['data']['created_at']
        assert data['data']['first_name'] == first_name
        assert data['data']['last_name'] == last_name
        assert data['data']['birth_date'] == 'Tue, 01 Jan 1980 00:00:00 GMT'
        assert data['data']['bio'] == bio
        assert data['data']['imperial_units'] is False
        assert data['data']['location'] == location
        assert data['data']['timezone'] is None
        assert data['data']['weekm'] is False
        assert data['data']['language'] is None
        assert data['data']['nb_sports'] == 0
        assert data['data']['nb_workouts'] == 0
        assert data['data']['records'] == []
        assert data['data']['sports_list'] == []
        assert data['data']['total_distance'] == 0
        assert data['data']['total_duration'] == '0:00:00'


class TestUserAccountUpdate(ApiTestCaseMixin):
    @staticmethod
    def assert_no_emails_sent(
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        email_updated_to_current_address_mock.send.assert_not_called()
        email_updated_to_new_address_mock.send.assert_not_called()
        password_change_email_mock.send.assert_not_called()

    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_current_password_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, error_message='current password is missing')

    def test_it_returns_error_if_email_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    password='12345678',
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'email is missing')

    def test_it_returns_error_if_current_password_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password=self.random_string(),
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_401(response, error_message='invalid credentials')

    def test_it_does_not_send_emails_when_error_occurs(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password=self.random_string(),
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_no_emails_sent(
            email_updated_to_current_address_mock,
            email_updated_to_new_address_mock,
            password_change_email_mock,
        )

    def test_it_does_not_returns_error_if_no_new_password_provided(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user account updated'

    def test_it_does_not_send_emails_if_no_change(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_no_emails_sent(
            email_updated_to_current_address_mock,
            email_updated_to_new_address_mock,
            password_change_email_mock,
        )

    def test_it_returns_error_if_new_email_is_invalid(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=self.random_string(),
                    password='12345678',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'email: valid email must be provided\n')

    def test_it_only_updates_email_to_confirm_if_new_email_provided(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        current_email = user_1.email
        new_email = 'new.email@example.com'

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=new_email,
                    password='12345678',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert current_email == user_1.email
        assert new_email == user_1.email_to_confirm
        assert user_1.confirmation_token is not None

    def test_it_calls_email_updated_to_current_email_send_when_new_email_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_email = 'new.email@example.com'

        client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=new_email,
                    password='12345678',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
            environ_base={'HTTP_USER_AGENT': USER_AGENT},
        )

        email_updated_to_current_address_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_1.email,
            },
            {
                'username': user_1.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'linux',
                'browser_name': 'firefox',
                'new_email_address': new_email,
            },
        )

    def test_it_calls_email_updated_to_new_email_send_when_new_email_provided(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_email = 'new.email@example.com'
        expected_token = self.random_string()

        with patch('secrets.token_urlsafe', return_value=expected_token):
            client.patch(
                '/api/auth/profile/edit/account',
                content_type='application/json',
                data=json.dumps(
                    dict(
                        email=new_email,
                        password='12345678',
                    )
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
                environ_base={'HTTP_USER_AGENT': USER_AGENT},
            )

        email_updated_to_new_address_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_1.email_to_confirm,
            },
            {
                'username': user_1.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'linux',
                'browser_name': 'firefox',
                'email_confirmation_url': (
                    f'http://0.0.0.0:5000/email-update?token={expected_token}'
                ),
            },
        )

    def test_it_does_not_calls_password_change_email_send_when_new_email_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_email = 'new.email@example.com'
        expected_token = self.random_string()

        with patch('secrets.token_urlsafe', return_value=expected_token):
            client.patch(
                '/api/auth/profile/edit/account',
                content_type='application/json',
                data=json.dumps(
                    dict(
                        email=new_email,
                        password='12345678',
                    )
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
                environ_base={'HTTP_USER_AGENT': USER_AGENT},
            )

        password_change_email_mock.send.assert_not_called()

    def test_it_returns_error_if_controls_fail_on_new_password(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                    new_password=self.random_string(length=3),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'password: 8 characters required')

    def test_it_updates_auth_user_password_when_new_password_provided(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        current_hashed_password = user_1.password

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user account updated'
        assert current_hashed_password != user_1.password

    def test_new_password_is_hashed(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_password = self.random_string()

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                    new_password=new_password,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert new_password != user_1.password

    def test_it_calls_password_change_email_when_new_password_provided(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
            environ_base={'HTTP_USER_AGENT': USER_AGENT},
        )

        password_change_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_1.email,
            },
            {
                'username': user_1.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'linux',
                'browser_name': 'firefox',
            },
        )

    def test_it_does_not_call_email_updated_emails_send_when_new_password_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=user_1.email,
                    password='12345678',
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        email_updated_to_current_address_mock.send.assert_not_called()
        email_updated_to_new_address_mock.send.assert_not_called()

    def test_it_updates_email_to_confirm_and_password_when_new_email_and_password_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        current_email = user_1.email
        current_hashed_password = user_1.password
        new_email = 'new.email@example.com'

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email=new_email,
                    password='12345678',
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user account updated'
        assert user_1.email == current_email
        assert user_1.email_to_confirm == new_email
        assert user_1.password != current_hashed_password

    def test_it_calls_all_email_send_when_new_email_and_password_provided(
        self,
        app: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            data=json.dumps(
                dict(
                    email='new.email@example.com',
                    password='12345678',
                    new_password=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        email_updated_to_current_address_mock.send.assert_called_once()
        email_updated_to_new_address_mock.send.assert_called_once()
        password_change_email_mock.send.assert_called_once()


class TestUserPreferencesUpdate(ApiTestCaseMixin):
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

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user preferences updated'
        assert data['data']['username'] == user_1.username
        assert data['data']['email'] == user_1.email
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
                    color=self.random_string(),
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
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
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
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        self.assert_403(response, 'error, registration is disabled')

    def test_it_does_not_disable_registration_if_users_count_below_limit(
        self,
        app_with_3_users_max: Flask,
        user_1: User,
    ) -> None:
        client = app_with_3_users_max.test_client()
        client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 201


class TestPasswordResetRequest(ApiTestCaseMixin):
    def test_it_returns_error_on_empty_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_on_invalid_payload(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(username=self.random_string())),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_requests_password_reset_when_user_exists(
        self, app: Flask, user_1: User, user_reset_password_email: Mock
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

    def test_it_calls_reset_password_email_when_user_exists(
        self, app: Flask, user_1: User, reset_password_email: Mock
    ) -> None:
        client = app.test_client()
        token = self.random_string()

        with patch('jwt.encode', return_value=token):
            client.post(
                '/api/auth/password/reset-request',
                data=json.dumps(dict(email='test@test.com')),
                content_type='application/json',
                environ_base={'HTTP_USER_AGENT': USER_AGENT},
            )

        reset_password_email.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_1.email,
            },
            {
                'expiration_delay': '3 seconds',
                'username': user_1.username,
                'password_reset_url': (
                    f'http://0.0.0.0:5000/password-reset?token={token}'
                ),
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'linux',
                'browser_name': 'firefox',
            },
        )

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

    def test_it_does_not_call_reset_password_email_when_user_does_not_exist(
        self, app: Flask, reset_password_email: Mock
    ) -> None:
        client = app.test_client()

        client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(email='test@test.com')),
            content_type='application/json',
        )

        reset_password_email.assert_not_called()


class TestPasswordUpdate(ApiTestCaseMixin):
    def test_it_returns_error_if_payload_is_empty(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_token_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    password=self.random_string(),
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
                    token=self.random_string(),
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
                    password=self.random_string(),
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
                        password=self.random_string(),
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
                    password=self.random_string(length=7),
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'password: 8 characters required\n')

    def test_it_does_not_send_email_after_error(
        self,
        app: Flask,
        user_1: User,
        password_change_email_mock: MagicMock,
    ) -> None:
        token = get_user_token(user_1.id, password_reset=True)
        client = app.test_client()

        client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token=token,
                    password=self.random_string(length=7),
                )
            ),
            content_type='application/json',
        )

        password_change_email_mock.assert_not_called()

    def test_it_updates_password(
        self,
        app: Flask,
        user_1: User,
        password_change_email_mock: MagicMock,
    ) -> None:
        token = get_user_token(user_1.id, password_reset=True)
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token=token,
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'password updated'

    def test_it_send_email_after_successful_update(
        self,
        app: Flask,
        user_1: User,
        password_change_email_mock: MagicMock,
    ) -> None:
        token = get_user_token(user_1.id, password_reset=True)
        client = app.test_client()

        response = client.post(
            '/api/auth/password/update',
            data=json.dumps(
                dict(
                    token=token,
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
            environ_base={'HTTP_USER_AGENT': USER_AGENT},
        )

        assert response.status_code == 200
        password_change_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_1.email,
            },
            {
                'username': user_1.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'linux',
                'browser_name': 'firefox',
            },
        )


class TestEmailUpdateWitUnauthenticatedUser(ApiTestCaseMixin):
    def test_it_returns_error_if_token_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/email/update',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_token_is_invalid(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/email/update',
            data=json.dumps(dict(token=self.random_string())),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_does_not_update_email_if_token_mismatches(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.confirmation_token = self.random_string()
        new_email = 'new.email@example.com'
        user_1.email_to_confirm = new_email
        client = app.test_client()

        response = client.post(
            '/api/auth/email/update',
            data=json.dumps(dict(token=self.random_string())),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_updates_email(self, app: Flask, user_1: User) -> None:
        token = self.random_string()
        user_1.confirmation_token = token
        new_email = 'new.email@example.com'
        user_1.email_to_confirm = new_email
        client = app.test_client()

        response = client.post(
            '/api/auth/email/update',
            data=json.dumps(dict(token=token)),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'email updated'
        assert user_1.email == new_email
        assert user_1.email_to_confirm is None
        assert user_1.confirmation_token is None

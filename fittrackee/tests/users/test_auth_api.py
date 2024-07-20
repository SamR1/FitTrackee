import json
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, Union
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask
from sqlalchemy.dialects.postgresql import insert
from time_machine import travel

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import (
    BlacklistedToken,
    User,
    UserDataExport,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.users.utils.token import get_user_token
from fittrackee.workouts.models import Sport

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict

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

    def test_it_returns_error_if_accepted_policy_is_missing(
        self, app: Flask
    ) -> None:
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

        self.assert_400(response)

    def test_it_returns_error_if_accepted_policy_is_false(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                    accepted_policy=False,
                )
            ),
            content_type='application/json',
        )

        self.assert_400(
            response,
            'sorry, you must agree privacy policy to register',
        )

    def test_it_returns_error_if_username_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    email=self.random_email(),
                    password=self.random_string(),
                    accepted_policy=True,
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
                    accepted_policy=True,
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
                    accepted_policy=True,
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
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'sorry, that username is already taken')

    def test_it_returns_error_if_password_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    accepted_policy=True,
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
                    accepted_policy=True,
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
                    accepted_policy=True,
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
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        self.assert_400(response, 'email: valid email must be provided\n')

    def test_it_does_not_send_email_after_error(
        self, app: Flask, account_confirmation_email_mock: Mock
    ) -> None:
        client = app.test_client()

        client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_string(),
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        account_confirmation_email_mock.send.assert_not_called()

    def test_it_returns_success_if_payload_is_valid(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert 'auth_token' not in data

    def test_it_creates_user_with_default_date_format(
        self, app: Flask
    ) -> None:
        client = app.test_client()
        username = self.random_string()

        client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=username,
                    email=self.random_email(),
                    password=self.random_string(),
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        new_user = User.query.filter_by(username=username).first()
        assert new_user.date_format == 'MM/dd/yyyy'

    @pytest.mark.parametrize(
        'input_language,expected_language',
        [('en', 'en'), ('fr', 'fr'), ('invalid', 'en'), (None, 'en')],
    )
    def test_it_creates_user_with_inactive_account(
        self,
        app: Flask,
        input_language: Optional[str],
        expected_language: str,
    ) -> None:
        client = app.test_client()
        username = self.random_string()
        email = self.random_email()
        accepted_policy_date = datetime.utcnow()

        with patch('fittrackee.users.auth.datetime.datetime') as datetime_mock:
            datetime_mock.utcnow = Mock(return_value=accepted_policy_date)
            client.post(
                '/api/auth/register',
                data=json.dumps(
                    dict(
                        username=username,
                        email=email,
                        password=self.random_string(),
                        language=input_language,
                        accepted_policy=True,
                    )
                ),
                content_type='application/json',
            )

        new_user = User.query.filter_by(username=username).first()
        assert new_user.email == email
        assert new_user.password is not None
        assert new_user.is_active is False
        assert new_user.language == expected_language
        assert new_user.accepted_policy_date == accepted_policy_date

    @pytest.mark.parametrize(
        'input_language,expected_language',
        [('en', 'en'), ('fr', 'fr'), ('invalid', 'en'), (None, 'en')],
    )
    def test_it_calls_account_confirmation_email_when_payload_is_valid(
        self,
        app: Flask,
        account_confirmation_email_mock: Mock,
        input_language: Optional[str],
        expected_language: str,
    ) -> None:
        client = app.test_client()
        email = self.random_email()
        username = self.random_string()
        expected_token = self.random_string()

        with patch('secrets.token_urlsafe', return_value=expected_token):
            client.post(
                '/api/auth/register',
                data=json.dumps(
                    dict(
                        username=username,
                        email=email,
                        password='12345678',
                        language=input_language,
                        accepted_policy=True,
                    )
                ),
                content_type='application/json',
                environ_base={'HTTP_USER_AGENT': USER_AGENT},
            )

        account_confirmation_email_mock.send.assert_called_once_with(
            {
                'language': expected_language,
                'email': email,
            },
            {
                'username': username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
                'account_confirmation_url': (
                    'http://0.0.0.0:5000/account-confirmation'
                    f'?token={expected_token}'
                ),
            },
        )

    def test_it_does_not_call_account_confirmation_email_when_email_sending_is_disabled(  # noqa
        self,
        app_wo_email_activation: Flask,
        account_confirmation_email_mock: Mock,
    ) -> None:
        client = app_wo_email_activation.test_client()
        email = self.random_email()
        username = self.random_string()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=username,
                    email=email,
                    password='12345678',
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
            environ_base={'HTTP_USER_AGENT': USER_AGENT},
        )

        assert response.status_code == 200
        account_confirmation_email_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'text_transformation',
        ['upper', 'lower'],
    )
    def test_it_does_not_return_error_if_a_user_already_exists_with_same_email(
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
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert 'auth_token' not in data

    def test_it_does_not_call_account_confirmation_email_if_user_already_exists(  # noqa
        self, app: Flask, user_1: User, account_confirmation_email_mock: Mock
    ) -> None:
        client = app.test_client()

        client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=self.random_string(),
                    email=user_1.email,
                    password=self.random_string(),
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        account_confirmation_email_mock.send.assert_not_called()


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

    def test_it_returns_error_if_user_account_is_inactive(
        self, app: Flask, inactive_user: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(email=inactive_user.email, password='12345678')
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

        self.assert_invalid_token(response)

    def test_it_returns_error_if_token_is_blacklisted(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        db.session.add(BlacklistedToken(token=auth_token))
        db.session.commit()

        response = client.get(
            '/api/auth/profile',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_invalid_token(response)

    def test_it_returns_user(self, app: Flask, user_1: User) -> None:
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
        assert data['data'] == jsonify_dict(user_1.serialize(user_1))

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self, app: Flask, user_1: User, client_scope: str, can_access: bool
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            '/api/auth/profile',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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
        assert data['data'] == jsonify_dict(user_1.serialize(user_1))

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            '/api/auth/profile/edit',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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

    def test_it_updates_email_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1.email
        )
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
        assert user_1.email == new_email
        assert user_1.email_to_confirm is None
        assert user_1.confirmation_token is None

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
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
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
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
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
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
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

    def test_it_does_not_calls_all_email_send_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1: User,
        email_updated_to_current_address_mock: MagicMock,
        email_updated_to_new_address_mock: MagicMock,
        password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_wo_email_activation, user_1.email
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

        self.assert_no_emails_sent(
            email_updated_to_current_address_mock,
            email_updated_to_new_address_mock,
            password_change_email_mock,
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.patch(
            '/api/auth/profile/edit/account',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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

    @pytest.mark.parametrize(
        'input_language,expected_language',
        [('en', 'en'), ('fr', 'fr'), ('invalid', 'en'), (None, 'en')],
    )
    def test_it_updates_user_preferences(
        self,
        app: Flask,
        user_1: User,
        input_language: Optional[str],
        expected_language: str,
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
                    language=input_language,
                    imperial_units=True,
                    display_ascent=False,
                    start_elevation_at_zero=False,
                    use_dark_mode=True,
                    use_raw_gpx_speed=True,
                    date_format='yyyy-MM-dd',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'user preferences updated'
        assert data['data']['display_ascent'] is False
        assert data['data']['start_elevation_at_zero'] is False
        assert data['data']['use_raw_gpx_speed'] is True
        assert data['data']['imperial_units'] is True
        assert data['data']['language'] == expected_language
        assert data['data']['timezone'] == 'America/New_York'
        assert data['data']['date_format'] == 'yyyy-MM-dd'
        assert data['data']['weekm'] is True
        assert data['data']['use_dark_mode'] is True

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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

    def test_it_updates_default_equipments_for_auth_user_without_existing_preferences(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        sport_2_running: Sport,
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
                    default_equipment_ids=[equipment_shoes_user_1.short_id],
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
        assert data['data']['default_equipments'] == [
            jsonify_dict(equipment_shoes_user_1.serialize())
        ]
        assert data['data']['is_active'] is True
        assert data['data']['stopped_speed_threshold'] == 0.1

    def test_it_updates_default_equipments_for_auth_user_with_existing_preferences(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_shoes_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                ]
            )
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_1_cycling.id,
                    default_equipment_ids=[
                        equipment_bike_user_1.short_id,
                    ],
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
        assert data['data']['default_equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert data['data']['is_active'] is True
        assert data['data']['stopped_speed_threshold'] == 1

    def test_it_does_not_update_equipment_when_ids_not_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        stopped_speed_threshold = 10
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_1_cycling.id,
                    stopped_speed_threshold=stopped_speed_threshold,
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
        assert data['data']['default_equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert data['data']['is_active'] is True
        assert (
            data['data']['stopped_speed_threshold'] == stopped_speed_threshold
        )

    def test_it_cannot_update_default_equipment_for_other_user_equip(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        equipment_shoes_user_1: Equipment,
        sport_2_running: Sport,
    ) -> None:
        # equipment_shoes_user_1 is owned by user 1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=sport_2_running.id,
                    default_equipment_ids=[equipment_shoes_user_1.short_id],
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_shoes_user_1.short_id
        assert data["message"] == (
            f'equipment with id {equipment_shoes_user_1.short_id} '
            'does not exist'
        )
        assert data["status"] == "not_found"

    def test_it_returns_error_when_equipment_is_invalid_for_given_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_shoes_user_1: Equipment,
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
                    default_equipment_ids=[equipment_shoes_user_1.short_id],
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_shoes_user_1.short_id
        assert data["message"] == (
            f"invalid equipment id {equipment_shoes_user_1.short_id} "
            f"for sport {sport_1_cycling.label}"
        )
        assert data["status"] == "invalid"

    def test_it_returns_400_when_multiple_equipments_are_provided(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        equipment_shoes_user_1: Equipment,
        equipment_another_shoes_user_1: Equipment,
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
                    default_equipment_ids=[
                        equipment_shoes_user_1.short_id,
                        equipment_another_shoes_user_1.short_id,
                    ],
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "only one equipment can be added")

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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            '/api/auth/profile/edit/sports',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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
        user_1_sport_1_preference: UserSportPreference,
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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.delete(
            f'/api/auth/profile/reset/sports/{sport_1_cycling.id}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'profile:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            '/api/auth/picture',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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
                    accepted_policy=True,
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
                    accepted_policy=True,
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
                    accepted_policy=True,
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
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200


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

    def test_it_returns_error_when_email_sending_is_disabled(
        self, app_wo_email_activation: Flask
    ) -> None:
        client = app_wo_email_activation.test_client()

        response = client.post(
            '/api/auth/password/reset-request',
            data=json.dumps(dict(email='test@test.com')),
            content_type='application/json',
        )

        self.assert_404_with_message(
            response, 'the requested URL was not found on the server'
        )

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
                'expiration_delay': 'a minute',
                'username': user_1.username,
                'password_reset_url': (
                    f'http://0.0.0.0:5000/password-reset?token={token}'
                ),
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
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

        with travel(now + timedelta(seconds=61), tick=False):
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

    def test_it_sends_email_after_successful_update(
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
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
            },
        )

    def test_it_does_not_send_email_when_email_sending_is_disabled(
        self,
        app_wo_email_activation: Flask,
        user_1: User,
        password_change_email_mock: MagicMock,
    ) -> None:
        token = get_user_token(user_1.id, password_reset=True)
        client = app_wo_email_activation.test_client()

        client.post(
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

        password_change_email_mock.send.assert_not_called()


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


class TestConfirmationAccount(ApiTestCaseMixin):
    def test_it_returns_error_if_token_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/account/confirm',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_returns_error_if_token_is_invalid(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/account/confirm',
            data=json.dumps(dict(token=self.random_string())),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_activates_user_account(
        self, app: Flask, inactive_user: User
    ) -> None:
        token = self.random_string()
        inactive_user.confirmation_token = token
        client = app.test_client()

        response = client.post(
            '/api/auth/account/confirm',
            data=json.dumps(dict(token=token)),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'account confirmation successful'
        assert inactive_user.is_active is True
        assert inactive_user.confirmation_token is None


class TestResendAccountConfirmationEmail(ApiTestCaseMixin):
    def test_it_returns_error_if_email_is_missing(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict()),
            content_type='application/json',
        )

        self.assert_400(response)

    def test_it_does_not_return_error_if_account_does_not_exist(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict(email=self.random_email())),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'confirmation email resent'

    def test_it_does_not_return_error_if_account_already_active(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict(email=user_1.email)),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'confirmation email resent'

    def test_it_does_not_call_account_confirmation_email_if_user_is_active(
        self,
        app: Flask,
        user_1: User,
        account_confirmation_email_mock: Mock,
    ) -> None:
        client = app.test_client()

        client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict(email=user_1.email)),
            content_type='application/json',
            environ_base={'HTTP_USER_AGENT': USER_AGENT},
        )

        account_confirmation_email_mock.send.assert_not_called()

    def test_it_returns_success_if_user_is_inactive(
        self, app: Flask, inactive_user: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict(email=inactive_user.email)),
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'confirmation email resent'

    def test_it_updates_token_if_user_is_inactive(
        self, app: Flask, inactive_user: User
    ) -> None:
        client = app.test_client()
        previous_token = inactive_user.confirmation_token

        client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict(email=inactive_user.email)),
            content_type='application/json',
        )

        assert inactive_user.confirmation_token != previous_token

    def test_it_calls_account_confirmation_email_if_user_is_inactive(
        self,
        app: Flask,
        inactive_user: User,
        account_confirmation_email_mock: Mock,
    ) -> None:
        client = app.test_client()
        expected_token = self.random_string()
        inactive_user.language = 'fr'

        with patch('secrets.token_urlsafe', return_value=expected_token):
            client.post(
                '/api/auth/account/resend-confirmation',
                data=json.dumps(dict(email=inactive_user.email)),
                content_type='application/json',
                environ_base={'HTTP_USER_AGENT': USER_AGENT},
            )

        account_confirmation_email_mock.send.assert_called_once_with(
            {
                'language': inactive_user.language,
                'email': inactive_user.email,
            },
            {
                'username': inactive_user.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'operating_system': 'Linux',
                'browser_name': 'Firefox',
                'account_confirmation_url': (
                    'http://0.0.0.0:5000/account-confirmation'
                    f'?token={expected_token}'
                ),
            },
        )

    def test_it_returns_error_if_email_sending_is_disabled(
        self, app_wo_email_activation: Flask, inactive_user: User
    ) -> None:
        client = app_wo_email_activation.test_client()

        response = client.post(
            '/api/auth/account/resend-confirmation',
            data=json.dumps(dict(email=inactive_user.email)),
            content_type='application/json',
        )

        self.assert_404_with_message(
            response, 'the requested URL was not found on the server'
        )


class TestUserLogout(ApiTestCaseMixin):
    def test_it_returns_error_when_headers_are_missing(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.post('/api/auth/logout', headers=dict())

        self.assert_401(response, 'provide a valid auth token')

    def test_it_returns_error_when_token_is_invalid(self, app: Flask) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/logout', headers=dict(Authorization='Bearer invalid')
        )

        self.assert_invalid_token(response)

    def test_it_returns_error_when_token_is_expired(
        self, app: Flask, user_1: User
    ) -> None:
        now = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with travel(now + timedelta(seconds=61), tick=False):
            response = client.post(
                '/api/auth/logout',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

            self.assert_invalid_token(response)

    def test_user_can_logout(self, app: Flask, user_1: User) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/logout',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == 'successfully logged out'
        assert response.status_code == 200

    def test_token_is_blacklisted_on_logout(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            '/api/auth/logout',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        token = BlacklistedToken.query.filter_by(token=auth_token).first()
        assert token.blacklisted_on is not None

    def test_it_returns_error_if_token_is_already_blacklisted(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        db.session.add(BlacklistedToken(token=auth_token))
        db.session.commit()

        response = client.post(
            '/api/auth/logout',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_invalid_token(response)


class TestUserPrivacyPolicyUpdate(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(dict(accepted_policy=True)),
        )

        self.assert_401(response)

    def test_it_returns_error_if_accepted_policy_is_missing(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/account/privacy-policy',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_updates_accepted_policy(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        accepted_policy_date = datetime.utcnow()

        with travel(accepted_policy_date, tick=False):
            response = client.post(
                '/api/auth/account/privacy-policy',
                content_type='application/json',
                data=json.dumps(dict(accepted_policy=True)),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        assert user_1.accepted_policy_date == accepted_policy_date

    @pytest.mark.parametrize('input_accepted_policy', [False, '', None, 'foo'])
    def test_it_return_error_if_user_has_not_accepted_policy(
        self,
        app: Flask,
        user_1: User,
        input_accepted_policy: Union[str, bool, None],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/account/privacy-policy',
            content_type='application/json',
            data=json.dumps(dict(accepted_policy=input_accepted_policy)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400


@patch('fittrackee.users.auth.export_data')
class TestPostUserDataExportRequest(ApiTestCaseMixin):
    def test_it_returns_data_export_info_when_no_ongoing_request_exists_for_user(  # noqa
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        db.session.add(UserDataExport(user_id=user_2.id))
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        data_export_request = UserDataExport.query.filter_by(
            user_id=user_1.id
        ).first()
        assert data["status"] == "success"
        assert data["request"] == jsonify_dict(data_export_request.serialize())

    def test_it_returns_error_if_ongoing_request_exist(
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        db.session.add(UserDataExport(user_id=user_1.id))
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "ongoing request exists")

    def test_it_returns_error_if_existing_request_has_not_expired(
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        completed_export_request = UserDataExport(user_id=user_1.id)
        db.session.add(completed_export_request)
        completed_export_request.completed = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "completed request already exists")

    def test_it_returns_new_request_if_existing_request_has_expired(  # noqa
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_expiration = app.config["DATA_EXPORT_EXPIRATION"]
        completed_export_request = UserDataExport(
            user_id=user_1.id,
            created_at=datetime.utcnow() - timedelta(hours=export_expiration),
        )
        db.session.add(completed_export_request)
        completed_export_request.completed = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        data_export_request = UserDataExport.query.filter_by(
            user_id=user_1.id
        ).first()
        assert data_export_request.id != completed_export_request.id
        assert data["status"] == "success"
        assert data["request"] == jsonify_dict(data_export_request.serialize())

    def test_it_calls_export_data_tasks_when_request_is_created(
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data_export_request = UserDataExport.query.filter_by(
            user_id=user_1.id
        ).first()
        export_data_mock.send.assert_called_once_with(
            export_request_id=data_export_request.id
        )

    def test_it_does_not_calls_export_data_tasks_when_request_already_exists(
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_expiration = app.config["DATA_EXPORT_EXPIRATION"]
        completed_export_request = UserDataExport(
            user_id=user_1.id,
            created_at=datetime.utcnow() - timedelta(hours=export_expiration),
        )
        db.session.add(completed_export_request)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        export_data_mock.send.assert_not_called()

    def test_it_returns_new_request_if_previous_request_has_expired(
        self,
        export_data_mock: Mock,
        app: Flask,
        user_1: User,
    ) -> None:
        export_expiration = app.config["DATA_EXPORT_EXPIRATION"]
        completed_export_request = UserDataExport(
            user_id=user_1.id,
            created_at=datetime.utcnow() - timedelta(hours=export_expiration),
        )
        db.session.add(completed_export_request)
        completed_export_request.completed = True
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            '/api/auth/account/export/request',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data_export_request = UserDataExport.query.filter_by(
            user_id=user_1.id
        ).first()
        export_data_mock.send.assert_called_once_with(
            export_request_id=data_export_request.id
        )


class TestGetUserDataExportRequest(ApiTestCaseMixin):
    def test_it_returns_none_if_no_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/auth/account/export',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["request"] is None

    def test_it_does_not_return_another_user_existing_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        export_expiration = app.config["DATA_EXPORT_EXPIRATION"]
        completed_export_request = UserDataExport(
            user_id=user_2.id,
            created_at=datetime.utcnow() - timedelta(hours=export_expiration),
        )
        db.session.add(completed_export_request)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/auth/account/export',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["request"] is None

    def test_it_returns_existing_request_for_authenticated_user(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        export_expiration = app.config["DATA_EXPORT_EXPIRATION"]
        completed_export_request = UserDataExport(
            user_id=user_1.id,
            created_at=datetime.utcnow() - timedelta(hours=export_expiration),
        )
        db.session.add(completed_export_request)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/auth/account/export',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["request"] == jsonify_dict(
            completed_export_request.serialize()
        )


class TestDownloadExportDataArchive(ApiTestCaseMixin):
    def test_it_returns_404_when_request_export_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/auth/account/export/{self.random_string()}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'file not found')

    def test_it_returns_404_when_request_export_from_another_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        archive_file_name = self.random_string()
        export_request = UserDataExport(user_id=user_2.id)
        db.session.add(export_request)
        export_request.completed = True
        export_request.file_name = archive_file_name
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/auth/account/export/{archive_file_name}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'file not found')

    def test_it_returns_404_when_file_name_does_not_match(
        self, app: Flask, user_1: User
    ) -> None:
        export_request = UserDataExport(user_id=user_1.id)
        db.session.add(export_request)
        export_request.completed = True
        export_request.file_name = self.random_string()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/auth/account/export/{self.random_string()}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'file not found')

    def test_it_calls_send_from_directory_if_request_exist(
        self, app: Flask, user_1: User
    ) -> None:
        archive_file_name = self.random_string()
        export_request = UserDataExport(user_id=user_1.id)
        db.session.add(export_request)
        export_request.completed = True
        export_request.file_name = archive_file_name
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch('fittrackee.users.auth.send_from_directory') as mock:
            mock.return_value = 'file'

            client.get(
                f'/api/auth/account/export/{archive_file_name}',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        mock.assert_called_once_with(
            f"{app.config['UPLOAD_FOLDER']}/exports/{user_1.id}",
            archive_file_name,
            mimetype='application/zip',
            as_attachment=True,
        )

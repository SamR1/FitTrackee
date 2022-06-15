import json
from typing import Optional

import pytest
from flask import Flask

from fittrackee.application.models import AppConfig
from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestGetConfig(ApiTestCaseMixin):
    def test_it_gets_application_config_for_unauthenticated_user(
        self, app: Flask
    ) -> None:
        app_config = AppConfig.query.first()
        client = app.test_client()

        response = client.get('/api/config')

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data'] == jsonify_dict(app_config.serialize())

    def test_it_gets_application_config(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/config',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']

    def test_it_returns_error_if_application_has_no_config(
        self, app_no_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_no_config, user_1_admin.email
        )

        response = client.get(
            '/api/config',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response, 'error on getting configuration')

    def test_it_returns_error_if_application_has_several_config(
        self, app: Flask, app_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/config',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response, 'error on getting configuration')


class TestUpdateConfig(ApiTestCaseMixin):
    def test_it_updates_config_when_user_is_admin(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['gpx_limit_import'] == 100
        assert data['data']['is_registration_enabled'] is True
        assert data['data']['max_single_file_size'] == 1048576
        assert data['data']['max_zip_file_size'] == 10485760
        assert data['data']['max_users'] == 10

    def test_it_updates_all_config(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        admin_email = self.random_email()

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    admin_contact=admin_email,
                    gpx_limit_import=20,
                    max_single_file_size=10000,
                    max_zip_file_size=25000,
                    max_users=50,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['admin_contact'] == admin_email
        assert data['data']['gpx_limit_import'] == 20
        assert data['data']['is_registration_enabled'] is True
        assert data['data']['max_single_file_size'] == 10000
        assert data['data']['max_zip_file_size'] == 25000
        assert data['data']['max_users'] == 50

    def test_it_returns_403_when_user_is_not_an_admin(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_400_if_invalid_is_payload(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_on_update_if_application_has_no_config(
        self, app_no_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_no_config, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response, 'error when updating configuration')

    def test_it_raises_error_if_archive_max_size_is_below_files_max_size(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    gpx_limit_import=20,
                    max_single_file_size=10000,
                    max_zip_file_size=1000,
                    max_users=50,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response,
            (
                'Max. size of zip archive must be equal or greater than max.'
                ' size of uploaded files'
            ),
        )

    def test_it_raises_error_if_archive_max_size_equals_0(
        self, app_with_max_file_size_equals_0: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size_equals_0, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    max_zip_file_size=0,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, 'Max. size of zip archive must be greater than 0'
        )

    def test_it_raises_error_if_files_max_size_equals_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    max_single_file_size=0,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, 'Max. size of uploaded files must be greater than 0'
        )

    def test_it_raises_error_if_gpx_limit_import_equals_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    gpx_limit_import=0,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, 'Max. files in a zip archive must be greater than 0'
        )

    def test_it_raises_error_if_admin_contact_is_invalid(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    admin_contact=self.random_string(),
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, 'valid email must be provided for admin contact'
        )

    @pytest.mark.parametrize(
        'input_description,input_email', [('input string', ''), ('None', None)]
    )
    def test_it_empties_error_if_admin_contact_is_an_empty(
        self,
        app: Flask,
        user_1_admin: User,
        input_description: str,
        input_email: Optional[str],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        app_config = AppConfig.query.first()
        app_config.admin_contact = self.random_email()

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    admin_contact=input_email,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['admin_contact'] is None

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', True),
            ('profile:read', False),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', False),
        ],
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

import json

from flask import Flask

import fittrackee
from fittrackee.users.models import User

from ..api_test_case import ApiTestCaseMixin


class TestGetConfig(ApiTestCaseMixin):
    def test_it_gets_application_config(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/config',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['gpx_limit_import'] == 10
        assert data['data']['is_registration_enabled'] is True
        assert data['data']['max_single_file_size'] == 1048576
        assert data['data']['max_zip_file_size'] == 10485760
        assert data['data']['max_users'] == 100
        assert data['data']['map_attribution'] == (
            '&copy; <a href="http://www.openstreetmap.org/copyright" '
            'target="_blank" rel="noopener noreferrer">OpenStreetMap</a> '
            'contributors'
        )
        assert data['data']['version'] == fittrackee.__version__

    def test_it_returns_error_if_application_has_no_config(
        self, app_no_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_no_config, as_admin=True
        )

        response = client.get(
            '/api/config',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'error on getting configuration' in data['message']

    def test_it_returns_error_if_application_has_several_config(
        self, app: Flask, app_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.get(
            '/api/config',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'error on getting configuration' in data['message']


class TestUpdateConfig(ApiTestCaseMixin):
    def test_it_updates_config_when_user_is_admin(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
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
            app, as_admin=True
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(
                dict(
                    gpx_limit_import=20,
                    max_single_file_size=10000,
                    max_zip_file_size=25000,
                    max_users=50,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['data']['gpx_limit_import'] == 20
        assert data['data']['is_registration_enabled'] is True
        assert data['data']['max_single_file_size'] == 10000
        assert data['data']['max_zip_file_size'] == 25000
        assert data['data']['max_users'] == 50

    def test_it_returns_403_when_user_is_not_an_admin(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'success' not in data['status']
        assert 'error' in data['status']
        assert 'you do not have permissions' in data['message']

    def test_it_returns_400_if_invalid_is_payload(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'invalid payload' in data['message']

    def test_it_returns_error_on_update_if_application_has_no_config(
        self, app_no_config: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_no_config, as_admin=True
        )

        response = client.patch(
            '/api/config',
            content_type='application/json',
            data=json.dumps(dict(gpx_limit_import=100, max_users=10)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'error when updating configuration' in data['message']

    def test_it_raises_error_if_archive_max_size_is_below_files_max_size(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
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

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert (
            'Max. size of zip archive must be equal or greater than max. size '
            'of uploaded files'
        ) in data['message']

    def test_it_raises_error_if_archive_max_size_equals_0(
        self, app_with_max_file_size_equals_0: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size_equals_0, as_admin=True
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

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert (
            'Max. size of zip archive must be greater than 0'
            in data['message']
        )

    def test_it_raises_error_if_files_max_size_equals_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
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

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert (
            'Max. size of uploaded files must be greater than 0'
            in data['message']
        )

    def test_it_raises_error_if_gpx_limit_import_equals_0(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
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

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert (
            'Max. files in a zip archive must be greater than 0'
            in data['message']
        )

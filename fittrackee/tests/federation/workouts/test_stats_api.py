import json

from flask import Flask

from fittrackee.users.models import User

from ...test_case_mixins import ApiTestCaseMixin


class TestGetAllStats(ApiTestCaseMixin):
    def test_it_returns_local_users_count(
        self, app_with_federation: Flask, user_1_admin: User, remote_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1_admin.email
        )

        response = client.get(
            '/api/stats/all',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['users'] == 1

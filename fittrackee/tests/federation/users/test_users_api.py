import json

from flask import Flask

from fittrackee.users.models import User

from ...test_case_mixins import ApiTestCaseMixin


class TestGetLocalUsers(ApiTestCaseMixin):
    def test_it_gets_users_list(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_3: User,
        remote_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            '/api/users',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 2
        assert data['data']['users'][0]['username'] == user_3.username
        assert data['data']['users'][0]['is_remote'] is False
        assert data['data']['users'][1]['username'] == user_1.username
        assert data['data']['users'][1]['is_remote'] is False


class TestGetRemoteUsers(ApiTestCaseMixin):
    def test_it_gets_users_list(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_3: User,
        remote_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            '/api/users/remote',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0]['username'] == remote_user.username
        assert data['data']['users'][0]['is_remote']

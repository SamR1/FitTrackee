import json
from datetime import datetime
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.users.models import FollowRequest, User

from ..test_case_mixins import ApiTestCaseMixin
from ..utils import random_string


class TestFollowWithoutFederation(ApiTestCaseMixin):
    def test_it_raises_error_if_target_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            f'/api/users/{random_string()}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    def test_it_raises_error_if_target_user_has_already_rejected_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = False
        follow_request_from_user_1_to_user_2.updated_at = datetime.now()
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            f'/api/users/{user_2.username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'you do not have permissions'

    def test_it_creates_follow_request(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            f'/api/users/{user_2.username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{user_2.username}' is sent."
        )

    def test_it_returns_success_if_follow_request_already_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.post(
            f'/api/users/{user_2.username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{user_2.username}' is sent."
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        client.post(
            f'/api/users/{user_2.username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_not_called()

import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.users.models import FollowRequest, User

from ..mixins import ApiTestCaseMixin
from ..utils import random_string


class TestFollowWithoutFederation(ApiTestCaseMixin):
    def test_it_raises_error_if_target_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            f'/api/users/{user_2.username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', True),
            ('profile:write', False),
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
        user_1: User,
        user_2: User,
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
            f'/api/users/{user_2.username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestUnfollowWithoutFederation(ApiTestCaseMixin):
    def test_it_raises_error_if_target_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f'/api/users/{random_string()}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f'/api/users/{user_2.username}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'relationship does not exist'

    def test_it_removes_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f'/api/users/{user_2.username}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == (
            "Undo for a follow request to user "
            f"'{user_2.username}' is sent."
        )
        assert user_1.following.count() == 0

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        client.post(
            f'/api/users/{user_2.username}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('follow:read', False),
            ('follow:write', True),
            ('profile:write', False),
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
        user_1: User,
        user_2: User,
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
            f'/api/users/{user_2.username}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

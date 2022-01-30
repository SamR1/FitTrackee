import json
from datetime import datetime
from unittest.mock import patch

from flask import Flask
from flask.testing import FlaskClient

from fittrackee.users.models import FollowRequest, User

from ..test_case_mixins import ApiTestCaseMixin
from ..utils import random_string


class TestGetFollowRequestWithoutFederation(ApiTestCaseMixin):
    def test_it_returns_empty_list_if_no_follow_request(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['data']['follow_requests'] == []

    def test_it_returns_current_user_pending_follow_requests(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 1
        assert data['data']['follow_requests'][0]['username'] == 'sam'
        assert '@context' not in data['data']['follow_requests'][0]


class TestGetFollowRequestPagination(ApiTestCaseMixin):
    def test_it_returns_pagination(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 2
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    @patch('fittrackee.users.follow_requests.FOLLOW_REQUESTS_PER_PAGE', 1)
    def test_it_returns_second_page(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests?page=2',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 1
        assert data['data']['follow_requests'][0]['username'] == 'sam'
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 2,
        }

    @patch('fittrackee.users.follow_requests.MAX_FOLLOW_REQUESTS_PER_PAGE', 1)
    def test_it_returns_max_follow_request_per_page(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests?per_page=10',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 1
        assert data['data']['follow_requests'][0]['username'] == 'toto'
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 2,
        }

    def test_it_returns_follow_requests_with_descending_order(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests?order=desc',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 2
        assert data['data']['follow_requests'][0]['username'] == 'sam'
        assert data['data']['follow_requests'][1]['username'] == 'toto'

    def test_it_returns_one_request_per_page(
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests?per_page=1',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 1
        assert data['data']['follow_requests'][0]['username'] == 'toto'
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 2,
        }

    def test_it_returns_second_page_with_one_request_per_page_with_descending_order(  # noqa
        self,
        app: Flask,
        user_1: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/follow-requests?page=2&per_page=1&order=desc',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 1
        assert data['data']['follow_requests'][0]['username'] == 'toto'
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 2,
        }


class FollowRequestTestCase(ApiTestCaseMixin):
    def assert_it_returns_follow_request_not_found(
        self,
        client: FlaskClient,
        auth_token: str,
        user_name: str,
        action: str,
    ) -> None:
        url = f'/api/follow-requests/{user_name}/{action}'
        self.assert_return_not_found(
            url, client, auth_token, 'Follow request does not exist.'
        )

    @staticmethod
    def assert_it_returns_follow_request_already_processed(
        client: FlaskClient,
        auth_token: str,
        user_name: str,
        action: str,
    ) -> None:
        url = f'/api/follow-requests/{user_name}/{action}'
        response = client.post(
            url,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == (
            f"Follow request from user '{user_name}' already {action}ed."
        )

    @staticmethod
    def assert_it_returns_follow_request_processed(
        client: FlaskClient,
        auth_token: str,
        user_name: str,
        action: str,
    ) -> None:
        url = f'/api/follow-requests/{user_name}/{action}'
        response = client.post(
            url,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == (
            f"Follow request from user '{user_name}' is {action}ed."
        )


class TestAcceptFollowRequestWithoutFederation(FollowRequestTestCase):
    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_return_user_not_found(
            f'/api/follow-requests/{random_string()}/accept',
            client,
            auth_token,
        )

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_it_returns_follow_request_not_found(
            client, auth_token, user_2.username, 'accept'
        )

    def test_it_raises_error_if_follow_request_already_accepted(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_it_returns_follow_request_already_processed(
            client, auth_token, user_2.username, 'accept'
        )

    def test_it_accepts_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, user_2.username, 'accept'
        )


class TestRejectFollowRequestWithoutFederation(FollowRequestTestCase):
    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_return_user_not_found(
            f'/api/follow-requests/{random_string()}/reject',
            client,
            auth_token,
        )

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_it_returns_follow_request_not_found(
            client, auth_token, user_2.username, 'reject'
        )

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_it_returns_follow_request_already_processed(
            client, auth_token, user_2.username, 'reject'
        )

    def test_it_rejects_follow_request(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, user_2.username, 'reject'
        )

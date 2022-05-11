import json
from datetime import datetime
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.users.models import FollowRequest, User

from ...mixins import ApiTestCaseMixin, UserInboxTestMixin
from ...users.test_users_follow_request_api import FollowRequestTestCase
from ...utils import random_string


class TestGetFollowRequestWithFederation(ApiTestCaseMixin):
    def test_it_returns_empty_list_if_no_follow_request(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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

    def test_it_returns_current_user_follow_requests(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_3_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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
        assert data['data']['follow_requests'][0]['username'] == 'toto'
        assert data['data']['follow_requests'][0]['nb_workouts'] == 0


class TestAcceptLocalFollowRequestWithFederation(FollowRequestTestCase):
    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_return_user_not_found(
            f'/api/follow-requests/{random_string()}/accept',
            client,
            auth_token,
        )

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app_with_federation: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_not_found(
            client, auth_token, user_2.username, 'accept'
        )

    def test_it_raises_error_if_follow_request_already_accepted(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.is_approved = True
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_already_processed(
            client, auth_token, user_2.username, 'accept'
        )

    def test_it_accepts_follow_request(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, user_2.username, 'accept'
        )

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/follow-requests/{user_2.username}/accept',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()


class TestAcceptRemoteFollowRequestWithFederation(
    FollowRequestTestCase, UserInboxTestMixin
):
    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_accepts_follow_request(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_processed(
            client,
            auth_token,
            remote_user.actor.fullname,
            'accept',
        )

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_calls_send_to_user_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/follow-requests/{remote_actor.fullname}/accept',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_actor.user.id,
            followed_user_id=user_1.id,
        ).first()
        self.assert_send_to_remote_inbox_called_once(
            send_to_remote_inbox_mock,
            local_actor=user_1.actor,
            remote_actor=remote_actor,
            base_object=follow_request,
        )


class TestRejectLocalFollowRequestWithFederation(FollowRequestTestCase):
    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_return_user_not_found(
            f'/api/follow-requests/{random_string()}/reject',
            client,
            auth_token,
        )

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app_with_federation: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_not_found(
            client, auth_token, user_2.username, 'reject'
        )

    def test_it_raises_error_if_follow_request_already_accepted(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_already_processed(
            client, auth_token, user_2.username, 'reject'
        )

    def test_it_rejects_follow_request(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, user_2.username, 'reject'
        )

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/follow-requests/{user_2.username}/reject',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_remote_inbox_mock.send.assert_not_called()


class TestRejectRemoteFollowRequestWithFederation(
    FollowRequestTestCase, UserInboxTestMixin
):
    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_accepts_follow_request(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        self.assert_it_returns_follow_request_processed(
            client,
            auth_token,
            remote_user.actor.fullname,
            'reject',
        )

    @patch('fittrackee.users.models.send_to_remote_inbox')
    def test_it_calls_send_to_user_inbox(
        self,
        send_to_remote_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/follow-requests/{remote_actor.fullname}/reject',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_actor.user.id,
            followed_user_id=user_1.id,
        ).first()
        self.assert_send_to_remote_inbox_called_once(
            send_to_remote_inbox_mock,
            local_actor=user_1.actor,
            remote_actor=remote_actor,
            base_object=follow_request,
        )

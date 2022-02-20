import json
from datetime import datetime
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest

from ...test_case_mixins import ApiTestCaseMixin, UserInboxTestMixin
from ...users.test_users_follow_request_api import FollowRequestTestCase
from ...utils import random_string


class TestGetFollowRequestWithFederation(ApiTestCaseMixin):
    def test_it_returns_empty_list_if_no_follow_request(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        response = client.get(
            '/api/follow_requests',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['data']['follow_requests'] == []

    def test_it_returns_current_user_follow_requests_with_actors(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_3_to_user_1.updated_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        response = client.get(
            '/api/follow_requests',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['follow_requests']) == 1
        assert data['data']['follow_requests'][0]['name'] == 'toto'
        assert '@context' in data['data']['follow_requests'][0]


class TestAcceptLocalFollowRequestWithFederation(FollowRequestTestCase):
    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_return_user_not_found(
            f'/api/follow_requests/{random_string()}/accept',
            client,
            auth_token,
        )

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor, actor_2: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_not_found(
            client, auth_token, actor_2.user.username, 'accept'
        )

    def test_it_raises_error_if_follow_request_already_accepted(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1_with_federation.is_approved = True
        follow_request_from_user_2_to_user_1_with_federation.updated_at = (
            datetime.utcnow()
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_already_processed(
            client, auth_token, actor_2.user.username, 'accept'
        )

    def test_it_accepts_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, actor_2.user.username, 'accept'
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        client.post(
            f'/api/follow_requests/{actor_2.user.username}/accept',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_not_called()


class TestAcceptRemoteFollowRequestWithFederation(
    FollowRequestTestCase, UserInboxTestMixin
):
    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_accepts_follow_request(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, remote_actor.fullname, 'accept'  # type: ignore
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_calls_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        client.post(
            f'/api/follow_requests/{remote_actor.fullname}/accept',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_actor.user.id,
            followed_user_id=actor_1.user.id,
        ).first()
        self.assert_send_to_users_inbox_called_once(
            send_to_users_inbox_mock,
            local_actor=actor_1,
            remote_actor=remote_actor,
            base_object=follow_request,
        )


class TestRejectLocalFollowRequestWithFederation(FollowRequestTestCase):
    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_return_user_not_found(
            f'/api/follow_requests/{random_string()}/reject',
            client,
            auth_token,
        )

    def test_it_raises_error_if_follow_request_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor, actor_2: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_not_found(
            client, auth_token, actor_2.user.username, 'reject'
        )

    def test_it_raises_error_if_follow_request_already_accepted(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
    ) -> None:
        follow_request_from_user_2_to_user_1_with_federation.updated_at = (
            datetime.utcnow()
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_already_processed(
            client, auth_token, actor_2.user.username, 'reject'
        )

    def test_it_rejects_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, actor_2.user.username, 'reject'
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        client.post(
            f'/api/follow_requests/{actor_2.user.username}/reject',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_not_called()


class TestRejectRemoteFollowRequestWithFederation(
    FollowRequestTestCase, UserInboxTestMixin
):
    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_accepts_follow_request(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        self.assert_it_returns_follow_request_processed(
            client, auth_token, remote_actor.fullname, 'reject'  # type: ignore
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_calls_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        client.post(
            f'/api/follow_requests/{remote_actor.fullname}/reject',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_actor.user.id,
            followed_user_id=actor_1.user.id,
        ).first()
        self.assert_send_to_users_inbox_called_once(
            send_to_users_inbox_mock,
            local_actor=actor_1,
            remote_actor=remote_actor,
            base_object=follow_request,
        )

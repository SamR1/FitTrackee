import json
from datetime import datetime
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import FollowRequest

from ...test_case_mixins import ApiTestCaseMixin, BaseTestMixin
from ...utils import random_domain, random_string


class TestFollowWithFederation(ApiTestCaseMixin):
    """Follow user belonging to the same instance"""

    def test_it_raises_error_if_target_user_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
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
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = False
        follow_request_from_user_1_to_user_2.updated_at = datetime.now()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        response = client.post(
            f'/api/users/{actor_2.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'you do not have permissions'

    def test_it_creates_follow_request(
        self, app_with_federation: Flask, actor_1: Actor, actor_2: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        response = client.post(
            f'/api/users/{actor_2.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{actor_2.preferred_username}' "
            f"is sent."
        )

    def test_it_returns_success_if_follow_request_already_exists(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        response = client.post(
            f'/api/users/{actor_2.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{actor_2.preferred_username}' "
            f"is sent."
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )

        client.post(
            f'/api/users/{actor_2.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_not_called()


class TestRemoteFollowWithFederation(BaseTestMixin, ApiTestCaseMixin):
    """Follow user from another instance"""

    def test_it_raise_error_if_remote_actor_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        remote_account = f'{random_string()}@{random_domain()}'

        response = client.post(
            f'/api/users/{remote_account}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    def test_it_raise_error_if_remote_actor_does_not_exist_for_existing_remote_domain(  # noqa
        self, app_with_federation: Flask, actor_1: Actor, remote_domain: Domain
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        remote_account = f'{random_string()}@{remote_domain.name}'

        response = client.post(
            f'/api/users/{remote_account}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    @patch('fittrackee.federation.tasks.send_to_users_inbox')
    def test_it_creates_follow_request(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        remote_account = (
            f'{remote_actor.preferred_username}@{remote_actor.domain.name}'
        )

        response = client.post(
            f'/api/users/{remote_account}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{remote_account}' is sent."
        )

    def test_it_returns_success_if_follow_request_already_exists(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        remote_account = (
            f'{remote_actor.preferred_username}@{remote_actor.domain.name}'
        )

        response = client.post(
            f'/api/users/{remote_account}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{remote_account}' is sent."
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_calls_send_to_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        remote_account = (
            f'{remote_actor.preferred_username}@{remote_actor.domain.name}'
        )

        client.post(
            f'/api/users/{remote_account}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_called_once()
        self.assert_call_args_keys_equal(
            send_to_users_inbox_mock.send,
            ['sender_id', 'activity', 'recipients'],
        )
        call_args = self.get_call_kwargs(send_to_users_inbox_mock.send)
        assert call_args['sender_id'] == actor_1.id
        assert call_args['recipients'] == [remote_actor.inbox_url]
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=actor_1.user.id,
            followed_user_id=remote_actor.user.id,
        ).first()
        activity = follow_request.get_activity()
        del activity['id']
        self.assert_dict_contains_subset(call_args['activity'], activity)

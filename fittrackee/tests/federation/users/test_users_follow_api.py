import json
from datetime import datetime
from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.federation.models import Domain
from fittrackee.users.models import FollowRequest, User

from ...test_case_mixins import ApiTestCaseMixin, UserInboxTestMixin
from ...utils import RandomActor, random_string


class TestFollowWithFederation(ApiTestCaseMixin):
    """Follow user belonging to the same instance"""

    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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

    def test_it_raises_error_if_username_matches_only_a_remote_user(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{remote_user.username}/follow',
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
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        follow_request_from_user_1_to_user_2.is_approved = False
        follow_request_from_user_1_to_user_2.updated_at = datetime.now()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{user_2.actor.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'you do not have permissions'

    def test_it_creates_follow_request(
        self, app_with_federation: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{user_2.actor.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{user_2.actor.preferred_username}' "
            f"is sent."
        )

    def test_it_creates_follow_request_with_local_user_when_only_username_provided(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        remote_user: User,
    ) -> None:
        remote_user.username = user_2.username
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{user_2.actor.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{user_2.actor.preferred_username}' "
            f"is sent."
        )

    def test_it_returns_success_if_follow_request_already_exists(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{user_2.actor.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{user_2.actor.preferred_username}' "
            f"is sent."
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/users/{user_2.actor.preferred_username}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_not_called()


class TestRemoteFollowWithFederation(ApiTestCaseMixin, UserInboxTestMixin):
    """Follow user from another instance"""

    def test_it_raise_error_if_remote_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{random_actor.fullname}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    def test_it_raise_error_if_remote_actor_does_not_exist_for_existing_remote_domain(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{random_actor.fullname}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_creates_follow_request(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{remote_actor.fullname}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{remote_actor.fullname}' is sent."
        )

    def test_it_returns_success_if_follow_request_already_exists(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{remote_actor.fullname}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert (
            data['message']
            == f"Follow request to user '{remote_actor.fullname}' is sent."
        )

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_calls_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/users/{remote_actor.fullname}/follow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user_1.id,
            followed_user_id=remote_actor.user.id,
        ).first()
        self.assert_send_to_users_inbox_called_once(
            send_to_users_inbox_mock,
            local_actor=user_1.actor,
            remote_actor=remote_actor,
            base_object=follow_request,
        )


class TestUnfollowWithFederation(ApiTestCaseMixin):
    """Follow user belonging to the same instance"""

    def test_it_raises_error_if_target_user_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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
        self, app_with_federation: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
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

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_does_not_call_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        client.post(
            f'/api/users/{user_2.username}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        send_to_users_inbox_mock.send.assert_not_called()


class TestRemoteUnfollowWithFederation(ApiTestCaseMixin, UserInboxTestMixin):
    """Follow user from another instance"""

    def test_it_raise_error_if_remote_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{random_actor.fullname}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    def test_it_raise_error_if_remote_actor_does_not_exist_for_existing_remote_domain(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{random_actor.fullname}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == 'user does not exist'

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_removes_follow_request(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            f'/api/users/{remote_actor.fullname}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert data['message'] == (
            "Undo for a follow request to user "
            f"'{remote_actor.fullname}' is sent."
        )
        assert user_1.following.count() == 0

    @patch('fittrackee.users.models.send_to_users_inbox')
    def test_it_calls_send_to_user_inbox(
        self,
        send_to_users_inbox_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_actor = remote_user.actor
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user_1.id,
            followed_user_id=remote_actor.user.id,
        ).first()

        client.post(
            f'/api/users/{remote_actor.fullname}/unfollow',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_send_to_users_inbox_called_once(
            send_to_users_inbox_mock,
            local_actor=user_1.actor,
            remote_actor=remote_actor,
            base_object=follow_request,
            activity_args={'undo': True},
        )

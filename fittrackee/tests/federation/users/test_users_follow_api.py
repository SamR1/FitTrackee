import json
from datetime import datetime

from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest

from ...test_case_mixins import ApiTestCaseMixin
from ...utils import random_string


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

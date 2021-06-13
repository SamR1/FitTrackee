import json
from datetime import datetime

from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest

from ...api_test_case import ApiTestCaseMixin


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

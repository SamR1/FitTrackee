import json
from typing import Dict, Tuple
from unittest.mock import Mock, patch

import pytest
import requests
from flask import Flask
from werkzeug.test import TestResponse

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.models import Actor
from fittrackee.federation.signature import signature_header

from ...test_case_mixins import ApiTestCaseMixin
from ...utils import (
    generate_response,
    get_date_string,
    random_domain,
    random_string,
)

# Prevent pytest from collecting TestResponse as test
TestResponse.__test__ = False  # type: ignore


class TestUserInbox(ApiTestCaseMixin):
    @staticmethod
    def post_to_user_inbox(
        app_with_federation: Flask, actor_1: Actor, actor_2: Actor
    ) -> Tuple[Dict, TestResponse]:
        actor_2.generate_keys()
        host = random_domain()
        date_str = get_date_string()
        client = app_with_federation.test_client()
        inbox_path = f'/api/users/{actor_1.preferred_username}/inbox'
        follow_activity: Dict = {
            '@context': AP_CTX,
            'id': random_string(),
            'type': ActivityType.FOLLOW.value,
            'actor': actor_2.activitypub_id,
            'object': actor_1.activitypub_id,
        }

        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_2.serialize(),
            )
            requests_mock.path = inbox_path
            response = client.post(
                inbox_path,
                content_type='application/json',
                headers={
                    'Host': host,
                    'Date': date_str,
                    'Signature': signature_header(
                        host=host,
                        path=inbox_path,
                        date_str=date_str,
                        actor=actor_2,
                    ),
                    'Content-Type': 'application/ld+json',
                },
                data=json.dumps(follow_activity),
            )

        return follow_activity, response

    def test_it_returns_404_if_user_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.post(
            f'/api/users/{random_string()}/inbox',
            content_type='application/json',
            data=json.dumps({}),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    @pytest.mark.parametrize(
        'input_description, input_activity',
        [
            ('empty dict', {}),
            (
                'missing object',
                {'type': ActivityType.FOLLOW.value},
            ),
            ('missing type', {'object': random_string()}),
            (
                'invalid type',
                {'type': random_string(), 'object': random_string()},
            ),
        ],
    )
    def test_it_returns_400_if_activity_is_invalid(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        input_description: str,
        input_activity: Dict,
    ) -> None:
        client = app_with_federation.test_client()

        response = client.post(
            f'/api/users/{actor_1.preferred_username}/inbox',
            content_type='application/json',
            data=json.dumps(input_activity),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'invalid payload' in data['message']

    def test_it_returns_401_if_headers_are_missing(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()
        follow_activity = {
            '@context': AP_CTX,
            'id': random_string(),
            'type': ActivityType.FOLLOW.value,
            'actor': random_string(),
            'object': random_string(),
        }

        response = client.post(
            f'/api/users/{actor_1.preferred_username}/inbox',
            content_type='application/json',
            data=json.dumps(follow_activity),
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'Invalid signature.' in data['message']

    def test_it_returns_401_if_signature_is_invalid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()
        follow_activity = {
            '@context': AP_CTX,
            'id': random_string(),
            'type': ActivityType.FOLLOW.value,
            'actor': random_string(),
            'object': random_string(),
        }

        response = client.post(
            f'/api/users/{actor_1.preferred_username}/inbox',
            content_type='application/json',
            headers={
                'Host': random_string(),
                'Date': random_string(),
                'Signature': random_string(),
            },
            data=json.dumps(follow_activity),
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'Invalid signature.' in data['message']

    @patch('fittrackee.federation.inbox.handle_activity')
    def test_it_returns_200_if_activity_and_signature_are_valid(
        self,
        handle_activity: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
    ) -> None:
        _, response = self.post_to_user_inbox(
            app_with_federation, actor_1, actor_2
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']

    @patch('fittrackee.federation.inbox.handle_activity')
    def test_it_calls_handle_activity_task(
        self,
        handle_activity: Mock,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
    ) -> None:
        activity_dict, response = self.post_to_user_inbox(
            app_with_federation, actor_1, actor_2
        )

        handle_activity.send.assert_called_with(activity=activity_dict)

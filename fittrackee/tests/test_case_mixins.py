import json
import sys
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import Mock

from flask import Flask
from flask.testing import FlaskClient

from fittrackee.federation.models import Actor


class BaseTestMixin:
    @staticmethod
    def get_call_kwargs(mock: Mock) -> Dict:
        return (
            mock.call_args[1]
            if sys.version_info < (3, 8, 0)
            else mock.call_args.kwargs
        )

    def assert_call_args_keys_equal(
        self, mock: Mock, expected_keys: List
    ) -> None:
        args_list = self.get_call_kwargs(mock)
        assert list(args_list.keys()) == expected_keys

    @staticmethod
    def assert_dict_contains_subset(container: Dict, subset: Dict) -> None:
        assert subset.items() <= container.items()


class ApiTestCaseMixin:
    @staticmethod
    def get_test_client_and_auth_token(
        app: Flask, user_email: str
    ) -> Tuple[FlaskClient, str]:
        """user_email must be user_1 or user_2 email"""
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(
                    email=user_email,
                    password=(
                        '87654321'
                        if user_email == 'toto@toto.com'
                        else '12345678'
                    ),
                )
            ),
            content_type='application/json',
        )
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        return client, auth_token

    @staticmethod
    def assert_return_not_found(
        url: str, client: FlaskClient, auth_token: str, message: str
    ) -> None:
        response = client.post(
            url,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data['status'] == 'not found'
        assert data['message'] == message

    def assert_return_user_not_found(
        self, url: str, client: FlaskClient, auth_token: str
    ) -> None:
        self.assert_return_not_found(
            url, client, auth_token, 'user does not exist'
        )


class UserInboxTestMixin(BaseTestMixin):
    def assert_send_to_users_inbox_called_once(
        self,
        send_to_users_inbox_mock: Mock,
        local_actor: Actor,
        remote_actor: Actor,
        base_object: Any,
        activity_args: Optional[Dict] = None,
    ) -> None:
        send_to_users_inbox_mock.send.assert_called_once()
        self.assert_call_args_keys_equal(
            send_to_users_inbox_mock.send,
            ['sender_id', 'activity', 'recipients'],
        )
        call_args = self.get_call_kwargs(send_to_users_inbox_mock.send)
        assert call_args['sender_id'] == local_actor.id
        assert call_args['recipients'] == [remote_actor.inbox_url]
        activity = base_object.get_activity(
            {} if activity_args is None else activity_args
        )
        del activity['id']
        self.assert_dict_contains_subset(call_args['activity'], activity)


class CallArgsMixin:
    @staticmethod
    def get_args(call_args: Any) -> Any:
        if len(call_args) == 2:
            args, _ = call_args
        else:
            _, args, _ = call_args
        return args

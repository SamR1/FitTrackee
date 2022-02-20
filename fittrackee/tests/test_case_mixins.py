import json
import sys
from typing import Any, Dict, List, Tuple
from unittest.mock import Mock

from flask import Flask
from flask.testing import FlaskClient


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
        app: Flask, as_admin: bool = False
    ) -> Tuple[FlaskClient, str]:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(
                    email='admin@example.com' if as_admin else 'test@test.com',
                    password='12345678',
                )
            ),
            content_type='application/json',
        )
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        return client, auth_token


class CallArgsMixin:
    @staticmethod
    def get_args(call_args: Any) -> Any:
        if len(call_args) == 2:
            args, _ = call_args
        else:
            _, args, _ = call_args
        return args

import json
from typing import Any, Tuple

from flask import Flask
from flask.testing import FlaskClient


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


class CallArgsMixin:
    @staticmethod
    def get_args(call_args: Any) -> Any:
        if len(call_args) == 2:
            args, _ = call_args
        else:
            _, args, _ = call_args
        return args

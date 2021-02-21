import json
from typing import Tuple

from flask import Flask
from flask.testing import FlaskClient


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

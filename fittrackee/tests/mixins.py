import json
from typing import Any, Dict, Optional, Tuple

from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from .custom_asserts import assert_errored_response
from .utils import random_email, random_string


class RandomMixin:
    @staticmethod
    def random_string(
        length: Optional[int] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> str:
        return random_string(length, prefix, suffix)

    @staticmethod
    def random_email() -> str:
        return random_email()


class ApiTestCaseMixin(RandomMixin):
    @staticmethod
    def get_test_client_and_auth_token(
        app: Flask, user_email: str
    ) -> Tuple[FlaskClient, str]:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(
                dict(
                    email=user_email,
                    password='12345678',
                )
            ),
            content_type='application/json',
        )
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        return client, auth_token

    @staticmethod
    def assert_400(
        response: TestResponse,
        error_message: Optional[str] = 'invalid payload',
        status: Optional[str] = 'error',
    ) -> Dict:
        return assert_errored_response(
            response, 400, error_message=error_message, status=status
        )

    @staticmethod
    def assert_401(
        response: TestResponse,
        error_message: Optional[str] = 'provide a valid auth token',
    ) -> Dict:
        return assert_errored_response(
            response, 401, error_message=error_message
        )

    @staticmethod
    def assert_403(
        response: TestResponse,
        error_message: Optional[str] = 'you do not have permissions',
    ) -> Dict:
        return assert_errored_response(response, 403, error_message)

    @staticmethod
    def assert_404(response: TestResponse) -> Dict:
        return assert_errored_response(response, 404, status='not found')

    @staticmethod
    def assert_404_with_entity(response: TestResponse, entity: str) -> Dict:
        error_message = f'{entity} does not exist'
        return assert_errored_response(
            response, 404, error_message=error_message, status='not found'
        )

    @staticmethod
    def assert_404_with_message(
        response: TestResponse, error_message: str
    ) -> Dict:
        return assert_errored_response(
            response, 404, error_message=error_message, status='not found'
        )

    @staticmethod
    def assert_413(
        response: TestResponse,
        error_message: Optional[str] = None,
        match: Optional[str] = None,
    ) -> Dict:
        return assert_errored_response(
            response,
            413,
            error_message=error_message,
            status='fail',
            match=match,
        )

    @staticmethod
    def assert_500(
        response: TestResponse,
        error_message: Optional[str] = (
            'error, please try again or contact the administrator'
        ),
        status: Optional[str] = 'error',
    ) -> Dict:
        return assert_errored_response(
            response, 500, error_message=error_message, status=status
        )


class CallArgsMixin:
    @staticmethod
    def get_args(call_args: Any) -> Any:
        if len(call_args) == 2:
            args, _ = call_args
        else:
            _, args, _ = call_args
        return args

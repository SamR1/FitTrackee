from json import dumps

import pytest
from flask import Flask
from werkzeug.test import TestResponse

from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import random_short_id, random_string


class OAuth2ScopesTestCase(ApiTestCaseMixin):
    def assert_expected_response(
        self, response: TestResponse, client_scope: str, endpoint_scope: str
    ) -> None:
        if client_scope == endpoint_scope:
            self.assert_not_insufficient_scope_error(response)
        else:
            self.assert_insufficient_scope(response)


class TestOAuth2ScopesWithReadAccess(OAuth2ScopesTestCase):
    scope = 'read'

    @pytest.mark.parametrize(
        'endpoint_url',
        [
            '/api/auth/profile',
            '/api/records',
            '/api/sports',
            '/api/sports/1',
            f'/api/stats/{random_string()}/by_sport',
            f'/api/stats/{random_string()}/by_time',
            '/api/users/test',
            '/api/workouts',
            f'/api/workouts/{random_short_id()}',
            f'/api/workouts/{random_short_id()}/chart_data',
            f'/api/workouts/{random_short_id()}/chart_data/segment/1',
            f'/api/workouts/{random_short_id()}/gpx',
            f'/api/workouts/{random_short_id()}/gpx/download',
            f'/api/workouts/{random_short_id()}/gpx/segment/1',
        ],
    )
    def test_access_to_get_endpoints(
        self, app: Flask, user_1: User, endpoint_url: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1, scope=self.scope
        )

        response = client.get(
            endpoint_url,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_expected_response(
            response, client_scope=self.scope, endpoint_scope='read'
        )

    @pytest.mark.parametrize(
        'endpoint_url',
        ['/api/users'],
    )
    def test_access_to_endpoints_as_admin(
        self, app: Flask, user_1_admin: User, endpoint_url: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1_admin, scope=self.scope
        )

        response = client.get(
            endpoint_url,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_expected_response(
            response, client_scope=self.scope, endpoint_scope='read'
        )

    @pytest.mark.parametrize(
        'endpoint_url',
        [
            '/api/auth/picture',
            '/api/auth/profile/edit',
            '/api/auth/profile/edit/preferences',
            '/api/auth/profile/edit/sports',
            '/api/workouts',
            '/api/workouts/no_gpx',
        ],
    )
    def test_access_post_endpoints(
        self, app: Flask, user_1: User, endpoint_url: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1, scope=self.scope
        )

        response = client.post(
            endpoint_url,
            data=dumps(dict()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_expected_response(
            response, client_scope=self.scope, endpoint_scope='write'
        )

    @pytest.mark.parametrize(
        'endpoint_url',
        [
            '/api/auth/profile/edit/account',
            '/api/workouts/0',
        ],
    )
    def test_access_to_patch_endpoints(
        self, app: Flask, user_1: User, endpoint_url: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1, scope=self.scope
        )

        response = client.patch(
            endpoint_url,
            data=dumps(dict()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_expected_response(
            response, client_scope=self.scope, endpoint_scope='write'
        )

    @pytest.mark.parametrize(
        'endpoint_url',
        [
            '/api/config',
            '/api/sports/1',
            f'/api/users/{random_string()}',
        ],
    )
    def test_access_to_patch_endpoints_as_admin(
        self, app: Flask, user_1_admin: User, endpoint_url: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1_admin, scope=self.scope
        )

        response = client.patch(
            endpoint_url,
            data=dumps(dict()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_expected_response(
            response, client_scope=self.scope, endpoint_scope='write'
        )

    @pytest.mark.parametrize(
        'endpoint_url',
        [
            '/api/auth/picture',
            '/api/auth/profile/reset/sports/1',
            f'/api/users/{random_string()}',
            '/api/workouts/0',
        ],
    )
    def test_access_to_delete_endpoints(
        self, app: Flask, user_1: User, endpoint_url: str
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1, scope=self.scope
        )
        user_1.picture = random_string()

        response = client.delete(
            endpoint_url,
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_expected_response(
            response, client_scope=self.scope, endpoint_scope='write'
        )


class TestOAuth2ScopesWithWriteAccess(TestOAuth2ScopesWithReadAccess):
    scope = 'write'


class TestOAuth2ScopesWithReadAndWriteAccess(ApiTestCaseMixin):
    scope = 'read write'

    def test_client_can_access_endpoint_with_read_scope(
        self, app: Flask, user_1: User
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1, scope=self.scope
        )

        response = client.get(
            '/api/auth/profile',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_not_insufficient_scope_error(response)

    def test_client_with_read_can_access_endpoints_with_write_scope(
        self, app: Flask, user_1: User
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
        ) = self.create_oauth_client_and_issue_token(
            app, user_1, scope=self.scope
        )

        response = client.post(
            '/api/auth/picture',
            data=dumps(dict()),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_not_insufficient_scope_error(response)

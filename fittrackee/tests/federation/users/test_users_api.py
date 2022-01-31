import json
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import User

from ...test_case_mixins import ApiTestCaseMixin
from ...utils import (
    RandomActor,
    generate_response,
    jsonify_dict,
    random_string,
)


class TestGetLocalUsers(ApiTestCaseMixin):
    def test_it_gets_users_list(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_3: User,
        remote_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            '/api/users',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 2
        assert data['data']['users'][0]['username'] == user_3.username
        assert data['data']['users'][0]['is_remote'] is False
        assert data['data']['users'][1]['username'] == user_1.username
        assert data['data']['users'][1]['is_remote'] is False

    @pytest.mark.parametrize(
        'input_desc, input_username',
        [
            ('not existing user', random_string()),
            ('remote user account', '@sam@example.com'),
        ],
    )
    def test_it_returns_empty_users_list_filtering_on_username(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_desc: str,
        input_username: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/users?q={input_username}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 0,
            'total': 0,
        }


class TestGetRemoteUsers(ApiTestCaseMixin):
    def test_it_gets_users_list(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_3: User,
        remote_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.get(
            '/api/users/remote',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0]['username'] == remote_user.username
        assert data['data']['users'][0]['is_remote']

    def test_it_returns_remote_user_when_query_contains_account(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        with patch(
            'fittrackee.federation.utils_user.update_remote_user',
        ):
            response = client.get(
                f'/api/users/remote?q=@{remote_user.actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            remote_user.serialize(user_1)
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_calls_update_remote_user_when_remote_user_exists(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        with patch(
            'fittrackee.federation.utils_user.update_remote_user',
        ) as update_remote_user_mock:
            client.get(
                f'/api/users/remote?q=@{remote_user.actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        update_remote_user_mock.assert_called_with(remote_user.actor)

    def test_it_does_not_call_update_remote_user_for_local_user(
        self, app_with_federation: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        with patch(
            'fittrackee.federation.utils_user.update_remote_user',
        ) as update_remote_user_mock:
            client.get(
                f'/api/users/remote?q={user_2.username}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        update_remote_user_mock.assert_not_called()

    def test_it_creates_and_returns_remote_user(
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):
            response = client.get(
                f'/api/users/remote?q=@{random_actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0]['username'] == random_actor.name
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_empty_list_if_remote_user_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            side_effect={},
        ):
            response = client.get(
                f'/api/users/remote?q=@{random_actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 0,
            'total': 0,
        }


class TestDeleteUser(ApiTestCaseMixin):
    def test_it_deletes_actor_when_deleting_user(
        self, app_with_federation: Flask, user_1_admin: User, user_2: User
    ) -> None:
        actor_id = user_2.actor_id
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1_admin.email
        )

        client.delete(
            f'/api/users/{user_2.username}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert Actor.query.filter_by(id=actor_id).first() is None


class TestGetRemoteUser(ApiTestCaseMixin):
    def test_it_returns_error_if_remote_user_does_not_exists(
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        with patch(
            'requests.get', return_value=generate_response(status_code=404)
        ):

            response = client.get(
                f'/api/users/@{random_actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_it_returns_remote_user_if_exists(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        with patch(
            'fittrackee.federation.utils_user.update_remote_user',
        ):

            response = client.get(
                f'/api/users/@{remote_user.actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0]['username'] == remote_user.username

    def test_it_calls_update_remote_user(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )
        with patch(
            'fittrackee.federation.utils_user.update_remote_user',
        ) as update_remote_user_mock:

            client.get(
                f'/api/users/@{remote_user.actor.fullname}',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        update_remote_user_mock.assert_called_with(remote_user.actor)


class TestGetUserPicture(ApiTestCaseMixin):
    def test_it_returns_error_if_local_user_with_same_username_does_not_exist(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(f'/api/users/{remote_user.username}/picture')

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']


class TestUpdateUser(ApiTestCaseMixin):
    def test_it_updates_local_user_when_remote_user_exists_with_same_username(
        self,
        app_with_federation: Flask,
        user_1_admin: User,
        remote_user: User,
        user_2: User,
    ) -> None:
        remote_user.username = user_2.username
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(admin=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user['email'] == user_2.email
        assert user['is_remote'] is False

    def test_it_raise_error_when_updating_remote_user(
        self,
        app_with_federation: Flask,
        user_1_admin: User,
        remote_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/@{remote_user.actor.fullname}',
            content_type='application/json',
            data=json.dumps(dict(admin=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'invalid payload' in data['message']

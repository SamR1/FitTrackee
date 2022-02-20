import json
from unittest.mock import patch
from uuid import uuid4

from flask import Flask

from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.users.models import User

from ...test_case_mixins import ApiTestCaseMixin
from ...utils import RandomActor


class TestFederationUser:
    def test_it_returns_404_if_user_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            f'/federation/user/{uuid4().hex}',
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_it_returns_json_resource_descriptor_as_content_type(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            f'/federation/user/{actor_1.preferred_username}',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/jrd+json; charset=utf-8'

    def test_it_returns_actor(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            f'/federation/user/{actor_1.preferred_username}',
        )

        data = json.loads(response.data.decode())
        assert data == actor_1.serialize()

    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask, app_actor: Actor
    ) -> None:
        client = app.test_client()
        response = client.get(
            f'/federation/user/{app_actor.preferred_username}',
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'error, federation is disabled for this instance'
            in data['message']
        )


class TestRemoteUser(ApiTestCaseMixin):
    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask, user_1: User, random_actor: RandomActor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.post(
            '/federation/remote-user',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
            data=json.dumps({'actor_url': random_actor.activitypub_id}),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'error, federation is disabled for this instance'
            in data['message']
        )

    def test_it_returns_error_if_user_is_not_logged(
        self, app_with_federation: Flask, random_actor: RandomActor
    ) -> None:
        client = app_with_federation.test_client()
        response = client.post(
            '/federation/remote-user',
            content_type='application/json',
            data=json.dumps({'actor_url': random_actor.activitypub_id}),
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'provide a valid auth token' in data['message']

    def test_it_returns_400_if_remote_user_url_is_missing(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, actor_1.user.email
        )
        response = client.post(
            '/federation/remote-user',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'Invalid remote actor: invalid remote actor url.'
            in data['message']
        )

    def test_it_returns_error_if_create_remote_user_returns_error(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        random_actor: RandomActor,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, actor_1.user.email
        )
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.side_effect = ActorNotFoundException()
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps({'actor_url': random_actor.activitypub_id}),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert 'error' in data['status']
            assert (
                'Invalid remote actor: can not fetch remote actor.'
                in data['message']
            )

    def test_it_creates_remote_actor_if_actor_and_domain_dont_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        random_actor: RandomActor,
    ) -> None:
        remote_user_object = random_actor.get_remote_user_object()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, actor_1.user.email
        )
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps({'actor_url': random_actor.activitypub_id}),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert data == remote_user_object

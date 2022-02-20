import json
from unittest.mock import patch
from uuid import uuid4

from flask import Flask

from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import User

from ...test_case_mixins import ApiTestCaseMixin
from ...utils import (
    get_remote_user_object,
    random_actor_url,
    random_domain_with_scheme,
    random_string,
)


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
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)
        response = client.post(
            '/federation/remote-user',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
            data=json.dumps({'actor_url': random_actor_url()}),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'error, federation is disabled for this instance'
            in data['message']
        )

    def test_it_returns_error_if_user_is_not_logged(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()
        response = client.post(
            '/federation/remote-user',
            content_type='application/json',
            data=json.dumps({'actor_url': random_actor_url()}),
        )

        assert response.status_code == 401
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'provide a valid auth token' in data['message']

    def test_it_returns_400_if_remote_user_url_is_missing(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        response = client.post(
            '/federation/remote-user',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'invalid payload' in data['message']

    def test_it_returns_error_if_remote_instance_returns_error(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.side_effect = ActorNotFoundException()
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps({'actor_url': random_actor_url()}),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert 'error' in data['status']
            assert 'Can not fetch remote actor.' in data['message']

    def test_it_returns_error_if_remote_actor_object_is_invalid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = {}
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps({'actor_url': random_actor_url()}),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert 'error' in data['status']
            assert 'Invalid remote actor object.' in data['message']

    def test_it_returns_error_if_keys_are_missing_in_remote_actor_object(
        self, app_with_federation: Flask, actor_1: Actor, remote_domain: Domain
    ) -> None:
        remote_username = random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = {
                'preferredUsername': remote_username,
            }
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps(
                    {
                        'actor_url': random_actor_url(
                            username=remote_username,
                            domain_with_scheme=f'https://{remote_domain.name}',
                        )
                    }
                ),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert 'error' in data['status']
            assert 'Invalid remote actor object.' in data['message']

    def test_it_returns_error_if_remote_domain_is_local_domain(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
    ) -> None:
        remote_username = random_string()
        domain = f"https://{ app_with_federation.config['AP_DOMAIN']}"
        remote_user_object = get_remote_user_object(
            username=remote_username, domain_with_scheme=domain
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps(
                    {
                        'actor_url': random_actor_url(
                            username=remote_username, domain_with_scheme=domain
                        )
                    }
                ),
            )

            assert response.status_code == 400
            data = json.loads(response.data.decode())
            assert 'error' in data['status']
            assert (
                'The provided account is not a remote account.'
                in data['message']
            )

    def test_it_creates_remote_actor_if_actor_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor, remote_domain: Domain
    ) -> None:
        remote_username = random_string()
        remote_preferred_username = random_string()
        domain = f'https://{remote_domain.name}'
        remote_user_object = get_remote_user_object(
            username=remote_username,
            preferred_username=remote_preferred_username,
            domain_with_scheme=domain,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps(
                    {
                        'actor_url': random_actor_url(
                            username=remote_preferred_username,
                            domain_with_scheme=domain,
                        )
                    }
                ),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert data == remote_user_object

    def test_it_creates_remote_actor_if_actor_and_domain_dont_exist(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        remote_username = random_string()
        remote_preferred_username = random_string()
        domain = random_domain_with_scheme()
        remote_user_object = get_remote_user_object(
            username=remote_username,
            preferred_username=remote_preferred_username,
            domain_with_scheme=domain,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps(
                    {
                        'actor_url': random_actor_url(
                            username=remote_preferred_username,
                            domain_with_scheme=domain,
                        )
                    }
                ),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert data == remote_user_object

    def test_it_returns_updated_remote_actor_if_remote_domain_exists(
        self, app_with_federation: Flask, actor_1: Actor, remote_actor: Actor
    ) -> None:
        remote_user_object = remote_actor.serialize()
        updated_name = random_string()
        remote_user_object['name'] = updated_name
        last_fetched = remote_actor.last_fetch_date
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps({'actor_url': remote_actor.activitypub_id}),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert data == remote_user_object
            assert remote_actor.name == updated_name
            assert remote_actor.last_fetch_date != last_fetched

    def test_it_creates_several_remote_actors(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        """
        check constrains on User model (especially empty password and email)
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation
        )
        with patch(
            'fittrackee.federation.federation.get_remote_user'
        ) as get_remote_user_mock:
            remote_preferred_username = random_string()
            domain = random_domain_with_scheme()
            remote_user_object = get_remote_user_object(
                preferred_username=remote_preferred_username,
                domain_with_scheme=domain,
            )
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps(
                    {
                        'actor_url': random_actor_url(
                            username=remote_preferred_username,
                            domain_with_scheme=domain,
                        )
                    }
                ),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert data == remote_user_object

            remote_preferred_username = random_string()
            domain = random_domain_with_scheme()
            remote_user_object = get_remote_user_object(
                preferred_username=remote_preferred_username,
                domain_with_scheme=domain,
            )
            get_remote_user_mock.return_value = remote_user_object
            response = client.post(
                '/federation/remote-user',
                content_type='application/json',
                headers=dict(Authorization=f'Bearer {auth_token}'),
                data=json.dumps(
                    {
                        'actor_url': random_actor_url(
                            username=remote_preferred_username,
                            domain_with_scheme=domain,
                        )
                    }
                ),
            )

            assert response.status_code == 200
            data = json.loads(response.data.decode())
            assert data == remote_user_object

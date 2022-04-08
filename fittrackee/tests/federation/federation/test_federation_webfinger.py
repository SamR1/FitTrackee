import json
from uuid import uuid4

from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import User

from ...mixins import ApiTestCaseMixin


class TestWebfinger(ApiTestCaseMixin):
    def test_it_returns_400_if_resource_is_missing(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            '/.well-known/webfinger',
            content_type='application/json',
        )

        self.assert_400(response, 'Missing resource in request args.')

    def test_it_returns_400_if_account_is_missing(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            '/.well-known/webfinger?resource=test@example.com',
            content_type='application/json',
        )

        self.assert_400(response, 'Missing resource in request args.')

    def test_it_returns_400_if_argument_is_invalid(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/.well-known/webfinger?resource=acct:{uuid4().hex}',
            content_type='application/json',
        )

        self.assert_400(response, 'Invalid resource.')

    def test_it_returns_404_if_user_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        domain = app_with_federation.config['AP_DOMAIN']
        client = app_with_federation.test_client()

        response = client.get(
            f'/.well-known/webfinger?resource=acct:{uuid4().hex}@{domain}',
            content_type='application/json',
        )

        self.assert_404_with_entity(response, 'user')

    def test_it_returns_404_if_domain_is_not_instance_domain(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            '/.well-known/webfinger?resource=acct:'
            f'{user_1.actor.preferred_username}@{uuid4().hex}',
            content_type='application/json',
        )

        self.assert_404_with_entity(response, 'user')

    def test_it_returns_json_resource_descriptor_as_content_type(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            '/.well-known/webfinger?resource=acct:' f'{user_1.actor.fullname}',
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/jrd+json; charset=utf-8'

    def test_it_returns_subject_with_user_data(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        client = app_with_federation.test_client()

        response = client.get(
            '/.well-known/webfinger?resource=acct:' f'{actor_1.fullname}',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert f'acct:{actor_1.fullname}' in data['subject']

    def test_it_returns_user_links(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        client = app_with_federation.test_client()

        response = client.get(
            '/.well-known/webfinger?resource=acct:' f'{actor_1.fullname}',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['links'] == [
            {
                'href': (
                    f'https://{actor_1.domain.name}/users/'
                    f'{actor_1.user.username}'
                ),
                'rel': 'http://webfinger.net/rel/profile-page',
                'type': 'text/html',
            },
            {
                'href': actor_1.activitypub_id,
                'rel': 'self',
                'type': 'application/activity+json',
            },
        ]

    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask, app_actor: Actor
    ) -> None:
        client = app.test_client()

        response = client.get(
            '/.well-known/webfinger?resource=acct:' f'{app_actor.fullname}',
            content_type='application/json',
        )

        self.assert_403(
            response,
            'error, federation is disabled for this instance',
        )

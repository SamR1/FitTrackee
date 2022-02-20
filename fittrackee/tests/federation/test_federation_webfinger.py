import json
from uuid import uuid4

from flask import Flask

from fittrackee.federation.models import Actor


class TestWebfinger:
    def test_it_returns_400_if_resource_is_missing(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/webfinger',
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'Missing resource in request args.' in data['message']

    def test_it_returns_400_if_account_is_missing(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/webfinger?resource=test@example.com',
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'Missing resource in request args.' in data['message']

    def test_it_returns_400_if_argument_is_invalid(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            f'/.well-known/webfinger?resource=acct:{uuid4().hex}',
            content_type='application/json',
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'Invalid resource.' in data['message']

    def test_it_returns_404_if_user_does_not_exist(self, app: Flask) -> None:
        domain = app.config['AP_DOMAIN']
        client = app.test_client()
        response = client.get(
            f'/.well-known/webfinger?resource=acct:{uuid4().hex}@{domain}',
            content_type='application/json',
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_it_returns_404_if_domain_is_not_instance_domain(
        self, app: Flask, actor_1: Actor
    ) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/webfinger?resource=acct:'
            f'{actor_1.preferred_username}@{uuid4().hex}',
            content_type='application/json',
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_it_returns_json_resource_descriptor_as_content_type(
        self, app: Flask, actor_1: Actor
    ) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/webfinger?resource=acct:'
            f'{actor_1.preferred_username}@{actor_1.domain}',
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/jrd+json; charset=utf-8'

    def test_it_returns_subject_with_user_data(
        self, app: Flask, actor_1: Actor
    ) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/webfinger?resource=acct:'
            f'{actor_1.preferred_username}@{actor_1.domain}',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert (
            f'acct:{actor_1.preferred_username}@{actor_1.domain}'
            in data['subject']
        )

    def test_it_returns_user_links(self, app: Flask, actor_1: Actor) -> None:
        client = app.test_client()
        response = client.get(
            '/.well-known/webfinger?resource=acct:'
            f'{actor_1.preferred_username}@{actor_1.domain}',
            content_type='application/json',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['links'][0] == {
            'href': actor_1.ap_id,
            'rel': 'self',
            'type': 'application/activity+json',
        }

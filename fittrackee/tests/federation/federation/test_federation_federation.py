import json
from unittest.mock import patch
from uuid import uuid4

from flask import Flask

from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest, User

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


class TestLocalActorFollowers(ApiTestCaseMixin):
    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/followers',
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'error, federation is disabled for this instance'
            in data['message']
        )

    def test_it_returns_404_if_actor_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/followers',
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_it_returns_ordered_collection_without_follower(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': actor_1.followers_url,
            'type': 'OrderedCollection',
            'totalItems': 0,
            'first': f'{actor_1.followers_url}?page=1',
        }

    def test_it_returns_first_page_without_followers(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=1',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.followers_url}?page=1',
            'type': 'OrderedCollectionPage',
            'totalItems': 0,
            'partOf': actor_1.followers_url,
            'orderedItems': [],
        }

    def test_it_returns_error_if_page_is_invalid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=un',
        )

        assert response.status_code == 500
        data = json.loads(response.data.decode())
        assert data == {
            'message': 'error, please try again or contact the administrator',
            'status': 'error',
        }

    def test_it_does_not_return_error_when_page_that_does_not_return_followers(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=2',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.followers_url}?page=2',
            'type': 'OrderedCollectionPage',
            'totalItems': 0,
            'partOf': actor_1.followers_url,
            'orderedItems': [],
        }

    def test_it_returns_first_page_with_followers(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
        follow_request_from_user_3_to_user_1_with_federation: FollowRequest,
    ) -> None:
        actor_1.user.approves_follow_request_from(actor_2.user)
        actor_1.user.approves_follow_request_from(actor_3.user)
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=1',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.followers_url}?page=1',
            'type': 'OrderedCollectionPage',
            'totalItems': 2,
            'partOf': actor_1.followers_url,
            'orderedItems': [actor_3.activitypub_id, actor_2.activitypub_id],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_first_page_with_next_page_link(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
        follow_request_from_user_3_to_user_1_with_federation: FollowRequest,
    ) -> None:
        actor_1.user.approves_follow_request_from(actor_2.user)
        actor_1.user.approves_follow_request_from(actor_3.user)
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=1',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.followers_url}?page=1',
            'type': 'OrderedCollectionPage',
            'totalItems': 2,
            'partOf': actor_1.followers_url,
            'next': f'{actor_1.followers_url}?page=2',
            'orderedItems': [
                actor_3.activitypub_id,
            ],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_next_page(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_2_to_user_1_with_federation: FollowRequest,
        follow_request_from_user_3_to_user_1_with_federation: FollowRequest,
    ) -> None:
        actor_1.user.approves_follow_request_from(actor_2.user)
        actor_1.user.approves_follow_request_from(actor_3.user)
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=2',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.followers_url}?page=2',
            'type': 'OrderedCollectionPage',
            'totalItems': 2,
            'partOf': actor_1.followers_url,
            'prev': f'{actor_1.followers_url}?page=1',
            'orderedItems': [
                actor_2.activitypub_id,
            ],
        }


class TestLocalActorFollowing(ApiTestCaseMixin):
    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/following',
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'error, federation is disabled for this instance'
            in data['message']
        )

    def test_it_returns_404_if_actor_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/following',
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_it_returns_ordered_collection_without_following(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/following',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': actor_1.following_url,
            'type': 'OrderedCollection',
            'totalItems': 0,
            'first': f'{actor_1.following_url}?page=1',
        }

    def test_it_returns_first_page_without_following(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/following?page=1',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.following_url}?page=1',
            'type': 'OrderedCollectionPage',
            'totalItems': 0,
            'partOf': actor_1.following_url,
            'orderedItems': [],
        }

    def test_it_returns_error_if_page_is_invalid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/following?page=un',
        )

        assert response.status_code == 500
        data = json.loads(response.data.decode())
        assert data == {
            'message': 'error, please try again or contact the administrator',
            'status': 'error',
        }

    def test_it_does_not_return_error_when_page_that_does_not_return_following(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/following?page=2',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_1.following_url}?page=2',
            'type': 'OrderedCollectionPage',
            'totalItems': 0,
            'partOf': actor_1.following_url,
            'orderedItems': [],
        }

    def test_it_returns_first_page_with_following_users(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_3_to_user_2_with_federation: FollowRequest,
        follow_request_from_user_3_to_user_1_with_federation: FollowRequest,
    ) -> None:
        actor_1.user.approves_follow_request_from(actor_3.user)
        actor_2.user.approves_follow_request_from(actor_3.user)
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_3.preferred_username}/following?page=1',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_3.following_url}?page=1',
            'type': 'OrderedCollectionPage',
            'totalItems': 2,
            'partOf': actor_3.following_url,
            'orderedItems': [actor_2.activitypub_id, actor_1.activitypub_id],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_first_page_with_next_page_link(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_3_to_user_2_with_federation: FollowRequest,
        follow_request_from_user_3_to_user_1_with_federation: FollowRequest,
    ) -> None:
        actor_1.user.approves_follow_request_from(actor_3.user)
        actor_2.user.approves_follow_request_from(actor_3.user)
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_3.preferred_username}/following?page=1',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_3.following_url}?page=1',
            'type': 'OrderedCollectionPage',
            'totalItems': 2,
            'partOf': actor_3.following_url,
            'next': f'{actor_3.following_url}?page=2',
            'orderedItems': [
                actor_2.activitypub_id,
            ],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_next_page(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        actor_3: Actor,
        follow_request_from_user_3_to_user_2_with_federation: FollowRequest,
        follow_request_from_user_3_to_user_1_with_federation: FollowRequest,
    ) -> None:
        actor_1.user.approves_follow_request_from(actor_3.user)
        actor_2.user.approves_follow_request_from(actor_3.user)
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_3.preferred_username}/following?page=2',
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data == {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': f'{actor_3.following_url}?page=2',
            'type': 'OrderedCollectionPage',
            'totalItems': 2,
            'partOf': actor_3.following_url,
            'prev': f'{actor_3.following_url}?page=1',
            'orderedItems': [
                actor_1.activitypub_id,
            ],
        }

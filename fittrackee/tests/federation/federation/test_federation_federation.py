import json
from unittest.mock import patch
from uuid import uuid4

from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest, User

from ...mixins import ApiTestCaseMixin


class TestFederationUser(ApiTestCaseMixin):
    def test_it_returns_404_if_user_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            f'/federation/user/{uuid4().hex}',
        )

        self.assert_404_with_entity(response, 'user')

    def test_it_returns_json_resource_descriptor_as_content_type(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            f'/federation/user/{user_1.actor.preferred_username}',
        )

        assert response.status_code == 200
        assert response.content_type == 'application/jrd+json; charset=utf-8'

    def test_it_returns_actor(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        client = app_with_federation.test_client()
        response = client.get(
            f'/federation/user/{user_1.actor.preferred_username}',
        )

        data = json.loads(response.data.decode())
        assert data == user_1.actor.serialize()

    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask, app_actor: Actor
    ) -> None:
        client = app.test_client()
        response = client.get(
            f'/federation/user/{app_actor.preferred_username}',
        )

        self.assert_403(
            response,
            'error, federation is disabled for this instance',
        )


class TestLocalActorFollowers(ApiTestCaseMixin):
    def test_it_returns_error_if_federation_is_disabled(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/followers',
        )

        self.assert_403(
            response,
            'error, federation is disabled for this instance',
        )

    def test_it_returns_404_if_actor_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/followers',
        )

        self.assert_404_with_entity(response, 'user')

    def test_it_returns_ordered_collection_without_follower(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
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
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
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
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/followers?page=un',
        )

        self.assert_500(response)

    def test_it_does_not_return_error_when_page_that_does_not_return_followers(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
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
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        actor_1 = user_1.actor
        user_1.approves_follow_request_from(user_2)
        user_1.approves_follow_request_from(user_3)
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
            'orderedItems': [
                user_3.actor.activitypub_id,
                user_2.actor.activitypub_id,
            ],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_first_page_with_next_page_link(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        actor_1 = user_1.actor
        user_1.approves_follow_request_from(user_2)
        user_1.approves_follow_request_from(user_3)
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
                user_3.actor.activitypub_id,
            ],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_next_page(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_2_to_user_1: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        actor_1 = user_1.actor
        user_1.approves_follow_request_from(user_2)
        user_1.approves_follow_request_from(user_3)
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
                user_2.actor.activitypub_id,
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

        self.assert_403(
            response,
            'error, federation is disabled for this instance',
        )

    def test_it_returns_404_if_actor_does_not_exist(
        self, app_with_federation: Flask
    ) -> None:
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{uuid4().hex}/following',
        )

        self.assert_404_with_entity(response, 'user')

    def test_it_returns_ordered_collection_without_following(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
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
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
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
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        client = app_with_federation.test_client()

        response = client.get(
            f'/federation/user/{actor_1.preferred_username}/following?page=un',
        )

        self.assert_500(response)

    def test_it_does_not_return_error_when_page_that_does_not_return_following(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
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
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        actor_3 = user_3.actor
        user_1.approves_follow_request_from(user_3)
        user_2.approves_follow_request_from(user_3)
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
            'orderedItems': [
                user_2.actor.activitypub_id,
                user_1.actor.activitypub_id,
            ],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_first_page_with_next_page_link(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        actor_3 = user_3.actor
        user_1.approves_follow_request_from(user_3)
        user_2.approves_follow_request_from(user_3)
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
                user_2.actor.activitypub_id,
            ],
        }

    @patch('fittrackee.federation.federation.USERS_PER_PAGE', 1)
    def test_it_returns_next_page(
        self,
        app_with_federation: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        follow_request_from_user_3_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_1: FollowRequest,
    ) -> None:
        actor_3 = user_3.actor
        user_1.approves_follow_request_from(user_3)
        user_2.approves_follow_request_from(user_3)
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
                user_1.actor.activitypub_id,
            ],
        }

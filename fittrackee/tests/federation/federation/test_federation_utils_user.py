import os
from typing import Dict, Union
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.federation.exceptions import (
    ActorNotFoundException,
    RemoteActorException,
)
from fittrackee.federation.models import Actor, Domain
from fittrackee.federation.utils_user import (
    create_remote_user,
    get_user_from_username,
    get_username_and_domain,
    store_or_delete_user_picture,
    update_remote_actor_stats,
)
from fittrackee.files import get_absolute_file_path
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User

from ...utils import RandomActor, generate_response, random_string


class TestGetUsernameAndDomain:
    @pytest.mark.parametrize(
        'input_user_account, expected_username_and_domain',
        [
            ('@sam@example.com', ('sam', 'example.com')),
            (
                '@john.doe@test.example.social',
                ('john.doe', 'test.example.social'),
            ),
        ],
    )
    def test_it_returns_user_name_and_domain(
        self,
        input_user_account: str,
        expected_username_and_domain: Union[str, None],
    ) -> None:
        assert (
            get_username_and_domain(input_user_account)
            == expected_username_and_domain
        )

    @pytest.mark.parametrize(
        'input_description, input_user_account',
        [
            ('sam', 'sam'),
            ('@sam', '@sam'),
            ('sam@', 'sam@'),
            ('example.com', 'example.com'),
            ('@example.com', '@example.com'),
        ],
    )
    def test_it_returns_none_if_it_does_not_match(
        self,
        input_description: str,
        input_user_account: str,
    ) -> None:
        assert get_username_and_domain(input_user_account) == (None, None)


class TestCreateRemoteUser:
    def test_it_returns_error_if_remote_actor_domain_is_local(
        self, app_with_federation: Flask
    ) -> None:
        with pytest.raises(
            RemoteActorException,
            match=(
                'Invalid remote actor: '
                'the provided account is not a remote account.'
            ),
        ):

            create_remote_user(
                random_string(), app_with_federation.config["UI_URL"]
            )

    def test_it_returns_error_if_remote_webfinger_returns_error(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            side_effect=ActorNotFoundException(),
        ), pytest.raises(
            RemoteActorException,
            match='Invalid remote actor: can not fetch remote actor.',
        ):

            create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

    @pytest.mark.parametrize(
        'input_description, input_webfinger',
        [
            ('empty dict', {}),
            (
                'missing links',
                {
                    'subject': f'acct:{random_string()}',
                },
            ),
            (
                'empty links',
                {
                    'subject': f'acct:{random_string()}',
                    'links': [],
                },
            ),
            (
                'missing "self" link',
                {
                    'subject': f'acct:{random_string()}',
                    'links': [
                        {
                            'rel': 'http://ostatus.org/schema/1.0/subscribe',
                            'template': (
                                'https://example.com/'
                                'authorize_interaction?uri={uri}'
                            ),
                        }
                    ],
                },
            ),
        ],
    )
    def test_it_returns_error_if_remote_webfinger_does_not_return_links(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
        input_description: str,
        input_webfinger: Dict,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value={},
        ), pytest.raises(
            RemoteActorException,
            match=(
                'Invalid remote actor: invalid data fetched '
                'from webfinger endpoint.'
            ),
        ):
            create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

    def test_it_returns_error_if_fetching_remote_user_returns_error(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            side_effect=ActorNotFoundException(),
        ), pytest.raises(
            RemoteActorException,
            match='Invalid remote actor: can not fetch remote actor.',
        ):

            create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

    def test_it_returns_error_if_preferred_username_is_missing_in_remote_actor_object(  # noqa
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        remote_user_object = random_actor.get_remote_user_object()
        del remote_user_object['preferredUsername']
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=remote_user_object,
        ), pytest.raises(
            RemoteActorException,
            match='Invalid remote actor: invalid remote actor object.',
        ):

            create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

    def test_it_returns_error_if_keys_are_missing_in_remote_actor_object(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value={
                'preferredUsername': random_actor.preferred_username,
            },
        ), pytest.raises(
            RemoteActorException,
            match='Invalid remote actor: invalid remote actor object.',
        ):

            create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

    def test_it_creates_remote_actor_if_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        random_actor.domain = f'https://{remote_domain.name}'
        random_actor.manually_approves_followers = False
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):

            user = create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

        assert user.username == random_actor.name
        assert (
            user.manually_approves_followers
            == random_actor.manually_approves_followers
        )

    def test_it_creates_remote_actor_when_actor_and_domain_dont_exist(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):
            user = create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

        assert user.username == random_actor.name

    def test_it_calls_store_or_delete_user_picture(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
    ) -> None:
        remote_actor_object = random_actor.get_remote_user_object()
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=remote_actor_object,
        ), patch(
            'fittrackee.federation.utils_user.store_or_delete_user_picture'
        ) as store_or_delete_mock:
            user = create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

        store_or_delete_mock.assert_called_with(remote_actor_object, user)

    def test_it_calls_update_remote_actor_stats(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
    ) -> None:
        remote_actor_object = random_actor.get_remote_user_object()
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=remote_actor_object,
        ), patch(
            'fittrackee.federation.utils_user.store_or_delete_user_picture'
        ), patch(
            'fittrackee.federation.utils_user.update_remote_actor_stats'
        ) as update_remote_actor_stats_mock:
            user = create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

        update_remote_actor_stats_mock.assert_called_with(user.actor)

    def test_it_returns_updated_remote_actor_if_remote_actor_exists(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        remote_user_object = remote_user.actor.serialize()
        updated_name = random_string()
        remote_user_object['name'] = updated_name
        remote_user_object['manuallyApprovesFollowers'] = False
        last_fetched = remote_user.actor.last_fetch_date
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value={
                'subject': f'acct:{remote_user.actor.fullname}',
                'links': [
                    {
                        'rel': 'self',
                        'type': 'application/activity+json',
                        'href': remote_user.actor.activitypub_id,
                    }
                ],
            },
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=remote_user_object,
        ):
            create_remote_user(
                remote_user.actor.preferred_username,
                remote_user.actor.domain.name,
            )

        updated_actor = Actor.query.filter_by(id=remote_user.actor.id).first()
        assert updated_actor.name == updated_name
        assert updated_actor.last_fetch_date != last_fetched
        assert updated_actor.user.manually_approves_followers is False

    def test_it_creates_additional_remote_actor(
        self,
        app_with_federation: Flask,
        remote_user: User,
        random_actor: RandomActor,
    ) -> None:
        """
        check constrains on User model
        """
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):
            user = create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

            assert user.username == random_actor.name


class TestGetUserFromUsername:
    def test_it_raises_exception_if_no_user(
        self, app_with_federation: Flask
    ) -> None:
        with pytest.raises(UserNotFoundException):
            get_user_from_username(random_string())

    def test_it_raises_exception_if_only_remote_user_exists_when_usernme_provided(  # noqa
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        with pytest.raises(UserNotFoundException):
            get_user_from_username(remote_user.username)

    def test_it_raises_exception_if_no_local_user_and_with_creation(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        with pytest.raises(UserNotFoundException):
            get_user_from_username(random_string(), with_creation=True)

    def test_it_returns_local_user(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        assert get_user_from_username(user_1.username) == user_1

    def test_it_returns_remote_user(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        assert (
            get_user_from_username(remote_user.actor.fullname) == remote_user
        )

    def test_it_creates_and_returns_remote_user_if_not_existing_and_with_creation(  # noqa
        self, app_with_federation: Flask, random_actor: RandomActor
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):
            user = get_user_from_username(
                random_actor.fullname, with_creation=True
            )

        assert user.username == random_actor.name

    def test_it_creates_remote_user_when_regsitreation_is_disabled(  # noqa
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        app_with_federation.config['is_registration_enabled'] = False
        with patch(
            'fittrackee.federation.utils_user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):
            user = get_user_from_username(
                random_actor.fullname, with_creation=True
            )

        assert user.username == random_actor.name


class TestStoreOrDeleteUserPicture:
    @pytest.mark.parametrize(
        'input_description, input_icon',
        [
            (
                'type is not an image',
                {
                    'type': random_string(),
                    'mediaType': 'image/jpeg',
                    'url': 'https://example/file.jpg',
                },
            ),
            (
                'mediatype is not supported',
                {
                    'type': 'Image',
                    'mediaType': random_string(),
                    'url': f'https://example/file.{random_string()}',
                },
            ),
        ],
    )
    def test_it_does_not_store_picture_if_icon_is_not_supported(
        self,
        app_with_federation: Flask,
        remote_user: User,
        input_description: str,
        input_icon: Dict,
    ) -> None:
        with patch('builtins.open') as open_mock:

            store_or_delete_user_picture(
                remote_actor_object={
                    'icon': input_icon,
                },
                user=remote_user,
            )

        assert remote_user.picture is None
        open_mock.assert_not_called()

    def test_it_does_not_raise_error_if_it_can_not_fetch_image(
        self,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        with patch(
            'requests.get', return_value=generate_response(status_code=404)
        ), patch('builtins.open') as open_mock:

            store_or_delete_user_picture(
                remote_actor_object={
                    'icon': {
                        'type': 'Image',
                        'mediaType': 'image/jpeg',
                        'url': 'https://example.com/916cac70b7c694a4.jpg',
                    },
                },
                user=remote_user,
            )

        assert remote_user.picture is None
        open_mock.assert_not_called()

    def test_it_stores_user_picture(
        self,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        expected_relative_picture_path = os.path.join(
            'pictures', str(remote_user.id), f'{remote_user.username}.jpg'
        )
        expected_absolute_picture_path = os.path.join(
            app_with_federation.config['UPLOAD_FOLDER'],
            expected_relative_picture_path,
        )
        with patch(
            'requests.get', return_value=generate_response(status_code=200)
        ), patch('builtins.open') as open_mock:

            store_or_delete_user_picture(
                remote_actor_object={
                    'icon': {
                        'type': 'Image',
                        'mediaType': 'image/jpeg',
                        'url': f'https://example.com/{random_string()}.jpg',
                    },
                },
                user=remote_user,
            )

        assert remote_user.picture == expected_relative_picture_path
        open_mock.assert_called_once_with(expected_absolute_picture_path, 'wb')

    def test_it_updates_user_picture(
        self,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        remote_user.picture = random_string()
        expected_relative_picture_path = os.path.join(
            'pictures', str(remote_user.id), f'{remote_user.username}.jpg'
        )
        expected_absolute_picture_path = os.path.join(
            app_with_federation.config['UPLOAD_FOLDER'],
            expected_relative_picture_path,
        )
        with patch(
            'requests.get', return_value=generate_response(status_code=200)
        ), patch('builtins.open') as open_mock:

            store_or_delete_user_picture(
                remote_actor_object={
                    'icon': {
                        'type': 'Image',
                        'mediaType': 'image/jpeg',
                        'url': f'https://example.com/{random_string()}.jpg',
                    },
                },
                user=remote_user,
            )

        assert remote_user.picture == expected_relative_picture_path
        open_mock.assert_called_once_with(expected_absolute_picture_path, 'wb')

    def test_it_deletes_user_image_if_no_image_in_remote_actor_object(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        user_picture_path = random_string()
        remote_user.picture = user_picture_path
        with patch('os.path.isfile', return_value=True), patch(
            'os.remove'
        ) as os_remove_mock:

            store_or_delete_user_picture(
                remote_actor_object={}, user=remote_user
            )

        assert remote_user.picture is None
        os_remove_mock.assert_called_with(
            get_absolute_file_path(user_picture_path)
        )


class TestUpdateRemoteActorStats:
    def test_it_does_not_raise_error_if_actor_url_is_not_reachable(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        with patch(
            'requests.get', return_value=generate_response(status_code=400)
        ):

            update_remote_actor_stats(remote_user.actor)

        assert remote_user.actor.stats.items == 0

    def test_it_does_not_fetch_actor_urls_if_user_is_local(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        with patch('requests.get') as get_mock:

            update_remote_actor_stats(user_1.actor)

        get_mock.assert_not_called()

    def test_it_updates_followers_count(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        expected_followers_count = 10
        response_content = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': remote_user.actor.followers_url,
            'type': 'OrderedCollection',
            'totalItems': expected_followers_count,
            'first': f'{remote_user.actor.followers_url}?page=1',
        }
        with patch(
            'requests.get',
            return_value=generate_response(content=response_content),
        ):

            update_remote_actor_stats(remote_user.actor)

        assert remote_user.actor.stats.followers == expected_followers_count

    def test_it_updates_following_count(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        expected_following_count = 33
        response_content = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': remote_user.actor.following_url,
            'type': 'OrderedCollection',
            'totalItems': expected_following_count,
            'first': f'{remote_user.actor.following_url}?page=1',
        }
        with patch(
            'requests.get',
            return_value=generate_response(content=response_content),
        ):

            update_remote_actor_stats(remote_user.actor)

        assert remote_user.actor.stats.following == expected_following_count

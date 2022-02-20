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
)
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User

from ...utils import RandomActor, random_string


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
            'fittrackee.federation.utils_user.fetch_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
            return_value=random_actor.get_remote_user_object(),
        ):
            user = create_remote_user(
                random_actor.preferred_username, random_actor.domain
            )

        assert user.username == random_actor.name

    def test_it_returns_updated_remote_actor_if_remote_actor_exists(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        remote_user_object = remote_user.actor.serialize()
        updated_name = random_string()
        remote_user_object['name'] = updated_name
        remote_user_object['manuallyApprovesFollowers'] = False
        last_fetched = remote_user.actor.last_fetch_date
        with patch(
            'fittrackee.federation.utils_user.fetch_remote_actor',
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
            'fittrackee.federation.utils_user.get_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
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
            'fittrackee.federation.utils_user.fetch_remote_actor',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils_user.get_remote_actor',
            return_value=random_actor.get_remote_user_object(),
        ):
            user = get_user_from_username(
                random_actor.fullname, with_creation=True
            )

        assert user.username == random_actor.name

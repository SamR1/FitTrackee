from typing import Union
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
    get_username_and_domain,
)
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
        print(input_user_account)
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
    @pytest.mark.parametrize(
        'input_description, input_actor_url',
        [('none', None), ('empty string', '')],
    )
    def test_it_returns_error_if_remote_actor_url_is_invalid(
        self, input_description: str, input_actor_url: Union[str, None]
    ) -> None:
        with pytest.raises(
            RemoteActorException,
            match='Invalid remote actor: invalid remote actor url.',
        ):
            create_remote_user(input_actor_url)

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
            create_remote_user(f'{app_with_federation.config["UI_URL"]}')

    def test_it_returns_error_if_preferred_username_is_missing_in_remote_actor_object(  # noqa
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        random_actor.domain = f'https://{remote_domain.name}'
        remote_user_object = random_actor.get_remote_user_object()
        del remote_user_object['preferredUsername']
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object
            with pytest.raises(
                RemoteActorException,
                match='Invalid remote actor: invalid remote actor object.',
            ):
                create_remote_user(random_actor.activitypub_id)

    def test_it_returns_error_if_keys_are_missing_in_remote_actor_object(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = {
                'preferredUsername': random_actor.preferred_username,
            }
            with pytest.raises(
                RemoteActorException,
                match='Invalid remote actor: invalid remote actor object.',
            ):
                create_remote_user(random_actor.activitypub_id)

    def test_it_returns_error_if_fetching_remote_user_returns_error(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.side_effect = ActorNotFoundException()
            with pytest.raises(
                RemoteActorException,
                match='Invalid remote actor: can not fetch remote actor.',
            ):
                create_remote_user(random_actor.activitypub_id)

    def test_it_creates_remote_actor_if_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        remote_domain: Domain,
        random_actor: RandomActor,
    ) -> None:
        random_actor.domain = f'https://{remote_domain.name}'
        random_actor.manually_approves_followers = False
        remote_user_object = random_actor.get_remote_user_object()
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object

            actor = create_remote_user(random_actor.activitypub_id)

            expected_actor = Actor.query.filter_by(
                activitypub_id=random_actor.activitypub_id
            ).first()
            assert actor == expected_actor
            assert actor.user.username == random_actor.name
            assert (
                actor.user.manually_approves_followers
                == random_actor.manually_approves_followers
            )

    def test_it_creates_remote_actor_if_actor_and_domain_dont_exist(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
    ) -> None:
        remote_user_object = random_actor.get_remote_user_object()
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object

            actor = create_remote_user(random_actor.activitypub_id)

            expected_actor = Actor.query.filter_by(
                activitypub_id=random_actor.activitypub_id
            ).first()
            assert actor == expected_actor

    def test_it_returns_updated_remote_actor_if_remote_actor_exists(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        remote_actor = remote_user.actor
        remote_user_object = remote_actor.serialize()
        updated_name = random_string()
        remote_user_object['name'] = updated_name
        remote_user_object['manuallyApprovesFollowers'] = False
        last_fetched = remote_actor.last_fetch_date
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = remote_user_object

            create_remote_user(remote_actor.activitypub_id)

            updated_actor = Actor.query.filter_by(id=remote_actor.id).first()
            assert updated_actor.name == updated_name
            assert updated_actor.last_fetch_date != last_fetched
            assert updated_actor.user.manually_approves_followers is False

    def test_it_creates_several_remote_actors(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
        random_actor_2: RandomActor,
    ) -> None:
        """
        check constrains on User model (especially empty password and email)
        """
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            remote_user_object = random_actor.get_remote_user_object()
            get_remote_user_mock.return_value = remote_user_object
            actor = create_remote_user(random_actor.activitypub_id)

            assert actor.activitypub_id == random_actor.activitypub_id

            remote_user_object = random_actor_2.get_remote_user_object()
            get_remote_user_mock.return_value = remote_user_object
            actor = create_remote_user(random_actor_2.activitypub_id)

            assert actor.activitypub_id == random_actor_2.activitypub_id

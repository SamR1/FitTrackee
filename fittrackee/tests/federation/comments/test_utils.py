from unittest.mock import Mock, patch

from flask import Flask

from fittrackee.comments.utils import handle_mentions
from fittrackee.federation.exceptions import RemoteActorException
from fittrackee.federation.models import Domain
from fittrackee.tests.utils import RandomActor, random_string
from fittrackee.users.models import User


@patch('fittrackee.federation.utils.user.update_remote_user')
class TestGetMentionedUsers:
    def test_it_does_not_raise_exception_when_fetching_actor_raises_exception(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        remote_domain: Domain,
    ) -> None:
        text = f"@foo@{remote_domain.name} {random_string()}"

        with patch(
            "fittrackee.federation.utils.user."
            "create_remote_user_from_username",
            side_effect=RemoteActorException(),
        ):
            _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": set(), "remote": set()}

    def test_it_does_not_return_remote_user_when_mentioned_by_username(
        self, update_mock: Mock, app_with_federation: Flask, remote_user: User
    ) -> None:
        text = f"@{remote_user.username} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": set(), "remote": set()}

    def test_it_returns_remote_user(
        self, update_mock: Mock, app_with_federation: Flask, remote_user: User
    ) -> None:
        text = f"@{remote_user.fullname} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": set(), "remote": {remote_user}}

    def test_it_creates_remote_user(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        random_actor: RandomActor,
    ) -> None:
        text = f"@{random_actor.fullname} {random_string()}"

        with (
            patch(
                'fittrackee.federation.utils.user.fetch_account_from_webfinger',
                return_value=random_actor.get_webfinger(),
            ),
            patch(
                'fittrackee.federation.utils.user.get_remote_actor_url',
                return_value=random_actor.get_remote_user_object(),
            ),
        ):
            _, mentioned_users = handle_mentions(text)

        remote_user = User.query.filter_by(username=random_actor.name).one()
        assert mentioned_users == {"local": set(), "remote": {remote_user}}

    def test_it_returns_text_with_link_when_remote_user_found(
        self, update_mock: Mock, app_with_federation: Flask, remote_user: User
    ) -> None:
        text = f"@{remote_user.fullname} {random_string()}"

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text.replace(
            f"@{remote_user.fullname}",
            f'<a href="{remote_user.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@<span>{remote_user.fullname}</span>'
            f'</a>',
        )

    def test_it_returns_text_when_multiple_users(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        local_mention = f"@{user_1.username}"
        remote_mention = f"@{remote_user.fullname}"
        text = f"{local_mention} {remote_mention} {random_string()}"

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text.replace(
            local_mention,
            f'<a href="{user_1.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@<span>{user_1.username}</span></a>',
        ).replace(
            remote_mention,
            f'<a href="{remote_user.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@<span>{remote_user.fullname}</span>'
            f'</a>',
        )

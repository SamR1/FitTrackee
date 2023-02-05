from flask import Flask

from fittrackee.comments.utils import handle_mentions
from fittrackee.tests.utils import random_domain, random_string
from fittrackee.users.models import User


class TestHandleMentions:
    def test_it_does_not_linkify_user_if_not_user_found(
        self, app_with_federation: Flask
    ) -> None:
        text = f"@{random_string()}@{random_domain()} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == text
        assert mentioned_actors == set()

    def test_it_linkifies_user_when_remote_user_found(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        text = f"@{remote_user.actor.fullname} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == (
            f'<a href="{remote_user.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{remote_user.actor.fullname}'
            '</a> nice!'
        )
        assert mentioned_actors == {remote_user.actor}

    def test_it_linkifies_multiple_users(
        self, app_with_federation: Flask, user_1: User, remote_user: User
    ) -> None:
        text = f"@{user_1.actor.fullname} @{remote_user.actor.fullname} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == (
            f'<a href="{user_1.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.username}</a> '
            f'<a href="{remote_user.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{remote_user.actor.fullname}'
            '</a> nice!'
        )
        assert mentioned_actors == {user_1.actor, remote_user.actor}

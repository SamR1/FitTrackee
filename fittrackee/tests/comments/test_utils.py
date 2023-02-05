from flask import Flask

from fittrackee.comments.utils import handle_mentions
from fittrackee.tests.utils import random_string
from fittrackee.users.models import User


class TestHandleMentions:
    def test_it_does_not_linkify_user_if_not_user_found(
        self, app: Flask
    ) -> None:
        text = f"@{random_string()} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == text
        assert mentioned_actors == set()

    def test_it_linkifies_user_when_local_user_found(
        self, app: Flask, user_1: User
    ) -> None:
        text = f"@{user_1.username} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == (
            f'<a href="{user_1.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.username}</a> nice!'
        )
        assert mentioned_actors == {user_1.actor}

    def test_it_linkifies_user_when_local_user_found_with_domain(
        self, app: Flask, user_1: User
    ) -> None:
        text = f"@{user_1.actor.fullname} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == (
            f'<a href="{user_1.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.username}</a> nice!'
        )
        assert mentioned_actors == {user_1.actor}

    def test_it_linkifies_multiple_users(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        text = f"@{user_1.username} @{user_2.username} nice!"

        converted_text, mentioned_actors = handle_mentions(text)

        assert converted_text == (
            f'<a href="{user_1.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{user_1.username}</a> '
            f'<a href="{user_2.actor.profile_url}" target="_blank" '
            f'rel="noopener noreferrer">@{user_2.username}</a> nice!'
        )
        assert mentioned_actors == {user_1.actor, user_2.actor}

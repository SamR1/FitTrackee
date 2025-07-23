from flask import Flask

from fittrackee.comments.utils import handle_mentions
from fittrackee.tests.utils import random_string
from fittrackee.users.models import User


class TestGetMentionedUsers:
    def test_it_returns_empty_dict_when_no_mentions(self, app: Flask) -> None:
        text = random_string()

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": set(), "remote": set()}

    def test_it_returns_unchanged_text_when_no_mentions(
        self, app: Flask
    ) -> None:
        text = " ".join([random_string()] * 5)

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text

    def test_it_returns_empty_dict_when_user_not_found_by_username(
        self, app: Flask
    ) -> None:
        text = f"@{random_string()} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": set(), "remote": set()}

    def test_it_returns_unchanged_text_when_user_not_found_by_username(
        self, app: Flask
    ) -> None:
        text = f"@{random_string()} {random_string()}"

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text

    def test_it_returns_empty_dict_when_user_not_found_by_fullname(
        self, app: Flask
    ) -> None:
        text = f"@{random_string()}@{random_string()} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": set(), "remote": set()}

    def test_it_returns_user_when_mentioned_by_username(
        self, app: Flask, user_1: User
    ) -> None:
        text = f"@{user_1.username} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": {user_1}, "remote": set()}

    def test_it_returns_text_with_link_when_user_found_by_username(
        self, app: Flask, user_1: User
    ) -> None:
        text = f"@{user_1.username} {random_string()}"

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text.replace(
            f"@{user_1.username}",
            f'<a href="{user_1.get_user_url()}" target="_blank" '
            f'rel="noopener noreferrer">@<span>{user_1.username}</span></a>',
        )

    def test_it_returns_user_when_mentioned_by_actor_fullname(
        self, app: Flask, user_1: User
    ) -> None:
        text = f"@{user_1.fullname} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": {user_1}, "remote": set()}

    def test_it_returns_text_with_link_when_user_found_by_actor_fullname(
        self, app: Flask, user_1: User
    ) -> None:
        text = f"@{user_1.fullname} {random_string()}"

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text.replace(
            f"@{user_1.fullname}",
            f'<a href="{user_1.get_user_url()}" target="_blank" '
            f'rel="noopener noreferrer">@<span>{user_1.fullname}</span></a>',
        )

    def test_it_returns_deduplicated_user_when_mentioned_twice(
        self, app: Flask, user_1: User
    ) -> None:
        mention = f"@{user_1.username} " * 2
        text = f"{mention} {random_string()}"

        _, mentioned_users = handle_mentions(text)

        assert mentioned_users == {"local": {user_1}, "remote": set()}

    def test_it_returns_text_unchanged_when_mentioned_user_is_in_URL(
        self, app: Flask, user_1: User
    ) -> None:
        text = (
            f"{random_string()} "
            f"http://social.example.com/@{user_1.username}/{random_string()} "
            f"{random_string()}"
        )

        linkified_text, _ = handle_mentions(text)

        assert linkified_text == text

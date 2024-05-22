import secrets
from unittest.mock import patch

from click.testing import CliRunner
from flask import Flask

from fittrackee.cli import users_cli
from fittrackee.users.models import User

from ..utils import random_email, random_string


class TestCliUserCreate:
    def test_it_displays_error_when_user_exists_with_same_username(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            [
                "create",
                user_1.username,
                "--email",
                random_email(),
                "--password",
                random_string(),
            ],
        )

        assert (
            result.output
            == 'Error(s) occurred:\nsorry, that username is already taken\n'
        )

    def test_it_displays_error_when_user_exists_with_same_email(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            [
                "create",
                random_string(),
                "--email",
                user_1.email,
                "--password",
                random_string(),
            ],
        )

        assert result.output == (
            'Error(s) occurred:\n'
            'This user already exists. No action done.\n'
        )

    def test_it_displays_success_message_when_user_is_created(
        self,
        app: Flask,
    ) -> None:
        username = random_string()
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            [
                "create",
                username,
                "--email",
                random_email(),
                "--password",
                random_string(),
            ],
        )

        assert f"User '{username}' created.\n" in result.output

    def test_it_displays_password_when_password_is_not_provided(
        self,
        app: Flask,
    ) -> None:
        username = random_string()
        password = random_string()
        runner = CliRunner()

        with patch.object(secrets, 'token_urlsafe', return_value=password):
            result = runner.invoke(
                users_cli,
                ["create", username, "--email", random_email()],
            )

        assert f"The user password is: {password}\n" in result.output

    def test_it_creates_user_with_default_language(
        self, app: Flask, user_1: User
    ) -> None:
        username = random_string()
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["create", username, "--email", random_email()],
        )

        user = User.query.filter_by(username=username).first()
        assert user.language == "en"
        assert (
            'The user preference for interface language is: en'
            in result.output
        )

    def test_it_creates_user_with_provided_language(
        self, app: Flask, user_1: User
    ) -> None:
        username = random_string()
        language = "fr"
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            [
                "create",
                username,
                "--email",
                random_email(),
                "--lang",
                language,
            ],
        )

        user = User.query.filter_by(username=username).first()
        assert user.language == language
        assert (
            f'The user preference for interface language is: {language}'
            not in result.output
        )

    def test_it_creates_user_with_default_language_when_not_supported(
        self, app: Flask, user_1: User
    ) -> None:
        username = random_string()
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            [
                "create",
                username,
                "--email",
                random_email(),
                "--lang",
                "invalid",
            ],
        )

        user = User.query.filter_by(username=username).first()
        assert user.language == "en"
        assert (
            'The user preference for interface language is: en'
            in result.output
        )


class TestCliUserUpdate:
    def test_it_displays_error_when_user_does_not_exist(
        self, app: Flask
    ) -> None:
        username = random_string()
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", username],
        )

        assert result.output == (
            f"User '{username}' not found.\n"
            f"Check the provided user name (case sensitive).\n"
        )

    def test_it_displays_no_updates_when_no_option_provided(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", user_1.username],
        )

        assert result.output == 'No updates.\n'

    def test_it_displays_error_updated_when_user_not_found(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", user_1.username.upper(), '--set-admin', "true"],
        )

        assert result.output == (
            f"User '{user_1.username.upper()}' not found.\n"
            f"Check the provided user name (case sensitive).\n"
        )

    def test_it_displays_user_updated_when_setting_admin_rights(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", user_1.username, '--set-admin', "true"],
        )

        assert result.output == f"User '{user_1.username}' updated.\n"

    def test_it_displays_user_updated_when_removing_admin_rights(
        self, app: Flask, user_1_admin: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", user_1_admin.username, '--set-admin', "false"],
        )

        assert result.output == f"User '{user_1_admin.username}' updated.\n"

    def test_it_displays_user_updated_when_activating_user(
        self, app: Flask, inactive_user: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", inactive_user.username, '--activate'],
        )

        assert result.output == f"User '{inactive_user.username}' updated.\n"

    def test_it_displays_password_when_resetting_password(
        self, app: Flask, user_1: User
    ) -> None:
        password = random_string()
        runner = CliRunner()

        with patch.object(secrets, 'token_urlsafe', return_value=password):
            result = runner.invoke(
                users_cli,
                ["update", user_1.username, '--reset-password'],
            )

        assert result.output == (
            f"User '{user_1.username}' updated.\n"
            f"The new password is: {password}\n"
        )

    def test_it_displays_user_updated_when_updating_email(
        self, app: Flask, inactive_user: User
    ) -> None:
        new_email = random_email()
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            ["update", inactive_user.username, '--update-email', new_email],
        )

        assert result.output == f"User '{inactive_user.username}' updated.\n"

    def test_it_displays_error_when_email_is_invalid(
        self, app: Flask, inactive_user: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            users_cli,
            [
                "update",
                inactive_user.username,
                '--update-email',
                random_string(),
            ],
        )

        assert (
            result.output
            == "An error occurred: valid email must be provided\n"
        )

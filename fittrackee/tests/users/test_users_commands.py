import secrets
from unittest.mock import patch

from click.testing import CliRunner
from flask import Flask

from fittrackee import bcrypt
from fittrackee.cli import cli
from fittrackee.users.models import User

from ..utils import random_email, random_string


class TestCliUserCreate:
    def test_it_displays_error_when_user_exists_with_same_username(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "users",
                "create",
                user_1.username,
                "--email",
                random_email(),
                "--password",
                random_string(),
            ],
        )

        assert result.exit_code == 0
        assert (
            result.output
            == 'Error(s) occurred:\nsorry, that username is already taken\n'
        )

    def test_it_displays_error_when_user_exists_with_same_email(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "users",
                "create",
                random_string(),
                "--email",
                user_1.email,
                "--password",
                random_string(),
            ],
        )

        assert result.exit_code == 0
        assert result.output == (
            'Error(s) occurred:\n'
            'This user already exists. No action done.\n'
        )

    def test_it_creates_user(
        self,
        app: Flask,
    ) -> None:
        username = random_string()
        email = random_email()
        password = random_string()
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "users",
                "create",
                username,
                "--email",
                email,
                "--password",
                password,
            ],
        )

        assert result.exit_code == 0
        assert f"User '{username}' created.\n" in result.output
        user = User.query.filter_by(username=username).first()
        assert user.is_active is True
        assert user.email == email
        assert bcrypt.check_password_hash(user.password, password)

    def test_it_displays_password_when_password_is_not_provided(
        self,
        app: Flask,
    ) -> None:
        username = random_string()
        email = random_email()
        password = random_string()
        runner = CliRunner()

        with patch.object(secrets, 'token_urlsafe', return_value=password):
            result = runner.invoke(
                cli,
                ["users", "create", username, "--email", email],
            )

        assert result.exit_code == 0
        assert f"The user password is: {password}\n" in result.output
        user = User.query.filter_by(username=username).first()
        assert user.is_active is True
        assert user.email == email
        assert bcrypt.check_password_hash(user.password, password)

    def test_it_creates_user_with_default_language(
        self, app: Flask, user_1: User
    ) -> None:
        username = random_string()
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ["users", "create", username, "--email", random_email()],
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
            cli,
            [
                "users",
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
            cli,
            [
                "users",
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
    def test_it_returns_error_when_missing_user_name(self, app: Flask) -> None:
        runner = CliRunner()

        result = runner.invoke(cli, ['users', 'update'])

        assert result.exit_code == 2
        assert "Error: Missing argument 'USERNAME'." in result.output

    def test_it_display_error_when_user_not_found(self, app: Flask) -> None:
        username = random_string()
        runner = CliRunner()

        result = runner.invoke(cli, ['users', 'update', username])

        assert result.exit_code == 0
        assert f"User '{username}' not found." in result.output

    def test_it_does_not_update_user_when_no_options_provided(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()
        previous_email = user_1.email
        previous_password = user_1.password

        result = runner.invoke(cli, ['users', 'update', user_1.username])

        assert result.exit_code == 0
        assert "No updates." in result.output
        assert user_1.admin is False
        assert user_1.is_active is True
        assert user_1.email == previous_email
        assert user_1.password == previous_password

    def test_it_sets_admin_rights(self, app: Flask, user_1: User) -> None:
        runner = CliRunner()
        previous_email = user_1.email
        previous_password = user_1.password

        with app.app_context():
            result = runner.invoke(
                cli,
                ['users', 'update', user_1.username, '--set-admin', 'true'],
            )

            assert result.exit_code == 0
            assert f"User '{user_1.username}' updated." in result.output
            updated_user = User.query.filter_by(id=user_1.id).first()
            assert updated_user.admin is True
            # unchanged values
            assert updated_user.is_active is True
            assert updated_user.email == previous_email
            assert updated_user.password == previous_password

    def test_it_removes_admin_rights(
        self, app: Flask, user_1_admin: User
    ) -> None:
        runner = CliRunner()
        previous_email = user_1_admin.email
        previous_password = user_1_admin.password

        with app.app_context():
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    user_1_admin.username,
                    '--set-admin',
                    'false',
                ],
            )

            assert result.exit_code == 0
            assert f"User '{user_1_admin.username}' updated." in result.output
            updated_user = User.query.filter_by(id=user_1_admin.id).first()
            assert updated_user.admin is False
            # unchanged values
            assert updated_user.is_active is True
            assert updated_user.email == previous_email
            assert updated_user.password == previous_password

    def test_it_activates_user_when_adding_admin_rights(
        self, app: Flask, inactive_user: User
    ) -> None:
        runner = CliRunner()
        previous_email = inactive_user.email
        previous_password = inactive_user.password

        with app.app_context():
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    inactive_user.username,
                    '--set-admin',
                    'true',
                ],
            )

            assert result.exit_code == 0
            assert f"User '{inactive_user.username}' updated." in result.output
            updated_user = User.query.filter_by(id=inactive_user.id).first()
            assert updated_user.admin is True
            assert updated_user.is_active is True
            # unchanged values
            assert updated_user.email == previous_email
            assert updated_user.password == previous_password

    def test_it_activates_user(self, app: Flask, inactive_user: User) -> None:
        runner = CliRunner()
        previous_email = inactive_user.email
        previous_password = inactive_user.password

        with app.app_context():
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    inactive_user.username,
                    '--activate',
                ],
            )

            assert result.exit_code == 0
            assert f"User '{inactive_user.username}' updated." in result.output
            updated_user = User.query.filter_by(id=inactive_user.id).first()
            assert updated_user.is_active is True
            # unchanged values
            assert updated_user.admin is False
            assert updated_user.email == previous_email
            assert updated_user.password == previous_password

    def test_it_resets_password(self, app: Flask, user_1: User) -> None:
        runner = CliRunner()
        previous_email = user_1.email
        new_password = random_string()

        with app.app_context(), patch.object(
            secrets, 'token_urlsafe', return_value=new_password
        ):
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    user_1.username,
                    '--reset-password',
                ],
            )

            assert result.exit_code == 0
            assert f"User '{user_1.username}' updated." in result.output
            assert f"The new password is: {new_password}" in result.output
            updated_user = User.query.filter_by(id=user_1.id).first()
            assert bcrypt.check_password_hash(
                updated_user.password, new_password
            )
            # unchanged values
            assert updated_user.admin is False
            assert updated_user.is_active is True
            assert updated_user.email == previous_email

    def test_it_updates_email(self, app: Flask, user_1: User) -> None:
        runner = CliRunner()
        previous_password = user_1.password
        new_email = random_email()

        with app.app_context():
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    user_1.username,
                    '--update-email',
                    new_email,
                ],
            )

            assert result.exit_code == 0
            assert f"User '{user_1.username}' updated." in result.output
            updated_user = User.query.filter_by(id=user_1.id).first()
            assert updated_user.email == new_email
            # unchanged values
            assert updated_user.admin is False
            assert updated_user.is_active is True
            assert updated_user.password == previous_password

    def test_it_displays_error_when_email_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        runner = CliRunner()

        with app.app_context():
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    user_1.username,
                    '--update-email',
                    random_string(),
                ],
            )

            assert result.exit_code == 0
            assert (
                result.output
                == "An error occurred: valid email must be provided\n"
            )

    def test_it_updates_user(self, app: Flask, inactive_user: User) -> None:
        runner = CliRunner()
        previous_password = inactive_user.password
        new_email = random_email()

        with app.app_context():
            result = runner.invoke(
                cli,
                [
                    'users',
                    'update',
                    inactive_user.username,
                    '--update-email',
                    new_email,
                    '--set-admin',
                    'true',
                ],
            )

            assert result.exit_code == 0
            assert f"User '{inactive_user.username}' updated." in result.output
            updated_user = User.query.filter_by(id=inactive_user.id).first()
            assert updated_user.email == new_email
            assert updated_user.admin is True
            assert updated_user.is_active is True
            assert updated_user.password == previous_password

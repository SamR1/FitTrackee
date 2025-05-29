import logging
import sys
from typing import Optional

import click
from humanize import naturalsize

from fittrackee import db
from fittrackee.cli.app import app
from fittrackee.languages import SUPPORTED_LANGUAGES
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.export_data import (
    clean_user_data_export,
    generate_user_data_archives,
    process_queued_data_export,
)
from fittrackee.users.roles import UserRole
from fittrackee.users.timezones import get_timezone
from fittrackee.users.users_service import UserManagerService
from fittrackee.users.utils.language import get_language
from fittrackee.users.utils.tokens import clean_blacklisted_tokens

handler = logging.StreamHandler()
logger = logging.getLogger("fittrackee_users_cli")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@click.group(name="users")
def users_cli() -> None:
    """Manage users."""
    pass


@users_cli.command("create")
@click.argument("username")
@click.option("--email", type=str, required=True, help="User email.")
@click.option(
    "--password",
    type=str,
    help="User password. If not provided, a random password is generated.",
)
@click.option(
    "--lang",
    type=str,
    help=(
        "User preference for interface language (two-letter code, ISO 639-1)."
        " If not provided or not supported, it falls back to English ('en')."
        f" Supported languages: {', '.join(SUPPORTED_LANGUAGES)}."
    ),
)
@click.option(
    "--tz",
    type=str,
    help=(
        "User preference for timezone. If not provided or not supported, "
        "it falls back to 'Europe/Paris'."
    ),
)
@click.option(
    "--role", type=click.Choice(UserRole.db_choices()), help="Set user role."
)
def create_user(
    username: str,
    email: str,
    password: Optional[str],
    lang: Optional[str],
    role: Optional[str],
    tz: Optional[str],
) -> None:
    """Create an active user account."""
    with app.app_context():
        try:
            user_manager_service = UserManagerService(username)
            user, user_password = user_manager_service.create_user(
                email=email, password=password, check_email=True, role=role
            )
            if user:
                db.session.add(user)
                user_language = get_language(lang)
                user.language = user_language
                user_timezone = get_timezone(tz)
                user.timezone = user_timezone
                db.session.commit()
                user_manager_service.update(activate=True)
                click.echo(f"User '{username}' created.")
                if lang != user_language:
                    click.echo(
                        "The user preference for interface language "
                        f"is: {user_language}"
                    )
                if tz != user_timezone:
                    click.echo(
                        f"The user preference for timezone is: {user_timezone}"
                    )
                if not password:
                    click.echo(f"The user password is: {user_password}")
        except Exception as e:
            click.echo(f"Error(s) occurred:\n{e}", err=True)


@users_cli.command("update")
@click.argument("username")
@click.option(
    "--set-admin",
    type=bool,
    help="[DEPRECATED] Add/remove admin rights (when adding admin rights, "
    "it also activates user account if not active).",
)
@click.option(
    "--set-role",
    type=click.Choice(UserRole.db_choices()),
    help="Set user role (when setting 'moderator', 'admin' and 'owner' "
    "role, it also activates user account if not active).",
)
@click.option("--activate", is_flag=True, help="Activate user account.")
@click.option(
    "--reset-password",
    is_flag=True,
    help="Reset user password (a new password will be displayed).",
)
@click.option("--update-email", type=str, help="Update user email.")
def manage_user(
    username: str,
    set_admin: Optional[bool],
    set_role: Optional[str],
    activate: bool,
    reset_password: bool,
    update_email: Optional[str],
) -> None:
    """Manage given user account."""
    with app.app_context():
        role = None
        if set_admin is not None:
            click.echo(
                "WARNING: --set-admin is deprecated. "
                "Please use --set-role option instead."
            )
            role = "admin" if set_admin else "user"
        if set_admin is not None and set_role is not None:
            raise click.ClickException(
                "--set-admin and --set-role can not be used together.",
            )

        if set_role:
            role = set_role

        try:
            user_manager_service = UserManagerService(username)
            _, is_user_updated, password, _ = user_manager_service.update(
                role=role,
                with_confirmation=False,
                activate=activate if activate else None,
                reset_password=reset_password,
                new_email=update_email,
            )
            if is_user_updated:
                click.echo(f"User '{username}' updated.")
                if password:
                    click.echo(f"The new password is: {password}")
            else:
                click.echo("No updates.")
        except UserNotFoundException:
            click.echo(
                f"User '{username}' not found.\n"
                "Check the provided user name (case sensitive).",
                err=True,
            )
        except Exception as e:
            click.echo(f"An error occurred: {e}", err=True)


@users_cli.command("clean_tokens")
@click.option("--days", type=int, required=True, help="Number of days.")
def clean(
    days: int,
) -> None:
    """
    Clean blacklisted tokens expired for more than provided number of days.
    """
    with app.app_context():
        deleted_rows = clean_blacklisted_tokens(days)
        logger.info(f"Blacklisted tokens deleted: {deleted_rows}.")


@users_cli.command("clean_archives")
@click.option("--days", type=int, required=True, help="Number of days.")
def clean_export_archives(
    days: int,
) -> None:
    """
    Clean user export archives created for more than provided number of days.
    """
    with app.app_context():
        counts = clean_user_data_export(days)
        logger.info(
            f"Deleted data export requests: {counts['deleted_requests']}."
        )
        logger.info(
            f"Deleted data export archives: {counts['deleted_archives']}."
        )
        logger.info(f"Freed space: {naturalsize(counts['freed_space'])}.")


@users_cli.command("export_archives")
@click.option(
    "--max",
    "max_reports",
    type=int,
    required=True,
    help="Maximum number of export requests to process.",
)
def export_archives(max_reports: int) -> None:
    """
    Export user data in zip archive if queued requests exist.

    To use in case redis is not set.
    """
    with app.app_context():
        count = generate_user_data_archives(max_reports)
        logger.info(f"Generated data export archives: {count}.")


@users_cli.command("export_archive")
@click.option(
    "--id",
    "task_id",
    type=str,
    required=True,
    help="Id of task to process",
)
def export_archive(task_id: str) -> None:
    """
    Process queued user data export.

    To use in case redis is not set.
    """
    with app.app_context():
        try:
            process_queued_data_export(task_id)
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)
        logger.info("\nDone.")

import logging
from typing import Optional

import click
from humanize import naturalsize

from fittrackee import db
from fittrackee.cli.app import app
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.export_data import (
    clean_user_data_export,
    generate_user_data_archives,
)
from fittrackee.users.utils.admin import UserManagerService
from fittrackee.users.utils.token import clean_blacklisted_tokens

handler = logging.StreamHandler()
logger = logging.getLogger('fittrackee_users_cli')
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@click.group(name='users')
def users_cli() -> None:
    """Manage users."""
    pass


@users_cli.command('create')
@click.argument('username')
@click.option('--email', type=str, required=True, help='User email.')
@click.option(
    '--password',
    type=str,
    help='User password. If not provided, a random password is generated.',
)
def create_user(username: str, email: str, password: Optional[str]) -> None:
    """Create an active user account."""
    with app.app_context():
        try:
            user_manager_service = UserManagerService(username)
            user, user_password = user_manager_service.create_user(
                email=email, password=password
            )
            db.session.add(user)
            db.session.commit()
            user_manager_service.update(activate=True)
            click.echo(f"User '{username}' created.")
            if not password:
                click.echo(f"The user password is: {user_password}")
        except Exception as e:
            click.echo(f'Error(s) occurred:\n{e}', err=True)


@users_cli.command('update')
@click.argument('username')
@click.option(
    '--set-admin',
    type=bool,
    help='Add/remove admin rights (when adding admin rights, '
    'it also activates user account if not active).',
)
@click.option('--activate', is_flag=True, help='Activate user account.')
@click.option(
    '--reset-password',
    is_flag=True,
    help='Reset user password (a new password will be displayed).',
)
@click.option('--update-email', type=str, help='Update user email.')
def manage_user(
    username: str,
    set_admin: Optional[bool],
    activate: bool,
    reset_password: bool,
    update_email: Optional[str],
) -> None:
    """Manage given user account."""
    with app.app_context():
        try:
            user_manager_service = UserManagerService(username)
            _, is_user_updated, password = user_manager_service.update(
                is_admin=set_admin,
                with_confirmation=False,
                activate=activate,
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
            click.echo(f'An error occurred: {e}', err=True)


@users_cli.command('clean_tokens')
@click.option('--days', type=int, required=True, help='Number of days.')
def clean(
    days: int,
) -> None:
    """
    Clean blacklisted tokens expired for more than provided number of days.
    """
    with app.app_context():
        deleted_rows = clean_blacklisted_tokens(days)
        logger.info(f'Blacklisted tokens deleted: {deleted_rows}.')


@users_cli.command('clean_archives')
@click.option('--days', type=int, required=True, help='Number of days.')
def clean_export_archives(
    days: int,
) -> None:
    """
    Clean user export archives created for more than provided number of days.
    """
    with app.app_context():
        counts = clean_user_data_export(days)
        logger.info(
            f'Deleted data export requests: {counts["deleted_requests"]}.'
        )
        logger.info(
            f'Deleted data export archives: {counts["deleted_archives"]}.'
        )
        logger.info(f'Freed space: {naturalsize(counts["freed_space"])}.')


@users_cli.command('export_archives')
@click.option(
    '--max',
    type=int,
    required=True,
    help='Maximum number of export requests to process.',
)
def export_archives(
    max: int,
) -> None:
    """
    Export user data in zip archive if incomplete requests exist.
    To use in case redis is not set.
    """
    with app.app_context():
        count = generate_user_data_archives(max)
        logger.info(f'Generated data export archives: {count}.')

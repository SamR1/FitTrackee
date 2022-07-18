from typing import Optional

import click

from fittrackee.cli.app import app
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.utils.admin import UserManagerService


@click.group(name='users')
def users_cli() -> None:
    """Manage users."""
    pass


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

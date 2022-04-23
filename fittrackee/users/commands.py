import click

from fittrackee.cli.app import app
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.utils.admin import set_admin_rights


@click.group(name='users')
def users_cli() -> None:
    """Manage users."""
    pass


@users_cli.command('set-admin')
@click.argument('username')
def set_admin(username: str) -> None:
    """Set admin rights for given user"""
    with app.app_context():
        try:
            set_admin_rights(username)
            click.echo(f"User '{username}' updated.")
        except UserNotFoundException:
            click.echo(f"User '{username}' not found.", err=True)

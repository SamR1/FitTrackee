# source for StandaloneApplication class:
# http://docs.gunicorn.org/en/stable/custom.html
import os
from typing import Dict, Optional

import click
import gunicorn.app.base
from flask import Flask
from flask_migrate import upgrade

from fittrackee import create_app
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.utils.admin import UserManagerService

HOST = os.getenv('HOST', '127.0.0.1')
PORT = os.getenv('PORT', '5000')
WORKERS = os.getenv('APP_WORKERS', 1)
BASEDIR = os.path.abspath(os.path.dirname(__file__))
WARNING_MESSAGE = (
    "\nThis command is deprecated, it will be removed in a next version.\n"
    "Please use ftcli instead.\n"
)
app = create_app()


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(
        self, current_app: Flask, options: Optional[Dict] = None
    ) -> None:
        self.options = options or {}
        self.application = current_app
        super().__init__()

    def load_config(self) -> None:
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Flask:
        return self.application


# DEPRECATED COMMANDS
@click.group()
def users_cli() -> None:
    pass


@users_cli.command('set_admin')
@click.argument('username')
def set_admin(username: str) -> None:
    """
    [deprecated] Set admin rights for given user.

    It will be removed in a next version.
    """
    print(WARNING_MESSAGE)
    with app.app_context():
        try:
            user_manager_service = UserManagerService(username)
            user_manager_service.update(
                is_admin=True,
            )
            print(f"User '{username}' updated.")
        except UserNotFoundException:
            print(f"User '{username}' not found.")


def upgrade_db() -> None:
    """
    [deprecated] Apply migrations.

    It will be removed in a next version.
    """
    print(WARNING_MESSAGE)
    with app.app_context():
        upgrade(directory=BASEDIR + '/migrations')


def worker() -> None:
    raise SystemExit(
        "Error: this command is disabled, "
        "it will be removed in a next version.\n"
        "Please use flask-dramatiq CLI instead ('flask worker')."
    )


def main() -> None:
    options = {'bind': f'{HOST}:{PORT}', 'workers': WORKERS}
    StandaloneApplication(app, options).run()


if __name__ == '__main__':
    app.run()

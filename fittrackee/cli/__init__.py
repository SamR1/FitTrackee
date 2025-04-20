import click

from fittrackee.migrations.commands import db_cli
from fittrackee.oauth2.commands import oauth2_cli
from fittrackee.users.commands import users_cli
from fittrackee.workouts.commands import workouts_cli


@click.group()
def cli() -> None:
    """FitTrackee Command Line Interface"""
    pass


cli.add_command(db_cli)
cli.add_command(oauth2_cli)
cli.add_command(users_cli)
cli.add_command(workouts_cli)

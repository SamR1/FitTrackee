import logging

import click

from fittrackee.cli.app import app
from fittrackee.workouts.tasks import process_workouts_archives_upload

handler = logging.StreamHandler()
logger = logging.getLogger("fittrackee_workouts_cli")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@click.group(name="workouts")
def workouts_cli() -> None:
    """Manage workouts."""
    pass


@workouts_cli.command("archive_upload")
@click.option(
    "--max",
    "max_archives",
    type=int,
    required=True,
    help="Maximum number of workouts archive to process.",
)
def workouts_archive_upload(
    max_archives: int,
) -> None:
    """
    Process workouts archive upload if incomplete tasks exist (progress = 0 and
    (not errored).
    To use in case redis is not set.
    """
    with app.app_context():
        count = process_workouts_archives_upload(max_archives)
        logger.info(f"Workouts archives processed: {count}.")

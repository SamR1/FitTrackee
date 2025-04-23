import logging
import sys

import click

from fittrackee.cli.app import app
from fittrackee.workouts.tasks import (
    process_workouts_archive_upload,
    process_workouts_archives_uploads,
)

handler = logging.StreamHandler()
logger = logging.getLogger("fittrackee_workouts_cli")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


@click.group(name="workouts")
def workouts_cli() -> None:
    """Manage workouts."""
    pass


@workouts_cli.command("archive_uploads")
@click.option(
    "--max",
    "max_archives",
    type=int,
    required=True,
    help="Maximum number of workouts archive to process.",
)
@click.option(
    "--verbose",
    "-v",
    "verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output log (default: disabled).",
)
def workouts_archive_uploads(max_archives: int, verbose: bool) -> None:
    """
    Process workouts archive upload if incomplete tasks exist (progress = 0 and
    not aborted/errored).
    To use in case redis is not set.
    """
    with app.app_context():
        if verbose:
            upload_logger = logging.getLogger("fittrackee_workouts_upload")
            upload_logger.setLevel(logging.DEBUG)
            upload_logger.addHandler(handler)
        count = process_workouts_archives_uploads(max_archives, logger)
        logger.info(f"\nWorkouts archives processed: {count}.")


@workouts_cli.command("archive_upload")
@click.option(
    "--id",
    "task_short_id",
    type=str,
    required=True,
    help="Id of task to process",
)
@click.option(
    "--verbose",
    "-v",
    "verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output log (default: disabled).",
)
def process_queued_archive_upload(task_short_id: str, verbose: bool) -> None:
    """
    Process given queued workouts archive upload.

    To use in case redis is not set.
    """
    with app.app_context():
        if verbose:
            upload_logger = logging.getLogger("fittrackee_workouts_upload")
            upload_logger.setLevel(logging.DEBUG)
            upload_logger.addHandler(handler)
        try:
            process_workouts_archive_upload(task_short_id, logger)
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)
        logger.info("\nDone.")

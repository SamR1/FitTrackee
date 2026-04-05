import logging

import click
from humanize import naturalsize

from fittrackee.cli.app import app

from .utils import clean_orphan_media_attachments

logger = logging.getLogger("fittrackee_media_attachments_cli")
logger.setLevel(logging.INFO)


@click.group(name="media_attachments")
def media_attachments_cli() -> None:
    """Manage media attachments."""
    pass


@media_attachments_cli.command("clean_orphans")
@click.option("--days", type=int, required=True, help="Number of days.")
def clean_orphans(days: int) -> None:
    """
    Clean media attachments without workout and created for more than
    provided number of days.
    """
    with app.app_context():
        counts = clean_orphan_media_attachments(days)
        logger.info(
            f"Deleted orphan media attachments: {counts['deleted_media_attachments']}."  # noqa: E501
        )
        logger.info(f"Freed space: {naturalsize(counts['freed_space'])}.")

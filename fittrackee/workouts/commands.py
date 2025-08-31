import logging
import sys
from datetime import datetime
from typing import Optional

import click

from fittrackee.cli.app import app
from fittrackee.users.models import User
from fittrackee.workouts.constants import WORKOUT_ALLOWED_EXTENSIONS
from fittrackee.workouts.models import Sport
from fittrackee.workouts.services.workouts_from_file_refresh_service import (
    WorkoutsFromFileRefreshService,
)
from fittrackee.workouts.tasks import (
    process_workouts_archive_upload,
    process_workouts_archives_uploads,
)
from fittrackee.workouts.utils.workouts import get_workout_datetime

WORKOUT_VALID_EXTENSIONS = ", ".join(WORKOUT_ALLOWED_EXTENSIONS)
handler = logging.StreamHandler()
logger = logging.getLogger("fittrackee_workouts_cli")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def validate_order(
    ctx: click.core.Context, param: click.core.Option, value: Optional[str]
) -> Optional[str]:
    if value and value not in ["asc", "desc"]:
        raise click.BadParameter("order must be 'asc' or 'desc'")
    return value


def validate_extension(
    ctx: click.core.Context, param: click.core.Option, value: Optional[str]
) -> Optional[str]:
    if value and value not in WORKOUT_ALLOWED_EXTENSIONS:
        raise click.BadParameter(
            f"valid extensions are: {WORKOUT_VALID_EXTENSIONS}"
        )
    return value


def validate_sport_id(
    ctx: click.core.Context, param: click.core.Option, value: Optional[int]
) -> Optional[int]:
    with app.app_context():
        if value is not None and not Sport.query.filter_by(id=value).first():
            raise click.BadParameter(f"invalid sport id '{value}'")
    return value


def validate_user(
    ctx: click.core.Context, param: click.core.Option, value: Optional[str]
) -> Optional[str]:
    with app.app_context():
        if (
            value is not None
            and not User.query.filter_by(username=value).first()
        ):
            raise click.BadParameter(f"user '{value}' does not exist")
    return value


def validate_number(
    ctx: click.core.Context, param: click.core.Option, value: Optional[int]
) -> Optional[int]:
    if value is not None and value < 1:
        raise click.BadParameter("value must be greater than 0")

    return value


def validate_date(
    ctx: click.core.Context, param: click.core.Option, value: Optional[str]
) -> Optional["datetime"]:
    if value is not None:
        try:
            date_value, _ = get_workout_datetime(
                workout_date=value,
                user_timezone=None,
                date_str_format="%Y-%m-%d",
            )
            return date_value
        except Exception as e:
            raise click.BadParameter(
                f"'{value}' does not match format '%Y-%m-%d'"
            ) from e
    return value


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
    Process workouts archive uploads if queued tasks exist (progress = 0 and
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


@workouts_cli.command("refresh")
@click.option(
    "--sport-id",
    help="sport id",
    type=int,
    callback=validate_sport_id,
)
@click.option(
    "--from",
    "date_from",
    help="start date (format: %Y-%m-%d)",
    callback=validate_date,
)
@click.option(
    "--to",
    "date_to",
    help="end date (format: %Y-%m-%d)",
    callback=validate_date,
)
@click.option(
    "--per-page",
    help="number of workouts per page (default: 10)",
    type=int,
    callback=validate_number,
    default=10,
)
@click.option(
    "--page",
    help="page number (default: 1)",
    type=int,
    callback=validate_number,
    default=1,
)
@click.option(
    "--order",
    help="workout date order: 'asc' or 'desc' (default: 'asc')",
    type=str,
    default="asc",
    callback=validate_order,
)
@click.option(
    "--user",
    help="username of workouts owner",
    type=str,
    callback=validate_user,
)
@click.option(
    "--extension",
    help=(
        "workout file extension "
        f"(valid values are: {WORKOUT_VALID_EXTENSIONS})"
    ),
    type=str,
    callback=validate_extension,
)
@click.option(
    "--with-weather",
    help=(
        "enable weather data collection if weather provider is set and "
        "workout has no weather data. "
        "WARNING: depending on subscription, the rate limit can be reached, "
        "leading to errors and preventing weather data being collected during "
        "next uploads until the limit is reset (default: disabled)"
    ),
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option(
    "--verbose",
    "-v",
    "verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output log (default: disabled)",
)
def refresh_workouts(
    sport_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    per_page: int = 10,
    page: int = 1,
    order: str = "asc",
    user: Optional[str] = None,
    extension: Optional[str] = None,
    with_weather: bool = False,
    verbose: bool = False,
) -> None:
    """
    Refresh workouts
    """
    with app.app_context():
        if verbose:
            refresh_logger = logging.getLogger("fittrackee_workouts_refresh")
            refresh_logger.setLevel(logging.DEBUG)
            refresh_logger.addHandler(handler)

        try:
            service = WorkoutsFromFileRefreshService(
                sport_id=sport_id,
                date_from=date_from,
                date_to=date_to,
                per_page=per_page,
                page=page,
                order=order,
                user=user,
                extension=extension,
                with_weather=with_weather,
                verbose=verbose,
                logger=logger,
            )
            service.refresh()
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)

        logger.info("\nDone.")

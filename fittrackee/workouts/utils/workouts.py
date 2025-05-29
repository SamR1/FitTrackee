from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import pytz

from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import can_view

from ..exceptions import WorkoutForbiddenException
from ..models import Workout

if TYPE_CHECKING:
    from fittrackee.users.models import User


def get_workout_datetime(
    workout_date: Union["datetime", str],
    user_timezone: Optional[str],
    date_str_format: Optional[str] = None,
    with_user_timezone: bool = False,
) -> Tuple["datetime", Optional["datetime"]]:
    """
    Return datetime in UTC and datetime in user timezone if with_user_timezone
    is True.

    Note: columns in Datetime are still stored without timezone.
    Values must be in the UTC timezone before storing in database.
    """
    workout_date_in_user_tz = None

    # workout w/o gpx
    if isinstance(workout_date, str):
        if not date_str_format:
            date_str_format = "%Y-%m-%d %H:%M:%S"
        workout_date = datetime.strptime(workout_date, date_str_format)  # noqa: DTZ007
        if user_timezone:
            workout_date = pytz.timezone(user_timezone).localize(workout_date)

    if workout_date.tzinfo is None:
        workout_date_in_utc = workout_date.replace(tzinfo=timezone.utc)
        if user_timezone and with_user_timezone:
            workout_date_in_user_tz = workout_date_in_utc.astimezone(
                pytz.timezone(user_timezone)
            )
    else:
        workout_date_in_utc = workout_date.astimezone(pytz.utc)
        if user_timezone and with_user_timezone:
            workout_date_in_user_tz = workout_date.astimezone(
                pytz.timezone(user_timezone)
            )

    return workout_date_in_utc, workout_date_in_user_tz


def get_datetime_from_request_args(
    params: Dict, user: "User"
) -> Tuple[Optional["datetime"], Optional["datetime"]]:
    date_from = None
    date_to = None

    date_from_str = params.get("from")
    if date_from_str:
        date_from, _ = get_workout_datetime(
            workout_date=date_from_str,
            user_timezone=user.timezone,
            date_str_format="%Y-%m-%d",
        )
    date_to_str = params.get("to")
    if date_to_str:
        date_to, _ = get_workout_datetime(
            workout_date=f"{date_to_str} 23:59:59",
            user_timezone=user.timezone,
        )
    return date_from, date_to


def get_average_speed(
    total_workouts: int,
    total_average_speed: float,
    workout_average_speed: float,
) -> float:
    return round(
        (
            (total_average_speed * (total_workouts - 1))
            + float(workout_average_speed)
        )
        / total_workouts,
        2,
    )


def get_ordered_workouts(
    workouts: List["Workout"], limit: int
) -> List["Workout"]:
    return sorted(
        workouts, key=lambda workout: workout.workout_date, reverse=True
    )[:limit]


def get_workout(
    workout_short_id: str,
    auth_user: Optional["User"],
    allow_admin: bool = False,
) -> "Workout":
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter(Workout.uuid == workout_uuid).first()
    if not workout or (
        not can_view(workout, "workout_visibility", auth_user)
        and not (allow_admin and auth_user and auth_user.has_admin_rights)
    ):
        raise WorkoutForbiddenException()
    return workout

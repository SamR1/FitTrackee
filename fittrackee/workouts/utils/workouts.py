from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID

import pytz

from fittrackee.users.models import User
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import (
    VisibilityLevel,
    can_view,
    get_calculated_visibility,
)

from ..constants import WORKOUT_DATE_FORMAT
from ..exceptions import (
    WorkoutForbiddenException,
)
from ..models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Workout,
    WorkoutSegment,
)


def get_workout_datetime(
    workout_date: Union[datetime, str],
    user_timezone: Optional[str],
    date_str_format: Optional[str] = None,
    with_user_timezone: bool = False,
) -> Tuple[datetime, Optional[datetime]]:
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
    params: Dict, user: User
) -> Tuple[Optional[datetime], Optional[datetime]]:
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


def _remove_microseconds(delta: timedelta) -> timedelta:
    return delta - timedelta(microseconds=delta.microseconds)


def update_workout_data(
    workout: Union[Workout, WorkoutSegment], gpx_data: Dict
) -> Union[Workout, WorkoutSegment]:
    """
    Update workout or workout segment with data from gpx file
    """
    workout.pauses = _remove_microseconds(gpx_data["stop_time"])
    workout.moving = _remove_microseconds(gpx_data["moving_time"])
    workout.min_alt = gpx_data["elevation_min"]
    workout.max_alt = gpx_data["elevation_max"]
    workout.descent = gpx_data["downhill"]
    workout.ascent = gpx_data["uphill"]
    workout.max_speed = gpx_data["max_speed"]
    workout.ave_speed = gpx_data["average_speed"]
    return workout


def create_segment(
    workout_id: int, workout_uuid: UUID, segment_data: Dict
) -> WorkoutSegment:
    """
    Create Workout Segment from gpx data
    """
    new_segment = WorkoutSegment(
        workout_id=workout_id,
        workout_uuid=workout_uuid,
        segment_id=segment_data["idx"],
    )
    new_segment.duration = _remove_microseconds(segment_data["duration"])
    new_segment.distance = segment_data["distance"]
    update_workout_data(new_segment, segment_data)
    return new_segment


def edit_workout(
    workout: Workout, workout_data: Dict, auth_user: User
) -> Workout:
    """
    Edit a workout
    Note: the gpx file is NOT modified

    In a next version, map_data and weather_data will be updated
    (case of a modified gpx file, see issue #7)
    """
    if workout_data.get("sport_id"):
        workout.sport_id = workout_data["sport_id"]
    if workout_data.get("title"):
        workout.title = workout_data["title"][:TITLE_MAX_CHARACTERS]
    if workout_data.get("notes") is not None:
        workout.notes = workout_data["notes"][:NOTES_MAX_CHARACTERS]
    if workout_data.get("description") is not None:
        workout.description = workout_data["description"][
            :DESCRIPTION_MAX_CHARACTERS
        ]
    if workout_data.get("equipments_list") is not None:
        workout.equipments = workout_data["equipments_list"]
    if workout_data.get("workout_visibility") is not None:
        workout.workout_visibility = VisibilityLevel(
            workout_data.get("workout_visibility")
        )
    if not workout.gpx:
        if workout_data.get("workout_date"):
            workout.workout_date, _ = get_workout_datetime(
                workout_date=workout_data.get("workout_date", ""),
                date_str_format=WORKOUT_DATE_FORMAT,
                user_timezone=auth_user.timezone,
            )

        if workout_data.get("duration"):
            workout.duration = timedelta(seconds=workout_data["duration"])
            workout.moving = workout.duration

        if workout_data.get("distance"):
            workout.distance = workout_data["distance"]

        if workout.distance is not None:
            workout.ave_speed = (
                None
                if workout.duration.seconds == 0
                else float(workout.distance)
                / (workout.duration.seconds / 3600)
            )
            workout.max_speed = workout.ave_speed

        if "ascent" in workout_data:
            workout.ascent = workout_data.get("ascent")

        if "descent" in workout_data:
            workout.descent = workout_data.get("descent")

    else:
        if workout_data.get("analysis_visibility") is not None:
            analysis_visibility = VisibilityLevel(
                workout_data.get("analysis_visibility")
            )
            workout.analysis_visibility = get_calculated_visibility(
                visibility=analysis_visibility,
                parent_visibility=workout.workout_visibility,
            )
        if workout_data.get("map_visibility") is not None:
            map_visibility = VisibilityLevel(
                workout_data.get("map_visibility")
            )
            workout.map_visibility = get_calculated_visibility(
                visibility=map_visibility,
                parent_visibility=workout.analysis_visibility,
            )
    return workout


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


def get_ordered_workouts(workouts: List[Workout], limit: int) -> List[Workout]:
    return sorted(
        workouts, key=lambda workout: workout.workout_date, reverse=True
    )[:limit]


def get_workout(
    workout_short_id: str, auth_user: Optional[User], allow_admin: bool = False
) -> Workout:
    workout_uuid = decode_short_id(workout_short_id)
    workout = Workout.query.filter(Workout.uuid == workout_uuid).first()
    if not workout or (
        not can_view(workout, "workout_visibility", auth_user)
        and not (allow_admin and auth_user and auth_user.has_admin_rights)
    ):
        raise WorkoutForbiddenException()
    return workout

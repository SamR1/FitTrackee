from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy.sql import text

from fittrackee import db
from fittrackee.utils import decode_short_id
from fittrackee.workouts.exceptions import WorkoutGPXException
from fittrackee.workouts.utils.geometry import (
    get_chart_data_from_segment_points,
)

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


def get_chart_data(
    workout: "Workout",
    *,
    user: Optional["User"],
    can_see_heart_rate: bool,
    segment_short_id: Optional[str] = None,
) -> Optional[List]:
    """
    Get chart data from segments points if the segments have points, otherwise
    from the gpx file.
    """
    sql = """
        SELECT workout_segments.points
        FROM workout_segments
        WHERE workout_segments.workout_id  = :workout_id"""
    values: Dict = {"workout_id": workout.id}
    if segment_short_id is not None:
        segment_uuid = decode_short_id(segment_short_id)
        sql += """
          AND workout_segments.uuid  = :segment_uuid"""
        values["segment_uuid"] = segment_uuid
    sql += """
        ORDER BY workout_id, start_date"""
    segments_points = db.session.execute(text(sql), values).mappings().all()

    if not segments_points:
        raise WorkoutGPXException(
            "not found",
            (
                f"No segment with id '{segment_short_id}'"
                if segment_short_id is not None
                else "No segments"
            ),
            None,
        )

    if segments_points[0].points:
        return get_chart_data_from_segment_points(
            [segment["points"] for segment in segments_points],
            workout.sport,
            user=user,
            workout_ave_cadence=workout.ave_cadence,
            can_see_heart_rate=can_see_heart_rate,
        )

    return []

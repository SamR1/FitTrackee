from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.sql import text

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.workouts.exceptions import WorkoutGPXException
from fittrackee.workouts.utils.geometry import (
    get_chart_data_from_segment_points,
)
from fittrackee.workouts.utils.gpx import get_chart_data_from_gpx

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


def get_chart_data(
    workout: "Workout",
    *,
    can_see_heart_rate: bool,
    segment_id: Optional[int] = None,
) -> Optional[List]:
    """
    Get chart data from segments points if the segments have points, otherwise
    from the gpx file.
    """
    sql = """
        SELECT workout_segments.points
        FROM workout_segments
        WHERE workout_segments.workout_id  = :workout_id"""
    values = {"workout_id": workout.id}
    if segment_id is not None:
        segment_index = segment_id - 1
        if segment_index < 0:
            raise WorkoutGPXException("error", "Incorrect segment id", None)
        sql += """
          AND workout_segments.segment_id  = :segment_id"""
        values["segment_id"] = segment_index
    sql += """
        ORDER BY workout_id, segment_id"""
    segments_points = db.session.execute(text(sql), values).mappings().all()

    if not segments_points:
        raise WorkoutGPXException(
            "not found",
            (
                f"No segment with id '{segment_id}'"
                if segment_id is not None
                else "No segments"
            ),
            None,
        )

    if segments_points[0].points:
        return get_chart_data_from_segment_points(
            [segment["points"] for segment in segments_points],
            workout.sport.label,
            workout_ave_cadence=workout.ave_cadence,
            can_see_heart_rate=can_see_heart_rate,
        )

    if not workout.gpx:
        return []

    absolute_gpx_filepath = get_absolute_file_path(workout.gpx)
    return get_chart_data_from_gpx(
        absolute_gpx_filepath,
        workout.sport.label,
        workout.ave_cadence,
        can_see_heart_rate=can_see_heart_rate,
        segment_id=segment_id,
    )

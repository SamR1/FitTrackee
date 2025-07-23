from typing import TYPE_CHECKING, List, Optional

from fittrackee.files import get_absolute_file_path
from fittrackee.workouts.exceptions import WorkoutGPXException
from fittrackee.workouts.models import WorkoutSegment
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
    filters = [WorkoutSegment.workout_id == workout.id]
    if segment_id is not None:
        segment_index = segment_id - 1
        if segment_index < 0:
            raise WorkoutGPXException("error", "Incorrect segment id", None)
        filters.append(WorkoutSegment.segment_id == segment_id - 1)
    segment = WorkoutSegment.query.filter(*filters).first()

    if not segment:
        raise WorkoutGPXException(
            "not found",
            f"No segment with id '{segment_id}'"
            if segment_id is not None
            else "No segments",
            None,
        )

    if len(segment.points) == 0:
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

    return get_chart_data_from_segment_points(
        [segment] if segment_id else workout.segments,
        workout.sport.label,
        workout_ave_cadence=workout.ave_cadence,
        can_see_heart_rate=can_see_heart_rate,
    )

import json
from typing import TYPE_CHECKING, Dict, Optional

from sqlalchemy import func, select

from fittrackee import db
from fittrackee.workouts.models import WorkoutSegment

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


def get_geojson_from_segments(
    workout: "Workout",
    *,
    segment_id: Optional[int] = None,
) -> Optional[Dict]:
    segments_count = len(workout.segments) if segment_id is None else 1
    filters = [WorkoutSegment.workout_id == workout.id]
    if segment_id:
        filters.append(WorkoutSegment.segment_id == segment_id)
    geom_subquery = select(WorkoutSegment.geom).filter(*filters).subquery()
    subquery = (
        func.ST_Collect(geom_subquery.c.geom)
        if segment_id is None and (segments_count > 1)
        else geom_subquery.c.geom
    )
    geojson = db.session.scalar(func.ST_AsGeoJSON(subquery))
    if geojson:
        return json.loads(geojson)
    return None

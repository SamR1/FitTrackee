import json
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import func, select

from fittrackee import db
from fittrackee.workouts.constants import (
    POWER_SPORTS,
    RPM_CADENCE_SPORTS,
    SPM_CADENCE_SPORTS,
    SPORTS_WITHOUT_ELEVATION_DATA,
)
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


def get_chart_data_from_segment_points(
    segments: List["WorkoutSegment"],
    sport_label: str,
    *,
    workout_ave_cadence: Optional[int],
    can_see_heart_rate: bool,
) -> List:
    """
    Return data needed to generate chart with:
    - speed
    - elevation (if available)
    - heart rate (if available)
    - cadence (if available)
    - power (if available)
    """
    chart_data = []
    # elevation
    return_elevation_data = sport_label not in SPORTS_WITHOUT_ELEVATION_DATA
    # from extension: cadence
    return_cadence = (
        workout_ave_cadence
        and sport_label in RPM_CADENCE_SPORTS + SPM_CADENCE_SPORTS
    )
    cadence_in_spm = sport_label in SPM_CADENCE_SPORTS
    # from extension: power
    return_power = sport_label in POWER_SPORTS
    total_distance = 0

    for segment in segments:
        if not segment.points:
            continue

        points_count = len(segment.points)

        first_point = segment.points[0]
        first_point_duration = (
            first_point["duration"] if len(segments) == 1 else 0
        )

        for index, point in enumerate(segment.points, start=1):
            distance = round((point["distance"]) / 1000 + total_distance, 2)
            data = {
                "distance": distance,
                "duration": point["duration"] - first_point_duration,
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "speed": point["speed"],
                "time": point["time"],
            }
            if return_elevation_data and point.get("elevation"):
                data["elevation"] = point["elevation"]
            if return_cadence and "cadence" in point:
                data["cadence"] = (
                    point["cadence"] * 2
                    if cadence_in_spm
                    else point["cadence"]
                )
            if can_see_heart_rate and "heart_rate" in point:
                data["hr"] = point["heart_rate"]
            if return_power and "power" in point:
                data["power"] = point["power"]

            if index == points_count:
                total_distance = distance
            chart_data.append(data)

    return chart_data

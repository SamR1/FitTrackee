import json
from typing import TYPE_CHECKING, Dict, List, Optional

import geopandas as gpd
from shapely import Point
from sqlalchemy import func, select

from fittrackee import db
from fittrackee.utils import decode_short_id
from fittrackee.workouts.constants import (
    WGS84_CRS,
)
from fittrackee.workouts.exceptions import (
    InvalidCoordinatesException,
    InvalidRadiusException,
)
from fittrackee.workouts.models import WorkoutSegment
from fittrackee.workouts.utils.sports import get_sport_displayed_data

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


def get_geojson_from_segments(
    workout: "Workout",
    *,
    segment_short_id: Optional[str] = None,
) -> Optional[Dict]:
    """
    To refactor when using segment uuid
    """
    filters = [WorkoutSegment.workout_id == workout.id]
    if segment_short_id is not None:
        segment_uuid = decode_short_id(segment_short_id)
        filters.append(WorkoutSegment.uuid == segment_uuid)
    geom_subquery = select(WorkoutSegment.geom).filter(*filters).subquery()
    subquery = (
        func.ST_Collect(geom_subquery.c.geom)
        if segment_short_id is None
        else geom_subquery.c.geom
    )
    geojson = db.session.scalar(func.ST_AsGeoJSON(subquery))
    if geojson:
        return json.loads(geojson)
    return None


def get_chart_data_from_segment_points(
    segments_points: List[List[Dict]],
    sport: "Sport",
    *,
    user: Optional["User"],
    workout_ave_cadence: Optional[int],
    can_see_heart_rate: bool,
) -> List:
    """
    Return data needed to generate chart with:
    - speed depending on sport and user sport preferences
    - pace on sport and user sport preferences
    - elevation (if available)
    - heart rate (if available)
    - cadence (if available)
    - power (if available)
    """
    chart_data = []
    sport_data_visibility = get_sport_displayed_data(sport, user)
    return_cadence = (
        workout_ave_cadence and sport_data_visibility.display_cadence
    )
    total_distance = 0

    for segment_points in segments_points:
        if not segment_points:
            continue

        points_count = len(segment_points)
        first_point = segment_points[0]
        first_point_duration = (
            first_point["duration"] if len(segments_points) == 1 else 0
        )

        for index, point in enumerate(segment_points, start=1):
            distance = round((point["distance"]) / 1000 + total_distance, 2)
            data = {
                "distance": distance,
                "duration": point["duration"] - first_point_duration,
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "time": point["time"],
            }
            if sport_data_visibility.display_elevation and point.get(
                "elevation"
            ):
                data["elevation"] = point["elevation"]
            if sport_data_visibility.display_pace and "pace" in point:
                data["pace"] = point["pace"]
            if sport_data_visibility.display_speed and "speed" in point:
                data["speed"] = point["speed"]
            if return_cadence and "cadence" in point:
                data["cadence"] = (
                    point["cadence"] * 2
                    if sport_data_visibility.display_spm_cadence
                    else point["cadence"]
                )
            if sport_data_visibility.display_power and "power" in point:
                data["power"] = point["power"]
            if can_see_heart_rate and "heart_rate" in point:
                data["hr"] = point["heart_rate"]

            if index == points_count:
                total_distance = distance
            chart_data.append(data)

    return chart_data


def get_buffered_location(coordinates: str, radius_str: str) -> str:
    """
    coordinates: latitude,longitude
    radius: distance in kilometers
    """
    try:
        radius = float(radius_str)
    except ValueError as e:
        raise InvalidRadiusException() from e
    if radius <= 0:
        raise InvalidRadiusException()

    try:
        latitude, longitude = coordinates.split(",")
        point = Point(float(longitude), float(latitude))
    except ValueError as e:
        raise InvalidCoordinatesException() from e

    gdf = gpd.GeoDataFrame(geometry=[point], crs=WGS84_CRS)
    gdf_in_meters = gdf.to_crs(gdf.estimate_utm_crs())
    buffered_gdf_in_meters = gdf_in_meters.buffer(radius * 1000)
    buffered_gdf = buffered_gdf_in_meters.to_crs(WGS84_CRS)
    return f"SRID={WGS84_CRS};{buffered_gdf.loc[0]}"

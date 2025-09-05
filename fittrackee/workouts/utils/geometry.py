import json
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import geopandas as gpd
import shapely.wkt
from geoalchemy2.shape import to_shape
from shapely import Point, to_geojson
from shapely.geometry import LineString, MultiLineString

from fittrackee.workouts.constants import (
    POWER_SPORTS,
    RPM_CADENCE_SPORTS,
    SPM_CADENCE_SPORTS,
    SPORTS_WITHOUT_ELEVATION_DATA,
    WGS84_CRS,
)
from fittrackee.workouts.exceptions import (
    InvalidCoordinatesException,
    InvalidRadiusException,
    WorkoutException,
)

if TYPE_CHECKING:
    from geoalchemy2 import WKBElement
    from shapely.geometry.base import BaseGeometry

    from fittrackee.workouts.models import Workout


def get_geometry(
    geometry: Union[str, "WKBElement"],
) -> "BaseGeometry":
    if isinstance(geometry, str):
        return shapely.wkt.loads(geometry)
    return to_shape(geometry)


def get_geojson_from_geometry(geometry: "BaseGeometry") -> Dict:
    return json.loads(to_geojson(geometry))


def get_geojson_from_segments(workout: "Workout") -> Optional[Dict]:
    lines = [get_geometry(s.geom) for s in workout.segments if s.geom]
    if not lines:
        return None
    geometry = (
        LineString(lines[0]) if len(lines) == 1 else MultiLineString(lines)
    )
    return get_geojson_from_geometry(geometry)


def get_geojson_from_segment(
    workout: "Workout", *, segment_id: int
) -> Optional[Dict]:
    segment_index = segment_id - 1
    if segment_index < 0:
        raise WorkoutException("error", "Incorrect segment id", None)

    segment = next(
        (s for s in workout.segments if s.segment_id == segment_index),
        None,
    )
    if not segment or not segment.geom:
        return None

    return get_geojson_from_geometry(get_geometry(segment.geom))


def get_chart_data_from_segment_points(
    segments_points: List[List[Dict]],
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

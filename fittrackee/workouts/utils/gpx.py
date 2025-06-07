import json
from datetime import timezone
from typing import Dict, List, Optional

import gpxpy.gpx
from gpxpy.geo import distance as calculate_distance
from sqlalchemy import func
from sqlalchemy.sql.expression import select

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.workouts.models import Workout, WorkoutSegment

from ..constants import RPM_CADENCE_SPORTS, SPM_CADENCE_SPORTS
from ..exceptions import WorkoutGPXException


def open_gpx_file(gpx_file: str) -> Optional[gpxpy.gpx.GPX]:
    gpx_file = open(gpx_file, "r")  # type: ignore
    gpx = gpxpy.parse(gpx_file)
    if len(gpx.tracks) == 0:
        return None
    return gpx


def get_gpx_segments(
    track_segments: List, segment_id: Optional[int] = None
) -> List:
    """
    Return list of segments, filtered on segment id if provided
    """
    if segment_id is not None:
        segment_index = segment_id - 1
        if segment_index > (len(track_segments) - 1):
            raise WorkoutGPXException(
                "not found", f"No segment with id '{segment_id}'", None
            )
        if segment_index < 0:
            raise WorkoutGPXException("error", "Incorrect segment id", None)
        segments = [track_segments[segment_index]]
    else:
        segments = track_segments

    return segments


def get_chart_data(
    workout: "Workout",
    *,
    can_see_heart_rate: bool,
    segment_id: Optional[int] = None,
) -> Optional[List]:
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


def get_chart_data_from_gpx(
    gpx_file: str,
    sport_label: str,
    workout_ave_cadence: Optional[int],
    *,
    can_see_heart_rate: bool,
    segment_id: Optional[int] = None,
) -> Optional[List]:
    """
    Return data needed to generate chart with:
    - speed
    - elevation (if available)
    - heart rate (if available)
    - cadence (if available)

    Note: some files contains only zero cadence values. In this case,
    workout average cadence is None and cadence is not displayed.
    """
    gpx = open_gpx_file(gpx_file)
    if gpx is None:
        return None

    chart_data = []
    first_point = None
    previous_point = None
    previous_distance = 0
    return_cadence = (
        workout_ave_cadence
        and sport_label in RPM_CADENCE_SPORTS + SPM_CADENCE_SPORTS
    )
    cadence_in_spm = sport_label in SPM_CADENCE_SPORTS

    track_segments = gpx.tracks[0].segments
    segments = get_gpx_segments(track_segments, segment_id)

    for segment_idx, segment in enumerate(segments):
        for point_idx, point in enumerate(segment.points):
            if segment_idx == 0 and point_idx == 0:
                first_point = point
            distance = (
                point.distance_3d(previous_point)
                if (
                    point.elevation
                    and previous_point
                    and previous_point.elevation
                )
                else point.distance_2d(previous_point)
            )
            distance = 0 if distance is None else distance
            distance += previous_distance
            speed = (
                round((segment.get_speed(point_idx) / 1000) * 3600, 2)
                if segment.get_speed(point_idx) is not None
                else 0
            )
            data = {
                "distance": (
                    round(distance / 1000, 2) if distance is not None else 0
                ),
                "duration": int(point.time_difference(first_point)),
                "latitude": point.latitude,
                "longitude": point.longitude,
                "speed": speed,
                # workaround
                # https://github.com/tkrajina/gpxpy/issues/209
                "time": point.time.replace(
                    tzinfo=timezone(point.time.utcoffset())
                ),
            }
            if point.elevation:
                data["elevation"] = round(point.elevation, 1)
            if point.extensions:
                extensions = []
                for extension in point.extensions:
                    if "TrackPointExtension" in extension.tag:
                        extensions.extend(extension)
                    else:
                        extensions.append(extension)
                for element in extensions:
                    if (
                        can_see_heart_rate
                        and element.tag.endswith("hr")
                        and element.text
                    ):
                        data["hr"] = int(element.text)
                    if (
                        return_cadence
                        and (
                            element.tag.endswith("cad")
                            or element.tag.endswith("cadence")
                        )
                        and element.text
                    ):
                        data["cadence"] = (
                            int(float(element.text)) * 2
                            if cadence_in_spm
                            else int(float(element.text))
                        )
            chart_data.append(data)
            previous_point = point
            previous_distance = distance

    return chart_data


def extract_segment_from_gpx_file(
    content: str, segment_id: int
) -> Optional[str]:
    """
    Returns segments in xml format from a gpx file content
    """
    gpx_content = gpxpy.parse(content)
    if len(gpx_content.tracks) == 0:
        return None

    track_segment = get_gpx_segments(
        gpx_content.tracks[0].segments, segment_id
    )

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for point in track_segment[0].points:
        gpx_segment.points.append(
            gpxpy.gpx.GPXTrackPoint(
                point.latitude, point.longitude, elevation=point.elevation
            )
        )

    return gpx.to_xml()


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
    """
    chart_data = []
    return_cadence = (
        workout_ave_cadence
        and sport_label in RPM_CADENCE_SPORTS + SPM_CADENCE_SPORTS
    )
    cadence_in_spm = sport_label in SPM_CADENCE_SPORTS
    previous_segment_point = None

    for segment in segments:
        if not segment.points:
            continue

        points_count = len(segment.points)

        first_point = segment.points[0]
        first_point_duration = (
            first_point["duration"] if len(segments) == 1 else 0
        )
        previous_segment_point_distance = (
            calculate_distance(
                first_point["latitude"],
                first_point["longitude"],
                first_point.get("elevation"),
                previous_segment_point["latitude"],
                previous_segment_point["longitude"],
                previous_segment_point.get("elevation"),
            )
            + previous_segment_point["distance"]
            if previous_segment_point
            else 0.0
        )

        for index, point in enumerate(segment.points, start=1):
            distance = round(
                (point["distance"] + previous_segment_point_distance) / 1000, 2
            )
            data = {
                "distance": distance,
                "duration": point["duration"] - first_point_duration,
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "speed": point["speed"],
                "time": point["time"],
            }
            if point.get("elevation"):
                data["elevation"] = point["elevation"]
            if return_cadence and "cadence" in point:
                data["cadence"] = (
                    point["cadence"] * 2
                    if cadence_in_spm
                    else point["cadence"]
                )
            if can_see_heart_rate and "heart_rate" in point:
                data["hr"] = point["heart_rate"]

            if index == points_count:
                previous_segment_point = point
            chart_data.append(data)

    return chart_data

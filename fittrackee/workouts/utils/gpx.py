from datetime import timezone
from typing import List, Optional

import gpxpy.gpx

from ..constants import (
    POWER_SPORTS,
    RPM_CADENCE_SPORTS,
    SPM_CADENCE_SPORTS,
    SPORTS_WITHOUT_ELEVATION_DATA,
)
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
    - power (if available)

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
            if point.elevation and return_elevation_data:
                data["elevation"] = round(point.elevation, 1)
            if point.extensions:
                extensions = []
                for extension in point.extensions:
                    if "TrackPointExtension" in extension.tag:
                        extensions.extend(extension)
                    else:
                        extensions.append(extension)
                for element in extensions:
                    if not element.text:
                        continue
                    if can_see_heart_rate and element.tag.endswith("hr"):
                        data["hr"] = int(element.text)
                    if return_cadence and (
                        element.tag.endswith("cad")
                        or element.tag.endswith("cadence")
                    ):
                        data["cadence"] = (
                            int(float(element.text)) * 2
                            if cadence_in_spm
                            else int(float(element.text))
                        )
                    if return_power and (
                        element.tag.endswith("power")
                        or element.tag.endswith("pow")
                    ):
                        data["power"] = int(element.text)
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


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()

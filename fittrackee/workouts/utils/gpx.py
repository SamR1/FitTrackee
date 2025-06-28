from datetime import timezone
from typing import TYPE_CHECKING, Dict, List, Optional

import gpxpy.gpx
import polars as pl
from gpxpy.geo import distance as calculate_distance

from ..constants import RPM_CADENCE_SPORTS, SPM_CADENCE_SPORTS
from ..exceptions import WorkoutGPXException

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint


def open_gpx_file(gpx_file: str) -> Optional["gpxpy.gpx.GPX"]:
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


def calculate_distance_from_previous_point(struct: dict) -> float:
    if struct["previous_latitude"] is None:
        return 0.0
    return calculate_distance(
        struct["latitude"],
        struct["longitude"],
        struct["elevation"],
        struct["previous_latitude"],
        struct["previous_longitude"],
        struct["previous_elevation"],
    )


def get_extensions(point: "GPXTrackPoint") -> Dict:
    point_extensions: Dict = {"hr": None, "cadence": None}

    if not point.extensions:
        return point_extensions

    extensions = []
    for extension in point.extensions:
        if "TrackPointExtension" in extension.tag:
            extensions.extend(extension)
        else:
            extensions.append(extension)

    for element in extensions:
        if element.tag.endswith("hr") and element.text:
            point_extensions["hr"] = int(element.text)
        if (
            element.tag.endswith("cad") or element.tag.endswith("cadence")
        ) and element.text:
            point_extensions["cadence"] = int(float(element.text))
    return point_extensions


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

    Note: some files contains only zero cadence values. In this case,
    workout average cadence is None and cadence is not displayed.
    """
    gpx = open_gpx_file(gpx_file)
    if gpx is None:
        return None

    segments = get_gpx_segments(gpx.tracks[0].segments, segment_id)
    if not segments:
        return None

    first_point = None
    for segment in segments:
        if segment.points:
            first_point = segment.points[0]
            break
    if not first_point:
        return None

    first_point_time = first_point.time.replace(
        tzinfo=timezone(first_point.time.utcoffset())
    )

    return_cadence = (
        workout_ave_cadence
        and sport_label in RPM_CADENCE_SPORTS + SPM_CADENCE_SPORTS
    )
    cadence_in_spm = sport_label in SPM_CADENCE_SPORTS
    columns_to_return = [
        "distance",
        "duration",
        "elevation",
        "latitude",
        "longitude",
        "speed",
        "time",
    ]
    if return_cadence:
        columns_to_return.append("cadence")
    if can_see_heart_rate:
        columns_to_return.append("hr")

    points = []
    for segment in segments:
        for point_idx, point in enumerate(segment.points):
            points.append(
                {
                    "longitude": point.longitude,
                    "latitude": point.latitude,
                    "elevation": point.elevation,
                    "time": point.time.replace(
                        tzinfo=timezone(point.time.utcoffset())
                    ),
                    "speed": segment.get_speed(point_idx),
                    **get_extensions(point),
                }
            )

    df = (
        pl.LazyFrame(
            data=points,
        )
        .with_columns(
            duration=(pl.col("time") - first_point_time).dt.total_seconds()
        )
        .with_columns(previous_longitude=pl.col("longitude").shift(1))
        .with_columns(previous_latitude=pl.col("latitude").shift(1))
        .with_columns(previous_elevation=pl.col("elevation").shift(1))
        .with_columns(
            point_distance=pl.struct(
                pl.col("latitude"),
                pl.col("longitude"),
                pl.col("elevation"),
                pl.col("previous_latitude"),
                pl.col("previous_longitude"),
                pl.col("previous_elevation"),
            ).map_elements(
                calculate_distance_from_previous_point, return_dtype=pl.Float64
            )
        )
        .with_columns(
            distance=(pl.col("point_distance").cum_sum() / 1000).round(2)
        )
        .with_columns(speed=(pl.col("speed") / 1000 * 3600).round(2))
        .with_columns(
            cadence=pl.when(cadence_in_spm)
            .then(pl.col("cadence") * 2)
            .otherwise(pl.col("cadence"))
        )
    )

    return (
        df.select(*columns_to_return)
        .drop(pl.selectors.by_dtype(pl.Null))
        .collect()
        .rows(named=True)
    )


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

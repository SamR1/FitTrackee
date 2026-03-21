from typing import TYPE_CHECKING, Dict, Optional, Union

import gpxpy.gpx
from gpxpy.gpxfield import parse_time
from lxml import etree as ET

from fittrackee import VERSION
from fittrackee.workouts.exceptions import WorkoutGPXException

from ..constants import NSMAP, TRACK_EXTENSION_NSMAP

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


def open_gpx_file(gpx_file: str) -> Optional["gpxpy.gpx.GPX"]:
    gpx_file = open(gpx_file, "r")  # type: ignore
    gpx = gpxpy.parse(gpx_file)
    if len(gpx.tracks) == 0:
        return None
    return gpx


VALID_EXTENSIONS = {
    "cadence": "{gpxtpx}cad",
    "heart_rate": "{gpxtpx}hr",
    "power": "{gpxtpx}power",
}


def get_track_extension(calories: Union[int, str]) -> "ET.Element":
    track_extension = ET.Element(
        "{gpxtrkx}TrackStatsExtension",
        nsmap=TRACK_EXTENSION_NSMAP,
    )
    calories_element = ET.SubElement(track_extension, "{gpxtrkx}Calories")
    calories_element.text = str(calories)
    return track_extension


def get_extensions(point: Dict) -> Optional["ET.Element"]:
    track_point_extension = ET.Element("{gpxtpx}TrackPointExtension")
    has_extension = False
    for extension in VALID_EXTENSIONS.keys():
        if point.get(extension) is not None:
            element = ET.SubElement(
                track_point_extension, VALID_EXTENSIONS[extension]
            )
            element.text = str(point[extension])
            has_extension = True
    return track_point_extension if has_extension else None


def generate_gpx(workout: "Workout") -> str:
    if not workout.segments:
        raise WorkoutGPXException("error", "No segments")

    gpx_track = gpxpy.gpx.GPXTrack()
    nsmap = NSMAP

    if workout.calories is not None:
        track_extension = get_track_extension(str(workout.calories))
        gpx_track.extensions.append(track_extension)
        nsmap = {**nsmap, **TRACK_EXTENSION_NSMAP}

    for segment in workout.segments:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()

        for point in segment.points:
            gpx_point = gpxpy.gpx.GPXTrackPoint(
                point.get("latitude"),
                point.get("longitude"),
                elevation=point.get("elevation"),
                time=parse_time(point.get("time", "")),
            )
            extensions = get_extensions(point)
            if extensions is not None:
                gpx_point.extensions.append(extensions)
            gpx_segment.points.append(gpx_point)

        gpx_track.segments.append(gpx_segment)

    gpx = gpxpy.gpx.GPX()
    source = f" (from {workout.source})" if workout.source else ""
    gpx.creator = f"FitTrackee v{VERSION}{source}"
    gpx.nsmap = nsmap
    gpx.tracks.append(gpx_track)

    return gpx.to_xml(prettyprint=True)

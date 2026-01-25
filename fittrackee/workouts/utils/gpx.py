from typing import TYPE_CHECKING, Dict, Optional

import gpxpy.gpx
from gpxpy.gpxfield import parse_time
from lxml import etree as ET

from fittrackee import VERSION
from fittrackee.workouts.exceptions import WorkoutGPXException

from ..constants import NSMAP

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


def open_gpx_file(gpx_file: str) -> Optional["gpxpy.gpx.GPX"]:
    gpx_file = open(gpx_file, "r")  # type: ignore
    gpx = gpxpy.parse(gpx_file)
    if len(gpx.tracks) == 0:
        return None
    return gpx


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()


VALID_EXTENSIONS = {
    "cadence": "{gpxtpx}hr",
    "heart_rate": "{gpxtpx}cad",
    "power": "{gpxtpx}power",
}


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
    gpx.nsmap = NSMAP
    gpx.tracks.append(gpx_track)

    return gpx.to_xml(prettyprint=True)

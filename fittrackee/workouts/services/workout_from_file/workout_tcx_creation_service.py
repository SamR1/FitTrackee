import re
from typing import IO, Dict, Optional

import gpxpy.gpx
import xmltodict
from gpxpy.gpxfield import parse_time

from ...exceptions import WorkoutFileException
from .constants import NSMAP
from .workout_gpx_creation_service import WorkoutGpxCreationService


class WorkoutTcxCreationService(WorkoutGpxCreationService):
    @staticmethod
    def _get_elevation(point: Dict) -> Optional[float]:
        altitude_meters = point.get("AltitudeMeters")
        if altitude_meters is None:
            return None
        elevation = float(altitude_meters)
        # workaround
        # some devices/softwares return invalid elevation values
        # see https://github.com/piggz/harbour-amazfish/issues/494
        if -9999.99 < elevation < 9999.99:
            return elevation
        return None

    @classmethod
    def parse_file(cls, workout_file: IO[bytes]) -> "gpxpy.gpx.GPX":
        """
        Tcx files contain activities that contain laps containing tracks.
        A gpx file generated from tcx file contains one track containing one
        segment per activity.

        TODO:
        - handle multiple sports activities like Swimrun
        """
        try:
            tcx_dict = xmltodict.parse(workout_file)
        except Exception as e:
            raise WorkoutFileException(
                "error", "error when parsing tcx file"
            ) from e

        activities = (
            tcx_dict["TrainingCenterDatabase"]
            .get("Activities", {})
            .get("Activity", [])
        )
        if isinstance(activities, dict):
            activities = [activities]

        if not activities:
            raise WorkoutFileException(
                "error", "no activities in tcx file"
            ) from None

        gpx_track = gpxpy.gpx.GPXTrack()
        has_tracks = False
        cadence_prefix_tag = ""

        for activity in activities:
            has_points = False
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            laps = activity.get("Lap", [])
            if isinstance(laps, dict):
                laps = [laps]
            if not laps:
                continue

            for lap in laps:
                tcx_tracks = lap.get("Track", [])
                if isinstance(tcx_tracks, dict):
                    tcx_tracks = [tcx_tracks]
                if not tcx_tracks:
                    continue

                for tcx_track in tcx_tracks:
                    has_tracks = True

                    points = tcx_track.get("Trackpoint", [])
                    if isinstance(points, dict):
                        points = [points]

                    if not points:
                        continue

                    for point in points:
                        coordinates = point.get("Position", {})
                        if not coordinates:
                            continue

                        gpx_track_point = gpxpy.gpx.GPXTrackPoint(
                            longitude=float(
                                coordinates.get("LongitudeDegrees")
                            ),
                            latitude=float(coordinates.get("LatitudeDegrees")),
                            elevation=cls._get_elevation(point),
                            time=parse_time(point.get("Time")),
                        )

                        heart_rate = point.get("HeartRateBpm", {}).get("Value")
                        cadence = point.get("Cadence", {})
                        if not cadence:
                            extensions = point.get("Extensions", {})
                            if not cadence_prefix_tag:
                                tpx_tag = [
                                    key
                                    for key in extensions.keys()
                                    if re.search("TPX$", key)
                                ]
                                if tpx_tag:
                                    tpx_tag_prefix = tpx_tag[0].split(":")[0]
                                    if tpx_tag_prefix != "TPX":
                                        cadence_prefix_tag = (
                                            f"{tpx_tag_prefix}:"
                                        )
                            cadence = extensions.get(
                                f"{cadence_prefix_tag}TPX", {}
                            ).get(f"{cadence_prefix_tag}RunCadence")

                        if heart_rate is not None or cadence is not None:
                            gpx_track_point.extensions.append(
                                cls._get_extensions(heart_rate, cadence)
                            )

                        gpx_segment.points.append(gpx_track_point)
                        has_points = True

            if has_points:
                gpx_track.segments.append(gpx_segment)

        if not has_tracks:
            raise WorkoutFileException(
                "error", "no laps or no tracks in tcx file"
            ) from None

        if not gpx_track.segments:
            raise WorkoutFileException(
                "error", "no coordinates in tcx file"
            ) from None

        gpx = gpxpy.gpx.GPX()
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx

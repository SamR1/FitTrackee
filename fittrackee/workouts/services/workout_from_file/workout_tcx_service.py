import re
from typing import IO, Dict, Optional

import gpxpy.gpx
import xmltodict
from gpxpy.gpxfield import parse_time

from ...exceptions import WorkoutFileException
from .constants import NSMAP
from .workout_gpx_service import WorkoutGpxService


class WorkoutTcxService(WorkoutGpxService):
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
    def parse_file(
        cls, workout_file: IO[bytes], segments_creation_event: str
    ) -> "gpxpy.gpx.GPX":
        """
        Tcx files contain activities that contain laps containing tracks.
        A gpx file generated from tcx file contains one track containing one
        segment per activity.

        TODO:
        - handle multiple sports activities like Swimrun

        Note:
        - segments_creation_event is not used (only for .fit files)
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
        tag_prefix = None
        creator = ""

        for activity in activities:
            has_points = False

            if not creator:
                creator = activity.get("Creator", {}).get("Name", "")

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
                        cadence = point.get("Cadence")
                        power = None

                        extensions = point.get("Extensions", {})
                        tpx_tags = [
                            key
                            for key in extensions.keys()
                            if re.search("TPX$", key)
                        ]
                        if tpx_tags:
                            tpx_tag = tpx_tags[0]
                            if tag_prefix is None:
                                tag_prefix = (
                                    f"{tpx_tag.split(':')[0]}:"
                                    if ":" in tpx_tag
                                    else ""
                                )

                            power = extensions.get(tpx_tag, {}).get(
                                f"{tag_prefix}Watts"
                            )

                            if not cadence:
                                cadence = extensions.get(
                                    f"{tag_prefix}TPX", {}
                                ).get(f"{tag_prefix}RunCadence")

                        if (
                            heart_rate is not None
                            or cadence is not None
                            or power is not None
                        ):
                            gpx_track_point.extensions.append(
                                cls._get_extensions(heart_rate, cadence, power)
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
        author = (
            tcx_dict["TrainingCenterDatabase"].get("Author", {}).get("Name")
        )
        gpx.creator = creator if creator else author
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx

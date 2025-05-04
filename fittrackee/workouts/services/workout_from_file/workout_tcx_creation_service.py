from typing import IO

import gpxpy.gpx
import xmltodict
from gpxpy.gpxfield import parse_time

from ...exceptions import WorkoutFileException
from .workout_gpx_creation_service import WorkoutGpxCreationService


class WorkoutTcxCreationService(WorkoutGpxCreationService):
    @classmethod
    def parse_file(cls, workout_file: IO[bytes]) -> "gpxpy.gpx.GPX":
        """
        tcx files contain laps, which contain tracks.
        for now gpx file generated from tcx file contains only one track and
        one segment.
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
        laps = activities[0].get("Lap", [])
        if isinstance(laps, dict):
            laps = [laps]

        if not laps:
            raise WorkoutFileException(
                "error", "no laps in tcx file"
            ) from None

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()

        has_tracks = False
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
                for point in points:
                    coordinates = point.get("Position", {})
                    if not coordinates:
                        continue
                    altitude = point.get("AltitudeMeters")
                    gpx_segment.points.append(
                        gpxpy.gpx.GPXTrackPoint(
                            longitude=float(
                                coordinates.get("LongitudeDegrees")
                            ),
                            latitude=float(coordinates.get("LatitudeDegrees")),
                            elevation=float(altitude) if altitude else None,
                            time=parse_time(point.get("Time")),
                        )
                    )

        if not has_tracks:
            raise WorkoutFileException(
                "error", "no tracks in tcx file"
            ) from None

        gpx_track.segments.append(gpx_segment)
        gpx = gpxpy.gpx.GPX()
        gpx.tracks.append(gpx_track)
        return gpx

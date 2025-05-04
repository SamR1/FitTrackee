from typing import IO

import fitdecode
import gpxpy.gpx

from ...exceptions import WorkoutFileException
from .workout_gpx_creation_service import WorkoutGpxCreationService


class WorkoutFitCreationService(WorkoutGpxCreationService):
    @staticmethod
    def _get_coordinate(value: int) -> float:
        """
        converts coordinates from semicircles
        """
        return round(value * (180.0 / 2**31), 5)

    @classmethod
    def parse_file(cls, workout_file: IO[bytes]) -> "gpxpy.gpx.GPX":
        """
        For now only Activity Files are supported.
        see:
        https://developer.garmin.com/fit/file-types/activity/

        Activity File contains Laps (intervals in session) and Records.

        For now, only records are parsed and gpx file generated from fit file
        contains only one track and one segment.

        TODO:
        - handle multiple sports activities (see Session)
        """
        try:
            fit_file = fitdecode.FitReader(workout_file)
        except Exception as e:
            raise WorkoutFileException(
                "error", "error when parsing fit file"
            ) from e

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()

        try:
            for frame in fit_file:
                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue
                if frame.name != "record":
                    continue
                longitude = frame.get_value("position_long")
                latitude = frame.get_value("position_lat")
                time = frame.get_value("timestamp")
                if not longitude or not latitude or not time:
                    continue
                elevation = frame.get_value("enhanced_altitude")
                gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(
                        longitude=cls._get_coordinate(longitude),
                        latitude=cls._get_coordinate(latitude),
                        elevation=float(elevation) if elevation else None,
                        time=time,
                    )
                )
        except fitdecode.exceptions.FitHeaderError as e:
            raise WorkoutFileException(
                "error", "error when parsing fit file"
            ) from e

        gpx_track.segments.append(gpx_segment)
        gpx = gpxpy.gpx.GPX()
        gpx.tracks.append(gpx_track)
        return gpx

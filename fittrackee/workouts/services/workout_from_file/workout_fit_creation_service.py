from typing import IO

import fitdecode
import gpxpy.gpx

from ...exceptions import WorkoutFileException
from .constants import NSMAP
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
        contains only one track. A new segment is created on after 'stop_all'
        event.

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
        has_stop = False
        try:
            for frame in fit_file:
                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue
                # create a new segment after 'stop_all' event
                if (
                    frame.name == "event"
                    and frame.get_value("event") == "timer"
                    and frame.get_value("event_type") == "stop_all"
                ):
                    has_stop = True
                    gpx_track.segments.append(gpx_segment)
                    gpx_segment = gpxpy.gpx.GPXTrackSegment()

                if frame.name != "record":
                    continue

                longitude = (
                    frame.get_value("position_long")
                    if frame.has_field("position_long")
                    else None
                )
                latitude = (
                    frame.get_value("position_lat")
                    if frame.has_field("position_lat")
                    else None
                )
                time = (
                    frame.get_value("timestamp")
                    if frame.has_field("timestamp")
                    else None
                )
                if not longitude or not latitude or not time:
                    continue

                elevation = (
                    frame.get_value("enhanced_altitude")
                    if frame.has_field("enhanced_altitude")
                    else None
                )
                heart_rate = (
                    frame.get_value("heart_rate")
                    if frame.has_field("heart_rate")
                    else None
                )
                cadence = (
                    frame.get_value("cadence")
                    if frame.has_field("cadence")
                    else None
                )

                point = gpxpy.gpx.GPXTrackPoint(
                    longitude=cls._get_coordinate(longitude),
                    latitude=cls._get_coordinate(latitude),
                    elevation=float(elevation) if elevation else None,
                    time=time,
                )

                if heart_rate is not None or cadence is not None:
                    point.extensions.append(
                        cls._get_extensions(heart_rate, cadence)
                    )
                gpx_segment.points.append(point)

        except fitdecode.exceptions.FitHeaderError as e:
            raise WorkoutFileException(
                "error", "error when parsing fit file"
            ) from e

        if not has_stop:
            gpx_track.segments.append(gpx_segment)

        gpx = gpxpy.gpx.GPX()
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx

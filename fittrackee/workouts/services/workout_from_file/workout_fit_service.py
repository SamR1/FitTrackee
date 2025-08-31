from typing import IO, Optional

import fitdecode
import gpxpy.gpx

from ...exceptions import WorkoutFileException
from .constants import GARMIN_DEVICES, NSMAP
from .workout_gpx_service import WorkoutGpxService


class WorkoutFitService(WorkoutGpxService):
    @staticmethod
    def get_coordinate(value: int) -> float:
        """
        converts coordinates from semicircles
        """
        return value * (180.0 / 2**31)

    @classmethod
    def parse_file(
        cls,
        workout_file: IO[bytes],
        segments_creation_event: str,
    ) -> "gpxpy.gpx.GPX":
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
        creator: Optional[str] = None
        try:
            data_frames = filter(
                lambda frame: frame.frame_type == fitdecode.FIT_FRAME_DATA,
                fit_file,
            )

            # Handle device metadata from file_id
            file_id_frames = filter(
                lambda frame: frame.name == "file_id", data_frames
            )
            frame = next(file_id_frames, None)
            if frame and frame.has_field("manufacturer"):
                creator = frame.get_value("manufacturer")
                if frame.has_field("product") and frame.get_value("product"):
                    product = frame.get_raw_value("product")
                    if (
                        creator.lower() == "garmin"
                        and product in GARMIN_DEVICES.keys()
                    ):
                        product = GARMIN_DEVICES[product]
                    creator = f"{creator} {product}"

            # Handle the actual data frames. We sort them by timestamp
            # to handle devices that list events and records separately.
            event_and_record_frames = sorted(
                filter(
                    lambda frame: frame.name in ["event", "record"],
                    data_frames,
                ),
                key=lambda f: (
                    f.get_value("timestamp")
                    if f.has_field("timestamp")
                    else -1
                ),
            )

            for frame in event_and_record_frames:
                # create a new segment after 'stop_all' event
                if (
                    segments_creation_event in ["only_manual", "all"]
                    and frame.name == "event"
                    and frame.get_value("event") == "timer"
                    and frame.get_value("event_type") == "stop_all"
                ):
                    if (
                        segments_creation_event == "only_manual"
                        and frame.get_value("timer_trigger") != "manual"
                    ):
                        continue
                    if gpx_segment.points:
                        gpx_track.segments.append(gpx_segment)
                    gpx_segment = gpxpy.gpx.GPXTrackSegment()
                    continue

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
                power = (
                    frame.get_value("power")
                    if frame.has_field("power")
                    else None
                )

                point = gpxpy.gpx.GPXTrackPoint(
                    longitude=cls.get_coordinate(longitude),
                    latitude=cls.get_coordinate(latitude),
                    elevation=float(elevation) if elevation else None,
                    time=time,
                )

                if any(
                    value is not None for value in [heart_rate, cadence, power]
                ):
                    point.extensions.append(
                        cls._get_extensions(heart_rate, cadence, power)
                    )
                gpx_segment.points.append(point)

        except fitdecode.exceptions.FitHeaderError as e:
            raise WorkoutFileException(
                "error", "error when parsing fit file"
            ) from e

        if gpx_segment.points:
            gpx_track.segments.append(gpx_segment)

        if not gpx_track.segments:
            raise WorkoutFileException(
                "error", "no valid segments with GPS found in fit file"
            ) from None

        gpx = gpxpy.gpx.GPX()
        gpx.creator = creator
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx

from typing import IO, TYPE_CHECKING, Any, List, Optional

import fitdecode
import gpxpy.gpx

from ...constants import NSMAP
from ...exceptions import WorkoutFileException
from .constants import GARMIN_DEVICES
from .workout_gpx_service import WorkoutGpxService

if TYPE_CHECKING:
    from fitdecode.records import FitDataMessage


class WorkoutFitService(WorkoutGpxService):
    @staticmethod
    def get_coordinate(value: int) -> float:
        """
        converts coordinates from semicircles
        """
        return value * (180.0 / 2**31)

    @staticmethod
    def get_creator(data_frames: List["FitDataMessage"]) -> Optional[str]:
        creator = None
        # Handle device metadata from file_id
        file_id_frames = filter(lambda f: f.name == "file_id", data_frames)
        frame = next(file_id_frames, None)
        if not frame:
            return creator

        if frame.has_field("product_name"):
            creator = frame.get_value("product_name")
            if isinstance(creator, str):
                creator = creator.capitalize()
        elif frame.has_field("manufacturer"):
            creator = (
                frame.get_value("manufacturer")
                if isinstance(frame.get_value("manufacturer"), str)
                else None
            )
            if (
                creator
                and frame.has_field("product")
                and frame.get_value("product")
            ):
                product = frame.get_raw_value("product")
                if (
                    creator.lower() == "garmin"
                    and product in GARMIN_DEVICES.keys()
                ):
                    product = GARMIN_DEVICES[product]
                creator = f"{creator} {product}"
        return creator

    @staticmethod
    def get_total_calories(
        data_frames: List["FitDataMessage"],
    ) -> Optional[str]:
        # Get total calories from session
        # - total calories = resting + active calories
        # - units: kcal
        calories = None
        session_frames = filter(lambda f: f.name == "session", data_frames)
        frame = next(session_frames, None)
        if frame and frame.has_field("total_calories"):
            calories = frame.get_value("total_calories")
        return calories

    @staticmethod
    def get_value_from_frame(frame: "FitDataMessage", key: str) -> Any:
        if frame.has_field(key):
            return frame.get_value(key)
        return None

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
        try:
            data_frames = list(
                filter(
                    lambda frame: frame.frame_type == fitdecode.FIT_FRAME_DATA,
                    fit_file,
                )
            )

            creator = cls.get_creator(data_frames)

            calories = cls.get_total_calories(data_frames)

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
                        and frame.has_field("timer_trigger")
                        and frame.get_value("timer_trigger") != "manual"
                    ):
                        continue
                    if gpx_segment.points:
                        gpx_track.segments.append(gpx_segment)
                    gpx_segment = gpxpy.gpx.GPXTrackSegment()
                    continue

                if frame.name != "record":
                    continue

                longitude = cls.get_value_from_frame(frame, "position_long")
                latitude = cls.get_value_from_frame(frame, "position_lat")
                time = cls.get_value_from_frame(frame, "timestamp")
                if not longitude or not latitude or not time:
                    continue

                elevation = cls.get_value_from_frame(
                    frame, "enhanced_altitude"
                )
                # some devices store elevation as a tuple instead of a float
                if isinstance(elevation, tuple):
                    elevation = (
                        elevation[0] if elevation[0] is not None else None
                    )
                heart_rate = cls.get_value_from_frame(frame, "heart_rate")
                cadence = cls.get_value_from_frame(frame, "cadence")
                power = cls.get_value_from_frame(frame, "power")

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

        if calories:
            extension = cls._get_track_extension(calories)
            gpx_track.extensions.append(extension)

        gpx = gpxpy.gpx.GPX()
        gpx.creator = creator
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx

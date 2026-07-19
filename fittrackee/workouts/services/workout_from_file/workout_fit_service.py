from typing import IO, TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import fitdecode
import gpxpy.gpx
import numpy as np
import pandas as pd

from ...constants import NSMAP
from ...exceptions import WorkoutFileException
from .constants import GARMIN_DEVICES
from .workout_gpx_service import WorkoutGpxService

if TYPE_CHECKING:
    from fitdecode.records import FitDataMessage


FIT_MATCHING_FIELDS = {
    "avg_cadence": "ave_cadence",
    "avg_heart_rate": "ave_hr",
    "avg_power": "ave_power",
    "enhanced_avg_speed": "ave_speed",
    "enhanced_max_speed": "max_speed",
    "max_cadence": "max_cadence",
    "max_heart_rate": "max_hr",
    "max_power": "max_power",
    "total_ascent": "ascent",
    "total_descent": "descent",
    "total_distance": "distance",
    "total_elapsed_time": "duration",
    "total_timer_time": "moving",
    "total_calories": "calories",
}
ALL_KEYS = [*FIT_MATCHING_FIELDS.values(), "pauses"]


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
    def get_workout_value(df: "pd.DataFrame", key: str) -> Any:
        if key in [
            "ascent",
            "descent",
            "calories",
            "distance",
            "duration",
            "moving",
            "pauses",
        ]:
            return df[key].sum()
        if key in ["ave_cadence", "ave_hr", "ave_power", "ave_speed"]:
            return df[key].mean()
        if key in ["max_cadence", "max_hr", "max_power", "max_speed"]:
            return df[key].max()
        return None

    @classmethod
    def get_file_stats(
        cls,
        data_frames: List["FitDataMessage"],
    ) -> Dict:
        """
        Multi-sports activities like Swimrun contain multiple sessions
        """
        session_frames = filter(lambda f: f.name == "session", data_frames)
        sessions_stats = []

        for frame in session_frames:
            session_stats = {}

            for key, value in FIT_MATCHING_FIELDS.items():
                session_stats[value] = (
                    frame.get_value(key) if frame.has_field(key) else None
                )

            if session_stats["moving"] and session_stats["duration"]:
                session_stats["pauses"] = (
                    session_stats["duration"] - session_stats["moving"]
                )

            else:
                session_stats["pauses"] = None
            sessions_stats.append(session_stats)

        if len(sessions_stats) == 0:
            return {
                **{value: None for value in FIT_MATCHING_FIELDS.values()},
                "pauses": None,
            }

        if len(sessions_stats) == 1:
            return sessions_stats[0]

        df = pd.DataFrame(sessions_stats)
        workout_stats: Dict = {}
        for key in [*ALL_KEYS, "moving"]:
            value = cls.get_workout_value(df, key)
            if key in [
                "ave_speed",
                "max_speed",
                "distance",
                "duration",
                "moving",
                "calories",
            ]:
                workout_stats[key] = None if np.isnan(value) else float(value)
            else:
                workout_stats[key] = None if np.isnan(value) else int(value)

        return workout_stats

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
    ) -> Tuple["gpxpy.gpx.GPX", dict]:
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

            file_stats = cls.get_file_stats(data_frames)

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

        if file_stats["calories"]:
            # Get total calories from session
            # - total calories = resting + active calories
            # - units: kcal
            extension = cls._get_track_extension(file_stats["calories"])
            gpx_track.extensions.append(extension)

        gpx = gpxpy.gpx.GPX()
        gpx.creator = creator
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx, file_stats

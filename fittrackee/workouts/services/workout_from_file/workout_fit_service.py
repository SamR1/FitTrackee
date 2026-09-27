from typing import IO, TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import fitdecode
import gpxpy.gpx

from fittrackee.constants import ElevationDataSource, ElevationProcessing

from ...constants import FIT_MATCHING_FIELDS, FIT_MATCHING_SPORTS, NSMAP
from ...exceptions import WorkoutFileException
from .constants import GARMIN_DEVICES
from .workout_gpx_service import WorkoutGpxService

if TYPE_CHECKING:
    from fitdecode.records import FitDataMessage

    from fittrackee.users.models import User

    from ...models import Sport, Workout


class WorkoutFitService(WorkoutGpxService):
    file_type: str = "fit"

    def __init__(
        self,
        auth_user: "User",
        workout_file: IO[bytes],
        sport: "Sport",
        stopped_speed_threshold: float,
        *,
        get_weather: bool = True,
        get_elevation_on_refresh: bool = True,
        workout: Optional["Workout"] = None,
        change_elevation_source: Optional["ElevationDataSource"] = None,
        elevation_processing: Optional["ElevationProcessing"] = None,
    ):
        super().__init__(
            auth_user,
            workout_file,
            sport,
            stopped_speed_threshold,
            workout=workout,
            get_weather=get_weather,
            get_elevation_on_refresh=get_elevation_on_refresh,
            change_elevation_source=change_elevation_source,
            elevation_processing=elevation_processing,
        )

        # if stats are from file, elevation preferences are overridden
        if self.auth_user.workout_stats_from_file:
            # unless the user modifies elevation data source or processing
            if (
                self.workout
                and change_elevation_source
                and elevation_processing
            ):
                return

            if self.workout:
                self.updated_elevation_data_source = ElevationDataSource.FILE
                self.update_existing_elevation = (
                    self.workout.elevation_data_source
                    != ElevationDataSource.FILE
                ) or (
                    self.workout.elevation_processing
                    != ElevationProcessing.NONE
                )
                self.reuse_existing_elevation = (
                    not self.update_existing_elevation
                )

            else:
                self.updated_elevation_data_source = None

            self.all_data_from_file = True
            self.elevation_processing = ElevationProcessing.NONE
            self.elevation_service = None

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
    def get_sport_id_or_transition(
        frame: "FitDataMessage", multi_activities_sports: Dict
    ) -> Tuple[Optional[int], bool]:
        sport_key = ""
        if frame.has_field("sport"):
            sport_key = frame.get_value("sport")
            if sport_key == "transition":
                return None, True

            sub_sport = (
                frame.get_value("sub_sport")
                if frame.has_field("sub_sport")
                else "generic"
            )
            sport_key = f"{sport_key}|{sub_sport}"

        if not sport_key:
            return None, False

        sport_label = FIT_MATCHING_SPORTS.get(sport_key)
        if not sport_label:
            return None, False

        if sport_label in multi_activities_sports:
            return multi_activities_sports[sport_label], False

        return None, False

    @staticmethod
    def _get_session_frame_data(frame: "FitDataMessage") -> Dict:
        frame_stats: Dict = {}

        if frame.has_field("timestamp"):
            frame_stats["start_time"] = frame.get_value("timestamp")

        for key, value in FIT_MATCHING_FIELDS.items():
            frame_stats[value] = (
                frame.get_value(key) if frame.has_field(key) else None
            )

        if frame_stats["moving"] and frame_stats["duration"]:
            frame_stats["pauses"] = (
                frame_stats["duration"] - frame_stats["moving"]
            )
            if frame_stats["pauses"] < 0:
                frame_stats["pauses"] = 0
                frame_stats["duration"] = frame_stats["moving"]
        else:
            frame_stats["pauses"] = None

        return frame_stats

    @classmethod
    def get_sessions_stats(
        cls,
        data_frames: List["FitDataMessage"],
        create_segment_on_events: bool,
        multi_activities_sports: Dict,
    ) -> Tuple[List[Dict], Optional[int]]:
        """
        Multi-sports activities like Swimrun or Triathlon contain multiple
        sessions
        """
        session_frames = sorted(
            filter(lambda f: f.name == "session", data_frames),
            key=lambda f: (
                f.get_value("start_time") if f.has_field("start_time") else -1
            ),
        )
        sessions_stats: List[Dict] = []

        # for sport without several activities
        if create_segment_on_events:
            if not session_frames:
                return [cls.get_empty_stats()], None

            session_data = cls._get_session_frame_data(session_frames[0])
            return [session_data], session_data.get("calories")

        total_calories = 0
        for frame in session_frames:
            sport_id, is_transition = cls.get_sport_id_or_transition(
                frame, multi_activities_sports
            )
            session_stats: Dict = {
                "sport_id": sport_id,
                "is_transition": is_transition,
                **cls._get_session_frame_data(frame),
            }
            sessions_stats.append(session_stats)
            if session_stats.get("calories", 0):
                total_calories += session_stats["calories"]

        return sessions_stats, total_calories

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
        sport: "Sport",
    ) -> Tuple["gpxpy.gpx.GPX", List[Dict]]:
        """
        For now only Activity Files are supported.
        see:
        https://developer.garmin.com/fit/file-types/activity/

        Activity File contains Laps (intervals), Sessions and Records.

        For multi-activities sports like Swimrun and Triathlon, sessions
        are used to identify each activity, created as segment.

        Otherwise, only records are parsed and gpx file generated from fit file
        contains only one track. A new segment is created on after 'stop_all'
        event.
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

            multi_activities = {
                sport.label: sport.id for sport in sport.sports
            }
            create_segment_on_events = len(multi_activities.keys()) == 0
            sessions_stats, total_calories = cls.get_sessions_stats(
                data_frames, create_segment_on_events, multi_activities
            )
            session_index = -1

            # Handle the actual data frames. We sort them by timestamp
            # to handle devices that list events and records separately.
            event_record_and_session_frames = sorted(
                filter(
                    lambda frame: frame.name in ["event", "record", "session"],
                    data_frames,
                ),
                key=lambda f: (
                    f.get_value("timestamp")
                    if (
                        f.has_field("timestamp")
                        and f.name in ["event", "record"]
                    )
                    else f.get_value("start_time")
                    if f.has_field("start_time") and f.name == "session"
                    else -1
                ),
            )

            for frame in event_record_and_session_frames:
                # create a new segment after a new session for multi-activities
                # sport
                if not create_segment_on_events and frame.name == "session":
                    session_index += 1
                    if session_index > 0:
                        # note: Some transitions may not contain any points
                        gpx_track.segments.append(gpx_segment)
                        gpx_segment = gpxpy.gpx.GPXTrackSegment()
                    continue

                # create a new segment after 'stop_all' event
                elif (
                    create_segment_on_events
                    and segments_creation_event in ["only_manual", "all"]
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

        gpx_track.segments.append(gpx_segment)

        if not gpx_track.segments:
            raise WorkoutFileException(
                "error", "no valid segments with GPS found in fit file"
            ) from None

        if total_calories:
            # Get total calories from session
            # - total calories = resting + active calories
            # - units: kcal
            extension = cls._get_track_extension(total_calories)
            gpx_track.extensions.append(extension)

        gpx = gpxpy.gpx.GPX()
        gpx.creator = creator
        gpx.nsmap = NSMAP
        gpx.tracks.append(gpx_track)
        return gpx, sessions_stats

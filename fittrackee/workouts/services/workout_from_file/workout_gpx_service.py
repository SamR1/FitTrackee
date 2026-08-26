from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import gpxpy.gpx
import numpy as np
import pandas as pd
import pytz
from lxml import etree as ET

from fittrackee import appLog, db
from fittrackee.constants import ElevationDataSource, ElevationProcessing

from ...constants import MULTI_ACTIVITIES_SPORTS, SPORTS_WITHOUT_ELEVATION_DATA
from ...exceptions import (
    WorkoutElevationException,
    WorkoutExceedingValueException,
    WorkoutException,
    WorkoutFileException,
)
from ...models import WORKOUT_VALUES_LIMIT, Workout, WorkoutSegment
from ...utils.convert import (
    convert_speed_in_km_h,
    convert_speed_into_pace_duration,
    convert_speed_into_pace_in_sec_per_meter,
)
from ...utils.duration import remove_microseconds
from ...utils.gpx import get_track_extension
from ..elevation.elevation_mixin import ElevationMixin
from ..elevation.elevation_service import ElevationService
from ..elevation.exceptions import ElevationException
from .base_workout_with_segment_service import (
    BaseWorkoutWithSegmentsCreationService,
)
from .workout_point import WorkoutPoint

if TYPE_CHECKING:
    from uuid import UUID

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


@dataclass
class GpxInfo:
    distance: float
    duration: Optional[float]
    max_speed: float
    moving_time: float
    stopped_time: float
    max_alt: Optional[float]
    min_alt: Optional[float]
    ascent: Optional[float] = None
    descent: Optional[float] = None


class WorkoutGpxService(
    BaseWorkoutWithSegmentsCreationService, ElevationMixin
):
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
            workout,
            get_weather,
            get_elevation_on_refresh,
            change_elevation_source,
            elevation_processing,
        )
        self.gpx, self.file_stats, self.sessions_stats = self.parse_file(
            workout_file, auth_user.segments_creation_event, sport
        )
        self.cadences: List[int] = []
        self.heart_rates: List[int] = []
        self.powers: List[int] = []

    @staticmethod
    def _get_track_extension(calories: Union[int, str]) -> "ET.Element":
        return get_track_extension(calories)

    @staticmethod
    def _get_extensions(
        heart_rate: Optional[int], cadence: Optional[int], power: Optional[int]
    ) -> "ET.Element":
        track_point_extension = ET.Element("{gpxtpx}TrackPointExtension")
        if heart_rate is not None:
            heart_rate_element = ET.SubElement(
                track_point_extension, "{gpxtpx}hr"
            )
            heart_rate_element.text = str(heart_rate)
        if cadence is not None:
            cadence_element = ET.SubElement(
                track_point_extension, "{gpxtpx}cad"
            )
            cadence_element.text = str(cadence)
        if power is not None:
            power_element = ET.SubElement(
                track_point_extension, "{gpxtpx}power"
            )
            power_element.text = str(power)
        return track_point_extension

    @classmethod
    def parse_file(
        cls,
        workout_file: IO[bytes],
        segments_creation_event: str,
        sport: "Sport",
    ) -> Tuple["gpxpy.gpx.GPX", Dict, List[Dict]]:
        """
        Notes:
        - segments_creation_event is not used (only for .fit files)
        - file_stats and sessions_stats are only available for .fit files
        """
        try:
            gpx = gpxpy.parse(workout_file)  # type: ignore
        except Exception as e:
            raise WorkoutFileException(
                "error", "error when parsing gpx file"
            ) from e
        if len(gpx.tracks) == 0:
            raise WorkoutFileException(
                "error", "no tracks in gpx file"
            ) from None
        return gpx, {}, []

    @staticmethod
    def get_gpx_info(
        *,
        parsed_gpx: Union["gpxpy.gpx.GPXTrack", "gpxpy.gpx.GPXTrackSegment"],
        stopped_speed_threshold: float,
        use_raw_gpx_speed: bool,
    ) -> GpxInfo:
        moving_data = parsed_gpx.get_moving_data(
            stopped_speed_threshold=stopped_speed_threshold,
            raw=use_raw_gpx_speed,
        )
        if not moving_data:
            raise WorkoutFileException(
                "error", "gpx file is invalid"
            ) from None
        elevation = parsed_gpx.get_elevation_extremes()
        duration = parsed_gpx.get_duration()
        gpx_info = GpxInfo(
            duration=duration,
            distance=(
                moving_data.moving_distance + moving_data.stopped_distance
            ),
            moving_time=moving_data.moving_time,
            stopped_time=duration - moving_data.moving_time if duration else 0,
            max_speed=moving_data.max_speed,
            max_alt=elevation.maximum,
            min_alt=elevation.minimum,
        )
        if elevation.maximum:
            hill = parsed_gpx.get_uphill_downhill()
            gpx_info.ascent = hill.uphill
            gpx_info.descent = hill.downhill
        return gpx_info

    @staticmethod
    def check_gpx_info(gpx_info: Union["GpxInfo", Dict]) -> None:
        is_dict = isinstance(gpx_info, dict)
        for key, value in WORKOUT_VALUES_LIMIT.items():
            if key == "calories":
                continue
            gpx_info_value = (
                gpx_info.get(key)  # type: ignore[union-attr]
                if is_dict
                else getattr(gpx_info, key)
            )
            if gpx_info_value and gpx_info_value > value:
                raise WorkoutExceedingValueException(
                    f"'{key}' exceeds max value ({value})"
                )

    def set_stats_from_file(
        self,
        object_to_update: Union["Workout", "WorkoutSegment"],
        gpx_info: "GpxInfo",
        file_stats: Dict,
    ) -> None:
        self.check_gpx_info(file_stats)

        object_to_update.ascent = file_stats["ascent"]
        object_to_update.ave_speed = (
            convert_speed_in_km_h(file_stats["ave_speed"])
            if file_stats.get("ave_speed")
            else 0
        )
        object_to_update.ave_pace = convert_speed_into_pace_duration(
            object_to_update.ave_speed
        )
        object_to_update.descent = file_stats["descent"]
        object_to_update.distance = (
            file_stats["distance"] / 1000 if file_stats["distance"] else 0
        )
        object_to_update.duration = remove_microseconds(
            timedelta(
                seconds=file_stats["duration"] if file_stats["duration"] else 0
            )
        )
        object_to_update.max_alt = gpx_info.max_alt
        object_to_update.min_alt = gpx_info.min_alt
        object_to_update.moving = remove_microseconds(
            timedelta(
                seconds=file_stats["moving"] if file_stats["moving"] else 0
            )
        )
        object_to_update.pauses = remove_microseconds(
            timedelta(
                seconds=file_stats["pauses"] if file_stats["pauses"] else 0
            )
        )

        object_to_update.ave_cadence = file_stats["ave_cadence"]
        object_to_update.ave_hr = file_stats["ave_hr"]
        object_to_update.ave_power = file_stats["ave_power"]
        object_to_update.max_cadence = file_stats["max_cadence"]
        object_to_update.max_hr = file_stats["max_hr"]
        object_to_update.max_power = file_stats["max_power"]
        if isinstance(object_to_update, Workout):
            object_to_update.workout_stats_from_file = True

    def set_calculated_data(
        self,
        object_to_update: Union["Workout", "WorkoutSegment"],
        gpx_info: "GpxInfo",
        stopped_time_between_segments: timedelta,
        use_raw_gpx_speed: bool,
        raw_max_speed: Optional[float] = None,
    ) -> None:
        self.check_gpx_info(gpx_info)

        if isinstance(object_to_update, WorkoutSegment):
            max_speed = (
                raw_max_speed
                if use_raw_gpx_speed and raw_max_speed is not None
                else convert_speed_in_km_h(gpx_info.max_speed)
            )
            object_to_update.max_speed = max_speed
            object_to_update.best_pace = convert_speed_into_pace_duration(
                object_to_update.max_speed
            )
        else:
            object_to_update.workout_stats_from_file = False

        object_to_update.ascent = gpx_info.ascent
        object_to_update.ave_speed = convert_speed_in_km_h(
            gpx_info.distance / gpx_info.moving_time
            if gpx_info.moving_time > 0
            else 0
        )
        object_to_update.ave_pace = convert_speed_into_pace_duration(
            object_to_update.ave_speed
        )
        object_to_update.descent = gpx_info.descent
        object_to_update.distance = gpx_info.distance / 1000
        object_to_update.duration = remove_microseconds(
            timedelta(seconds=gpx_info.duration if gpx_info.duration else 0)
            + stopped_time_between_segments
        )
        object_to_update.max_alt = gpx_info.max_alt
        object_to_update.min_alt = gpx_info.min_alt
        object_to_update.moving = remove_microseconds(
            timedelta(seconds=gpx_info.moving_time)
        )
        object_to_update.pauses = remove_microseconds(
            timedelta(seconds=gpx_info.stopped_time)
            + stopped_time_between_segments
        )

    def set_statistics(
        self,
        *,
        parsed_gpx: Union["gpxpy.gpx.GPXTrack", "gpxpy.gpx.GPXTrackSegment"],
        object_to_update: Union["Workout", "WorkoutSegment"],
        stopped_time_between_segments: timedelta,
        stopped_speed_threshold: float,
        use_raw_gpx_speed: bool,
        hr_cadence_power_stats: dict,
        raw_max_speed: Optional[float] = None,
        all_data_from_file: bool = False,
        file_stats: Optional[Dict] = None,
    ) -> Union["Workout", "WorkoutSegment"]:
        """
        If user preferences 'workout_stats_from_file' is True and
        'all_data_from_file' is True (
        workout.elevation_data_source == ElevationDataSource.FILE and
        workout.elevation_processing == ElevationProcessing.NONE), statistics
        and elevation for charts are extracted from file.
        Otherwise, they are calculated by gpxpy according to user preferences.
        """

        gpx_info = self.get_gpx_info(
            parsed_gpx=parsed_gpx,
            stopped_speed_threshold=stopped_speed_threshold,
            use_raw_gpx_speed=use_raw_gpx_speed,
        )

        if (
            file_stats
            and self.auth_user.workout_stats_from_file
            and all_data_from_file
        ):
            self.set_stats_from_file(object_to_update, gpx_info, file_stats)
            if isinstance(object_to_update, WorkoutSegment):
                object_to_update.max_speed = (
                    convert_speed_in_km_h(file_stats["max_speed"])
                    if file_stats.get("max_speed")
                    else 0
                )
                object_to_update.best_pace = convert_speed_into_pace_duration(
                    object_to_update.max_speed
                )
        else:
            self.set_calculated_data(
                object_to_update,
                gpx_info,
                stopped_time_between_segments,
                use_raw_gpx_speed,
                raw_max_speed,
            )

            object_to_update.ave_cadence = hr_cadence_power_stats[
                "ave_cadence"
            ]
            object_to_update.ave_hr = hr_cadence_power_stats["ave_hr"]
            object_to_update.ave_power = hr_cadence_power_stats["ave_power"]
            object_to_update.max_cadence = hr_cadence_power_stats[
                "max_cadence"
            ]
            object_to_update.max_hr = hr_cadence_power_stats["max_hr"]
            object_to_update.max_power = hr_cadence_power_stats["max_power"]

        return object_to_update

    def get_workout_date(self) -> "datetime":
        if not self.start_point or not self.start_point.time:
            raise WorkoutFileException(
                "error", "<time> is missing in gpx file"
            )
        return self.start_point.time.astimezone(timezone.utc)

    def _get_hr_cadence_power_data(
        self,
        heart_rates: List[int],
        cadences: List[int],
        powers: List[int],
        *,
        is_workout: bool,
    ) -> Dict:
        """
        Some files contain only zero cadence values. In this case, workout
        average and max cadences is None and cadence is not displayed.

        For .fit files, it returns data from file instead of calculated them
        when user preference workout_stats_from_file is True and file contains
        data.
        """
        if (
            is_workout
            and self.auth_user.workout_stats_from_file
            and self.file_stats
        ):
            return {
                "ave_cadence": self.file_stats["ave_cadence"],
                "ave_hr": self.file_stats["ave_hr"],
                "ave_power": self.file_stats["ave_power"],
                "max_cadence": self.file_stats["max_cadence"],
                "max_hr": self.file_stats["max_hr"],
                "max_power": self.file_stats["max_power"],
            }

        ave_cadence = mean(cadences) if cadences else None
        return {
            "ave_cadence": ave_cadence if ave_cadence else None,
            "ave_hr": mean(heart_rates) if heart_rates else None,
            "ave_power": mean(powers) if powers else None,
            "max_cadence": max(cadences) if ave_cadence else None,
            "max_hr": max(heart_rates) if heart_rates else None,
            "max_power": max(powers) if powers else None,
        }

    def _get_point_elevation(
        self, elevation: Optional[float]
    ) -> Optional[float]:
        if not elevation or self.sport.label in SPORTS_WITHOUT_ELEVATION_DATA:
            return None

        # some devices/software stores invalid elevation values
        # note: to refactor
        if -9999.99 < elevation < 9999.99:
            return elevation
        return None

    def _get_elevation_service(
        self, segments: List["gpxpy.gpx.GPXTrackSegment"]
    ) -> Optional["ElevationService"]:
        if self.sport.label in SPORTS_WITHOUT_ELEVATION_DATA:
            return None

        if self._are_altitudes_missing_in_file(segments) and (
            self.is_creation
            or (
                self.get_elevation_on_refresh
                and self.updated_elevation_data_source is None
            )
        ):
            return ElevationService(
                self.auth_user.missing_elevations_data_source,
                self.auth_user.elevation_processing,
            )

        if (
            not self.get_elevation_on_refresh
            or not self.workout
            or self.elevation_processing is None
        ):
            return None

        if self.updated_elevation_data_source:
            return ElevationService(
                self.updated_elevation_data_source,
                self.elevation_processing,
            )

        if (
            self.workout.elevation_processing != ElevationProcessing.NONE
            and self.workout.elevation_processing != self.elevation_processing
        ):
            return ElevationService(
                self.workout.elevation_data_source,
                self.elevation_processing,
            )

        return None

    def _process_segment_points(
        self,
        track_segment: "gpxpy.gpx.GPXTrackSegment",
        stopped_time_between_segments: timedelta,
        previous_segment_last_point_time: Optional[datetime],
        new_workout_segment: "WorkoutSegment",
        first_point: "gpxpy.gpx.GPXTrackPoint",
        existing_elevations: "pd.DataFrame",
        elevation_service: Optional["ElevationService"],
        segment_stats: Dict,
    ) -> Tuple[
        timedelta,  # stopped_time_between_segments
        Optional[datetime],  # previous_segment_last_point_time
        Dict,  # hr_cadence_stats
        float,  # raw_max_speed
    ]:
        points = track_segment.points
        last_point_index = len(points) - 1
        cadences = []
        heart_rates = []
        powers = []
        previous_point = None
        previous_distance = 0.0
        segment_points: List[Dict] = []
        elevations: Union[List[int], List[float]] = []
        coordinates = []
        raw_max_speed = 0.0
        workout_id = self.workout.short_id if self.workout else ""

        if existing_elevations.empty and elevation_service:
            try:
                elevations = elevation_service.get_elevations(points)
            except Exception as e:
                raise WorkoutException(
                    "error",
                    "Error when getting elevation from elevation service",
                ) from e

        for point_idx, point in enumerate(points):
            if point_idx == 0:
                if not point.time:
                    raise WorkoutFileException(
                        "error", "<time> is missing in segment"
                    )
                new_workout_segment.start_date = point.time
                # if a previous segment exists, calculate stopped time
                # between the two segments
                if previous_segment_last_point_time and point.time:
                    stopped_time_between_segments += (
                        point.time - previous_segment_last_point_time
                    )

            point.elevation = self._get_point_elevation(point.elevation)
            # get elevation previously fetched
            if not existing_elevations.empty and (
                not self.updated_elevation_data_source
                or self.updated_elevation_data_source
                == ElevationDataSource.FILE
            ):
                try:
                    previous_value = existing_elevations.at[  # noqa: PD008
                        f"{point.time}|{point.latitude}|{point.longitude}",
                        "elevation",
                    ]
                    point.elevation = (
                        None
                        if previous_value is None or np.isnan(previous_value)
                        else float(previous_value)  # type: ignore[arg-type]
                    )
                except KeyError:
                    appLog.error(
                        "Error when getting existing elevation for "
                        f"workout '{workout_id}'."
                    )
            # get elevation from Elevation service
            elif elevations:
                point.elevation = elevations[point_idx]

            distance = (
                point.distance_3d(previous_point)  # type: ignore[arg-type]
                if (
                    point.elevation is not None
                    and previous_point is not None
                    and previous_point.elevation
                )
                else point.distance_2d(previous_point)  # type: ignore[arg-type]
            )
            distance = 0.0 if distance is None else distance
            distance += previous_distance

            calculated_speed = (
                0.0 if point_idx == 0 else track_segment.get_speed(point_idx)
            )
            speed = (
                0.0
                if calculated_speed is None
                else round(convert_speed_in_km_h(calculated_speed), 2)
            )
            raw_max_speed = speed if speed > raw_max_speed else raw_max_speed
            pace = convert_speed_into_pace_in_sec_per_meter(speed)

            time_difference = point.time_difference(first_point)

            # All values are calculated and stored regardless the sport.
            # Serializers filter and return data based on the sport.
            segment_point: Dict = {
                "distance": distance,
                "duration": int(time_difference) if time_difference else 0,
                "elevation": point.elevation,
                "latitude": point.latitude,
                "longitude": point.longitude,
                "pace": pace,
                "speed": speed,
                "time": (
                    str(point.time.astimezone(pytz.utc))
                    if point.time
                    else None
                ),
            }
            if point.extensions:
                extensions = []
                for extension in point.extensions:
                    if "TrackPointExtension" in extension.tag:
                        extensions.extend(extension)
                    else:
                        extensions.append(extension)
                for extension in extensions:
                    if not extension.text:
                        continue
                    if extension.tag == "power":
                        power = int(extension.text)
                        powers.append(power)
                        segment_point["power"] = power
                    if extension.tag.endswith("}hr"):
                        hr = int(extension.text)
                        heart_rates.append(hr)
                        segment_point["heart_rate"] = hr
                    if extension.tag.endswith("}cad"):
                        cadence = int(float(extension.text))
                        cadences.append(cadence)
                        segment_point["cadence"] = cadence
                    if extension.tag.endswith("}power"):
                        power = int(extension.text)
                        powers.append(power)
                        segment_point["power"] = power

            # last segment point
            if point_idx == last_point_index:
                previous_segment_last_point_time = point.time

                # store last gpx point (for weather data)
                # Note: since segments with one point are ignored, the last
                # point is overwritten, to get the last point from last valid
                # segment
                if point.time:
                    self.end_point = WorkoutPoint(
                        point.longitude,
                        point.latitude,
                        point.time,
                    )
            coordinates.append([point.longitude, point.latitude])
            segment_points.append(segment_point)

            previous_point = point
            previous_distance = distance

        hr_cadence_stats = self._get_hr_cadence_power_data(
            heart_rates, cadences, powers, is_workout=False
        )
        self.cadences.extend(cadences)
        self.heart_rates.extend(heart_rates)
        self.powers.extend(powers)
        self.coordinates.extend(coordinates)
        new_workout_segment.points = segment_points
        new_workout_segment.store_geometry(coordinates)

        if self.sport.label in MULTI_ACTIVITIES_SPORTS:
            new_workout_segment.calories = segment_stats.get("calories")
            new_workout_segment.sport_id = segment_stats.get("sport_id")  # type: ignore
            new_workout_segment.is_transition = segment_stats.get(
                "is_transition", False
            )

        return (
            stopped_time_between_segments,
            previous_segment_last_point_time,
            hr_cadence_stats,
            raw_max_speed,
        )

    @staticmethod
    def _get_point_index_from_database(point: Dict) -> Dict:
        return {
            "idx": (
                f"{point.get('time')}|{point.get('latitude')}|{point.get('longitude')}"
            ),
            "elevation": point.get("elevation"),
        }

    @staticmethod
    def _get_point_index_from_file(point: "gpxpy.gpx.GPXTrackPoint") -> Dict:
        return {
            "idx": f"{point.time}|{point.latitude}|{point.longitude}",
            "elevation": point.elevation,
        }

    def _get_elevation_from_segments(
        self,
        segments: Union[
            List["WorkoutSegment"], List["gpxpy.gpx.GPXTrackSegment"]
        ],
    ) -> "pd.DataFrame":
        file_elevations = pd.DataFrame()
        for index, segment in enumerate(segments):
            points = [
                {
                    **(
                        self._get_point_index_from_database(point)
                        if isinstance(point, dict)
                        else self._get_point_index_from_file(point)
                    ),
                    "segment_idx": index,
                }
                for point in segment.points  # type: ignore[attr-defined]
            ]
            if points:
                segment_df = pd.DataFrame(points).set_index(["idx"])
                file_elevations = pd.concat([file_elevations, segment_df])
        return file_elevations

    def _get_elevation_from_file(
        self, segments: List["gpxpy.gpx.GPXTrackSegment"]
    ) -> "pd.DataFrame":
        return self._get_elevation_from_segments(segments)

    def _calculate_elevation_data_source_and_processing(
        self,
        elevation_service: Optional["ElevationService"],
        existing_elevations: "pd.DataFrame",
    ) -> Tuple["ElevationDataSource", "ElevationProcessing"]:
        if elevation_service:
            return (
                elevation_service.elevation_data_source,
                elevation_service.elevation_processing,
            )

        if self.is_creation or not self.workout:
            return ElevationDataSource.FILE, ElevationProcessing.NONE

        if self.update_existing_elevation and not existing_elevations.empty:
            return self.workout.elevation_data_source, (
                self.elevation_processing
                or self.auth_user.elevation_processing
            )

        workout_elevation_data_source = (
            self.updated_elevation_data_source
            if self.updated_elevation_data_source == ElevationDataSource.FILE
            else self.workout.elevation_data_source
        )
        workout_elevation_processing = (
            self.workout.elevation_processing
            if (
                self.elevation_processing is None
                or (
                    self.elevation_processing
                    == self.workout.elevation_processing
                )
            )
            else self.elevation_processing
        )
        return workout_elevation_data_source, workout_elevation_processing

    @staticmethod
    def _are_altitudes_missing_in_file(
        segments: List["gpxpy.gpx.GPXTrackSegment"],
    ) -> bool:
        has_missing_elevation = False
        for segment in segments:
            if len(segment.points) < 2:
                continue
            has_missing_elevation = any(
                point.elevation is None for point in segment.points
            )
            if has_missing_elevation:
                break
        return has_missing_elevation

    def _get_transition_segment_with_one_point(
        self,
        new_workout_id: int,
        new_workout_uuid: "UUID",
        points: List["gpxpy.gpx.GPXTrackPoint"],
    ) -> "WorkoutSegment":
        if len(points) != 1:
            raise WorkoutException(
                "error",
                "Error when creating transition segment",
            ) from None

        point = points[0]
        new_workout_segment = WorkoutSegment(
            workout_id=new_workout_id,
            workout_uuid=new_workout_uuid,
        )
        new_workout_segment.distance = 0
        new_workout_segment.duration = timedelta()
        new_workout_segment.moving = timedelta()
        new_workout_segment.pauses = timedelta()
        new_workout_segment.start_date = point.time  # type: ignore
        new_workout_segment.is_transition = True
        new_workout_segment.points = [
            {
                "distance": 0,
                "duration": 0,
                "elevation": point.elevation,
                "latitude": point.latitude,
                "longitude": point.longitude,
                "pace": 0,
                "speed": 0,
                "time": (
                    str(point.time.astimezone(pytz.utc))
                    if point.time
                    else None
                ),
            }
        ]
        self.coordinates.append([point.longitude, point.latitude])
        new_workout_segment.store_geometry_as_point(
            [point.longitude, point.latitude]
        )
        return new_workout_segment

    def _process_segments(
        self,
        track_segments: List["gpxpy.gpx.GPXTrackSegment"],
        new_workout_id: int,
        new_workout_uuid: "UUID",
        first_point: "gpxpy.gpx.GPXTrackPoint",
    ) -> Tuple[timedelta, float, bool]:
        max_speed = 0.0
        previous_segment_last_point_time: Optional["datetime"] = None
        stopped_time_between_segments = timedelta(seconds=0)
        all_data_from_file = False
        existing_elevations = pd.DataFrame()
        elevation_service = None

        if not self.is_creation and self.workout:
            if (
                self.sport.label not in SPORTS_WITHOUT_ELEVATION_DATA
                and self.reuse_existing_elevation
            ):
                existing_elevations = self._get_elevation_from_segments(
                    WorkoutSegment.query.filter_by(
                        workout_id=self.workout.id
                    ).all()
                )
            # remove existing segments
            WorkoutSegment.query.filter_by(workout_id=self.workout.id).delete()

        # in case elevation processing changed (from 'none' to 'flat_window'),
        # the exiting elevation can be reused with calling elevation service
        if self.reuse_existing_elevation:
            if self.update_existing_elevation:
                try:
                    existing_elevations = self.get_smoothed_elevations_from_df(
                        existing_elevations, self.elevation_processing
                    )
                except ElevationException as e:
                    raise WorkoutElevationException() from e
        # - previous data source is not 'file' and switching to 'file'
        # or
        # - applying processing on a workout with data source from file
        elif (
            not self.is_creation
            and self.workout
            and (
                self.updated_elevation_data_source == ElevationDataSource.FILE
                or (
                    self.updated_elevation_data_source is None
                    and (
                        self.workout.elevation_data_source
                        == ElevationDataSource.FILE
                    )
                )
            )
        ):
            if self.elevation_processing != ElevationProcessing.NONE:
                try:
                    existing_elevations = self.get_smoothed_elevations_from_df(
                        self._get_elevation_from_file(track_segments),
                        self.elevation_processing,
                    )
                except ElevationException as e:
                    raise WorkoutElevationException() from e
        else:
            # get elevation service depending on conditions
            elevation_service = self._get_elevation_service(track_segments)
            elevation_service = (
                elevation_service
                if elevation_service
                and elevation_service.elevation_service is not None
                else None
            )

        if self.workout:
            workout_elevation_data_source, workout_elevation_processing = (
                self._calculate_elevation_data_source_and_processing(
                    elevation_service, existing_elevations
                )
            )
            self.workout.elevation_data_source = workout_elevation_data_source
            self.workout.elevation_processing = workout_elevation_processing

            all_data_from_file = (
                workout_elevation_data_source == ElevationDataSource.FILE
                and workout_elevation_processing == ElevationProcessing.NONE
            )

        for index, segment in enumerate(track_segments):
            segment_stats = {}
            if len(self.sessions_stats) >= index + 1:
                segment_stats = self.sessions_stats[index]

            # ignore segments with no distance
            if len(segment.points) == 0:
                continue

            if len(segment.points) == 1:
                # a transition segment can have 1 point
                if segment_stats.get("is_transition"):
                    new_workout_segment = (
                        self._get_transition_segment_with_one_point(
                            new_workout_id, new_workout_uuid, segment.points
                        )
                    )
                    db.session.add(new_workout_segment)
                continue

            new_workout_segment = WorkoutSegment(
                workout_id=new_workout_id,
                workout_uuid=new_workout_uuid,
            )
            db.session.add(new_workout_segment)

            (
                stopped_time_between_segments,
                previous_segment_last_point_time,
                hr_cadence_power_stats,
                raw_max_speed,
            ) = self._process_segment_points(
                segment,
                stopped_time_between_segments,
                previous_segment_last_point_time,
                new_workout_segment,
                first_point,
                existing_elevations,
                elevation_service,
                segment_stats,
            )

            self.set_statistics(
                parsed_gpx=segment,
                object_to_update=new_workout_segment,
                stopped_time_between_segments=timedelta(seconds=0),
                stopped_speed_threshold=self.stopped_speed_threshold,
                use_raw_gpx_speed=self.auth_user.use_raw_gpx_speed,
                hr_cadence_power_stats=hr_cadence_power_stats,
                raw_max_speed=raw_max_speed,
                file_stats=segment_stats,
                all_data_from_file=all_data_from_file,
            )

            if (
                new_workout_segment.max_speed
                and new_workout_segment.max_speed > max_speed
            ):
                max_speed = new_workout_segment.max_speed

        return (
            stopped_time_between_segments,
            max_speed,
            all_data_from_file,
        )

    @staticmethod
    def _get_calories(track: "gpxpy.gpx.GPXTrack") -> Optional[int]:
        # Get total calories (units: kcal)
        calories = None
        if not track.extensions:
            return calories
        for track_extension in track.extensions:
            for extension in track_extension:
                if not extension.text:
                    continue
                if extension.tag.endswith("}Calories"):
                    try:
                        calories = int(float(extension.text))
                    except ValueError:
                        calories = None
                    break
        return calories

    def _process_file(self) -> "Workout":
        if not self.gpx:
            raise WorkoutFileException(
                "error", "no gpx, please load gpx file before"
            ) from None

        track: "gpxpy.gpx.GPXTrack" = self.gpx.tracks[0]

        start_point = None
        for segment in track.segments:
            # segment must contain at least 2 points to be valid.
            if len(segment.points) > 1:
                start_point = segment.points[0]
                break

        if not start_point:
            raise WorkoutFileException(
                "error", "no valid segments in file"
            ) from None

        if start_point.time:
            self.start_point = WorkoutPoint(
                start_point.longitude,
                start_point.latitude,
                start_point.time,
            )
        self.workout_name = track.name
        self.workout_description = track.description

        if not self.workout:
            self.workout = Workout(
                user_id=self.auth_user.id,
                sport_id=self.sport.id,
                workout_date=self.get_workout_date(),
            )
            db.session.add(self.workout)
            db.session.flush()
        self.workout.source = self.gpx.creator
        if self.start_point:
            self.workout.store_start_point_geometry(
                [self.start_point.longitude, self.start_point.latitude]
            )

        (
            stopped_time_between_segments,
            max_speed,
            all_data_from_file,
        ) = self._process_segments(
            track.segments, self.workout.id, self.workout.uuid, start_point
        )

        hr_cadence_power_stats = self._get_hr_cadence_power_data(
            self.heart_rates, self.cadences, self.powers, is_workout=True
        )
        self.set_statistics(
            parsed_gpx=track,
            object_to_update=self.workout,
            stopped_time_between_segments=stopped_time_between_segments,
            stopped_speed_threshold=self.stopped_speed_threshold,
            use_raw_gpx_speed=self.auth_user.use_raw_gpx_speed,
            hr_cadence_power_stats=hr_cadence_power_stats,
            all_data_from_file=all_data_from_file,
            file_stats=self.file_stats,
        )
        if (
            self.file_stats
            and self.auth_user.workout_stats_from_file
            and all_data_from_file
        ):
            self.workout.max_speed = (
                convert_speed_in_km_h(self.file_stats["max_speed"])
                if self.file_stats.get("max_speed")
                else 0
            )
        else:
            self.workout.max_speed = max_speed
        self.workout.best_pace = convert_speed_into_pace_duration(
            self.workout.max_speed
        )
        self.workout.calories = self._get_calories(track)
        bounds = track.get_bounds()
        self.workout.bounds = (
            [
                bounds.min_latitude,
                bounds.min_longitude,
                bounds.max_latitude,
                bounds.max_longitude,
            ]
            if (
                bounds
                and bounds.min_latitude
                and bounds.min_longitude
                and bounds.max_latitude
                and bounds.max_longitude
            )
            else []
        )

        return self.workout

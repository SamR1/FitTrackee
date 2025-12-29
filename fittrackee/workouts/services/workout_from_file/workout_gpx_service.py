from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import gpxpy.gpx
import pandas as pd
import pytz
from lxml import etree as ET

from fittrackee import appLog, db
from fittrackee.constants import ElevationDataSource

from ...constants import SPORTS_WITHOUT_ELEVATION_DATA, TRACK_EXTENSION_NSMAP
from ...exceptions import WorkoutExceedingValueException, WorkoutFileException
from ...models import WORKOUT_VALUES_LIMIT, Workout, WorkoutSegment
from ...utils.convert import (
    convert_speed_into_pace_duration,
    convert_speed_into_pace_in_sec_per_meter,
)
from ..elevation.elevation_service import ElevationService
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


def remove_microseconds(delta: "timedelta") -> "timedelta":
    return delta - timedelta(microseconds=delta.microseconds)


class WorkoutGpxService(BaseWorkoutWithSegmentsCreationService):
    def __init__(
        self,
        auth_user: "User",
        workout_file: IO[bytes],
        sport: "Sport",
        stopped_speed_threshold: float,
        get_weather: bool = True,
        get_elevation_on_refresh: bool = True,
        workout: Optional["Workout"] = None,
        change_elevation_source: Optional[ElevationDataSource] = None,
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
        )
        self.gpx: "gpxpy.gpx.GPX" = self.parse_file(
            workout_file, auth_user.segments_creation_event
        )
        self.cadences: List[int] = []
        self.heart_rates: List[int] = []
        self.powers: List[int] = []

    @staticmethod
    def _get_track_extensions(calories: str) -> "ET.Element":
        track_point_extension = ET.Element(
            "{gpxtrkx}TrackStatsExtension",
            nsmap=TRACK_EXTENSION_NSMAP,
        )
        calories_element = ET.SubElement(
            track_point_extension, "{gpxtrkx}Calories"
        )
        calories_element.text = str(calories)
        return track_point_extension

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
    ) -> "gpxpy.gpx.GPX":
        """
        Note:
        - segments_creation_event is not used (only for .fit files)
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
        return gpx

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
    def check_gpx_info(gpx_info: "GpxInfo") -> None:
        for key, value in WORKOUT_VALUES_LIMIT.items():
            gpx_info_value = getattr(gpx_info, key)
            if gpx_info_value and gpx_info_value > value:
                raise WorkoutExceedingValueException(
                    f"'{key}' exceeds max value ({value})"
                )

    def set_calculated_data(
        self,
        *,
        parsed_gpx: Union["gpxpy.gpx.GPXTrack", "gpxpy.gpx.GPXTrackSegment"],
        object_to_update: Union["Workout", "WorkoutSegment"],
        stopped_time_between_segments: timedelta,
        stopped_speed_threshold: float,
        use_raw_gpx_speed: bool,
        hr_cadence_power_stats: dict,
        raw_max_speed: Optional[float] = None,
    ) -> Union["Workout", "WorkoutSegment"]:
        gpx_info = self.get_gpx_info(
            parsed_gpx=parsed_gpx,
            stopped_speed_threshold=stopped_speed_threshold,
            use_raw_gpx_speed=use_raw_gpx_speed,
        )
        self.check_gpx_info(gpx_info)

        if isinstance(object_to_update, WorkoutSegment):
            max_speed = (
                raw_max_speed
                if use_raw_gpx_speed and raw_max_speed is not None
                else (gpx_info.max_speed / 1000) * 3600
            )
            object_to_update.max_speed = max_speed
            object_to_update.best_pace = convert_speed_into_pace_duration(
                object_to_update.max_speed
            )

        object_to_update.ascent = gpx_info.ascent
        object_to_update.ave_speed = (
            (
                gpx_info.distance / gpx_info.moving_time
                if gpx_info.moving_time > 0
                else 0
            )
            / 1000
            * 3600
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

        object_to_update.ave_cadence = hr_cadence_power_stats["ave_cadence"]
        object_to_update.ave_hr = hr_cadence_power_stats["ave_hr"]
        object_to_update.ave_power = hr_cadence_power_stats["ave_power"]
        object_to_update.max_cadence = hr_cadence_power_stats["max_cadence"]
        object_to_update.max_hr = hr_cadence_power_stats["max_hr"]
        object_to_update.max_power = hr_cadence_power_stats["max_power"]

        return object_to_update

    def get_workout_date(self) -> "datetime":
        if not self.start_point or not self.start_point.time:
            raise WorkoutFileException(
                "error", "<time> is missing in gpx file"
            )
        return self.start_point.time.astimezone(timezone.utc)

    @staticmethod
    def _get_hr_cadence_power_data(
        heart_rates: List[int], cadences: List[int], powers: List[int]
    ) -> Dict:
        """
        Some files contain only zero cadence values. In this case, workout
        average and max cadences is None and cadence is not displayed.
        """
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

    def _get_elevations_and_elevation_data_source(
        self,
        points: List["gpxpy.gpx.GPXTrackPoint"],
        existing_elevations: "pd.DataFrame",
    ) -> Tuple[List[int], "ElevationDataSource"]:
        # Get elevations if:
        # - user preference is set
        # - corresponding Elevation API URL is set
        # - at least one value is missing
        # In case or refresh on workout refresh
        # - get_elevation_on_refresh is True and no existing elevations
        # - or change_elevation_source is provided and different than
        #   ElevationDataSource.FILE

        if (
            not self.is_creation
            and self.change_elevation_source == ElevationDataSource.FILE
        ):
            return [], ElevationDataSource.FILE

        elevations = []
        elevation_data_source = (
            self.workout.elevation_data_source
            if self.workout
            else ElevationDataSource.FILE
        )

        if self.sport.label not in SPORTS_WITHOUT_ELEVATION_DATA:
            elevation_service = None
            if (
                self.is_creation
                # refresh
                or (
                    self.change_elevation_source is None
                    and existing_elevations.empty
                    and self.get_elevation_on_refresh
                )
            ) and any(point.elevation is None for point in points):
                elevation_service = ElevationService(
                    self.auth_user.missing_elevations_processing
                )
            elif (
                self.workout
                and self.change_elevation_source is not None
                and self.change_elevation_source
                != self.workout.elevation_data_source
            ):
                elevation_service = ElevationService(
                    self.change_elevation_source
                )

            if elevation_service:
                elevations = elevation_service.get_elevations(points)
                if len(elevations) > 0:
                    elevation_data_source = (
                        elevation_service.elevation_data_source
                    )
        return elevations, elevation_data_source

    def _process_segment_points(
        self,
        track_segment: "gpxpy.gpx.GPXTrackSegment",
        stopped_time_between_segments: timedelta,
        previous_segment_last_point_time: Optional[datetime],
        is_last_segment: bool,
        new_workout_segment: "WorkoutSegment",
        first_point: "gpxpy.gpx.GPXTrackPoint",
        existing_elevations: "pd.DataFrame",
    ) -> Tuple[
        timedelta,
        Optional[datetime],
        Dict,
        float,
        "ElevationDataSource",
    ]:
        points = track_segment.points
        last_point_index = len(points) - 1
        cadences = []
        heart_rates = []
        powers = []
        previous_point = None
        previous_distance = 0.0
        segment_points: List[Dict] = []
        coordinates = []
        raw_max_speed = 0.0
        workout_id = self.workout.short_id if self.workout else ""

        elevations, elevation_data_source = (
            self._get_elevations_and_elevation_data_source(
                points, existing_elevations
            )
        )

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
            if (
                not self.change_elevation_source
                and not existing_elevations.empty
            ):
                try:
                    previous_value = existing_elevations.at[
                        f"{point.time}|{point.latitude}|{point.longitude}",
                        "elevation",
                    ]
                    point.elevation = (
                        None
                        if previous_value is None
                        else float(previous_value)  # type: ignore[arg-type]
                    )
                except KeyError:
                    appLog.error(
                        "Error when getting existing elevation for "
                        f"workout '{workout_id}'."
                    )
            # get elevation from Elevation service
            elif elevation_data_source != ElevationDataSource.FILE:
                point.elevation = elevations[point_idx]

            distance = (
                point.distance_3d(previous_point)  # type: ignore[arg-type]
                if (
                    point.elevation
                    and previous_point
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
                else round((calculated_speed / 1000) * 3600, 2)
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

                # last gpx point (for weather data)
                if is_last_segment and point.time:
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
            heart_rates, cadences, powers
        )
        self.cadences.extend(cadences)
        self.heart_rates.extend(heart_rates)
        self.powers.extend(powers)
        self.coordinates.extend(coordinates)
        new_workout_segment.points = segment_points
        new_workout_segment.store_geometry(coordinates)

        return (
            stopped_time_between_segments,
            previous_segment_last_point_time,
            hr_cadence_stats,
            raw_max_speed,
            elevation_data_source,
        )

    def _can_get_existing_elevations(self) -> bool:
        # no existing elevations on creation
        if not self.workout:
            return False

        # no existing elevations to store since original file contains
        # already missing elevation or no elevation service has been
        # previously set
        if self.workout.elevation_data_source == ElevationDataSource.FILE:
            return False

        # to avoid removing existing elevation when get_elevation_on_refresh
        # is False
        if not self.get_elevation_on_refresh:
            return True

        # to avoid removing existing elevation when Elevation service has been
        # disabled (i.e. elevation API URLs have been removed)
        if not ElevationService(
            self.auth_user.missing_elevations_processing
        ).elevation_service:
            return True

        # to avoid removing existing elevation when user has set elevation
        # service and workout elevation data are already fetched from the same
        # service
        if (
            self.workout.elevation_data_source
            == self.auth_user.missing_elevations_processing
        ):
            has_missing_elevation = any(
                point.get("elevation") is None
                for segment in self.workout.segments
                for point in segment.points
            )
            return not has_missing_elevation

        # otherwise, remove existing elevation to refresh values
        return False

    def _get_existing_elevations(self) -> "pd.DataFrame":
        existing_elevations = pd.DataFrame()

        if not self.workout or not self._can_get_existing_elevations():
            return existing_elevations

        previous_segments = WorkoutSegment.query.filter_by(
            workout_id=self.workout.id
        )
        for previous_segment in previous_segments.all():
            points = [
                {
                    "idx": (
                        f"{point.get('time')}|{point.get('latitude')}|{point.get('longitude')}"
                    ),
                    "elevation": point.get("elevation"),
                }
                for point in previous_segment.points
            ]
            if points:
                segment_df = pd.DataFrame(points).set_index(["idx"])
                existing_elevations = pd.concat(
                    [existing_elevations, segment_df]
                )
        return existing_elevations

    def _process_segments(
        self,
        segments: List["gpxpy.gpx.GPXTrackSegment"],
        new_workout_id: int,
        new_workout_uuid: "UUID",
        first_point: "gpxpy.gpx.GPXTrackPoint",
    ) -> Tuple[timedelta, float]:
        last_segment_index = len(segments) - 1
        max_speed = 0.0
        previous_segment_last_point_time: Optional["datetime"] = None
        stopped_time_between_segments = timedelta(seconds=0)

        existing_elevations = pd.DataFrame()
        # on workout refresh
        if not self.is_creation and self.workout:
            existing_elevations = self._get_existing_elevations()

            # remove existing segments
            WorkoutSegment.query.filter_by(workout_id=self.workout.id).delete()

        workout_update_missing_elevations = ElevationDataSource.FILE
        segment_idx = 0
        for segment in segments:
            # ignore segments with no distance
            if len(segment.points) < 2:
                continue

            new_workout_segment = WorkoutSegment(
                workout_id=new_workout_id,
                workout_uuid=new_workout_uuid,
            )
            db.session.add(new_workout_segment)

            is_last_segment = segment_idx == last_segment_index
            (
                stopped_time_between_segments,
                previous_segment_last_point_time,
                hr_cadence_power_stats,
                raw_max_speed,
                update_missing_elevations,
            ) = self._process_segment_points(
                segment,
                stopped_time_between_segments,
                previous_segment_last_point_time,
                is_last_segment,
                new_workout_segment,
                first_point,
                existing_elevations,
            )

            if self.change_elevation_source or (
                workout_update_missing_elevations == ElevationDataSource.FILE
                and update_missing_elevations != ElevationDataSource.FILE
            ):
                workout_update_missing_elevations = update_missing_elevations

            self.set_calculated_data(
                parsed_gpx=segment,
                object_to_update=new_workout_segment,
                stopped_time_between_segments=timedelta(seconds=0),
                stopped_speed_threshold=self.stopped_speed_threshold,
                use_raw_gpx_speed=self.auth_user.use_raw_gpx_speed,
                hr_cadence_power_stats=hr_cadence_power_stats,
                raw_max_speed=raw_max_speed,
            )

            if (
                new_workout_segment.max_speed
                and new_workout_segment.max_speed > max_speed
            ):
                max_speed = new_workout_segment.max_speed

            segment_idx += 1

        if self.workout and (
            self.is_creation
            or self.change_elevation_source
            or existing_elevations.empty
        ):
            self.workout.elevation_data_source = (
                workout_update_missing_elevations
            )
        return stopped_time_between_segments, max_speed

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
                    calories = int(extension.text)
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

        stopped_time_between_segments, max_speed = self._process_segments(
            track.segments, self.workout.id, self.workout.uuid, start_point
        )

        hr_cadence_power_stats = self._get_hr_cadence_power_data(
            self.heart_rates, self.cadences, self.powers
        )
        self.set_calculated_data(
            parsed_gpx=track,
            object_to_update=self.workout,
            stopped_time_between_segments=stopped_time_between_segments,
            stopped_speed_threshold=self.stopped_speed_threshold,
            use_raw_gpx_speed=self.auth_user.use_raw_gpx_speed,
            hr_cadence_power_stats=hr_cadence_power_stats,
        )
        self.workout.max_speed = max_speed
        self.workout.best_pace = convert_speed_into_pace_duration(max_speed)
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

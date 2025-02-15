from datetime import datetime, timedelta, timezone
from typing import IO, TYPE_CHECKING, Optional, Union

import gpxpy.gpx

from fittrackee import db

from ...exceptions import WorkoutFileException
from ...models import Workout, WorkoutSegment
from .base_workout_with_segment_service import (
    BaseWorkoutWithSegmentsCreationService,
)
from .workout_point import WorkoutPoint

if TYPE_CHECKING:
    from fittrackee.users.models import User


class WorkoutGpxCreationService(BaseWorkoutWithSegmentsCreationService):
    def __init__(
        self,
        auth_user: "User",
        workout_file: IO[bytes],
        sport_id: int,
        stopped_speed_threshold: float,
    ):
        super().__init__(
            auth_user, workout_file, sport_id, stopped_speed_threshold
        )
        self.gpx: "gpxpy.gpx.GPX" = self.parse_file(workout_file)

    @classmethod
    def parse_file(cls, workout_file: IO[bytes]) -> "gpxpy.gpx.GPX":
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
    def get_calculated_data(
        *,
        parsed_gpx: Union["gpxpy.gpx.GPXTrack", "gpxpy.gpx.GPXTrackSegment"],
        object_to_update: Union["Workout", "WorkoutSegment"],
        stopped_time_between_seg: timedelta,
        stopped_speed_threshold: float,
        use_raw_gpx_speed: bool,
    ) -> Union["Workout", "WorkoutSegment"]:
        moving_data = parsed_gpx.get_moving_data(
            stopped_speed_threshold=stopped_speed_threshold,
            raw=use_raw_gpx_speed,
        )
        if not moving_data:
            raise WorkoutFileException(
                "error", "gpx file is invalid"
            ) from None
        duration = parsed_gpx.get_duration()
        elevation = parsed_gpx.get_elevation_extremes()
        hill = (
            None
            # gpx file does not contain elevation data (<ele> element)
            if elevation.maximum is None
            else parsed_gpx.get_uphill_downhill()
        )

        if isinstance(object_to_update, WorkoutSegment):
            object_to_update.max_speed = (
                (moving_data.max_speed / 1000) * 3600 if moving_data else 0.0
            )
        distance = moving_data.moving_distance + moving_data.stopped_distance
        object_to_update.ave_speed = (
            (
                distance / moving_data.moving_time
                if moving_data.moving_time > 0
                else 0
            )
            / 1000
            * 3600
        )
        object_to_update.descent = None if hill is None else hill.downhill
        object_to_update.duration = (
            timedelta(seconds=duration if duration else 0)
            + stopped_time_between_seg
        )
        object_to_update.distance = distance / 1000
        object_to_update.max_alt = elevation.maximum
        object_to_update.min_alt = elevation.minimum
        object_to_update.moving = timedelta(seconds=moving_data.moving_time)
        object_to_update.pauses = (
            timedelta(seconds=moving_data.stopped_time)
            + stopped_time_between_seg
        )
        object_to_update.ascent = None if hill is None else hill.uphill
        return object_to_update

    def get_workout_date(self) -> "datetime":
        if not self.start_point or not self.start_point.time:
            raise WorkoutFileException(
                "error", "<time> is missing in gpx file"
            )
        return self.start_point.time.astimezone(timezone.utc)

    def _process_file(self) -> "Workout":
        if not self.gpx:
            raise WorkoutFileException(
                "error", "no gpx, please load gpx file before"
            ) from None

        track: "gpxpy.gpx.GPXTrack" = self.gpx.tracks[0]
        start_point = track.segments[0].points[0]
        if start_point.time:
            self.start_point = WorkoutPoint(
                start_point.longitude,
                start_point.latitude,
                start_point.time,
            )
        self.workout_name = track.name
        self.workout_description = track.description

        new_workout = Workout(
            user_id=self.auth_user.id,
            sport_id=self.sport_id,
            workout_date=self.get_workout_date(),
        )
        db.session.add(new_workout)
        db.session.flush()

        segments_nb = len(track.segments)
        max_speed = 0.0
        prev_seg_last_point: Optional[datetime] = None
        no_stopped_time = timedelta(seconds=0)
        stopped_time_between_seg = no_stopped_time

        for segment_idx, segment in enumerate(track.segments):
            new_workout_segment = WorkoutSegment(
                segment_id=segment_idx,
                workout_id=new_workout.id,
                workout_uuid=new_workout.uuid,
            )
            db.session.add(new_workout_segment)

            for point_idx, point in enumerate(segment.points):
                if point_idx == 0:
                    # if a previous segment exists, calculate stopped time
                    # between the two segments
                    if prev_seg_last_point and point.time:
                        stopped_time_between_seg += (
                            point.time - prev_seg_last_point
                        )

                # last segment point
                if point_idx == (len(segment.points) - 1):
                    prev_seg_last_point = point.time

                    # last gpx point
                    if segment_idx == (segments_nb - 1) and point.time:
                        self.end_point = WorkoutPoint(
                            point.longitude,
                            point.latitude,
                            point.time,
                        )
                self.coordinates.append([point.longitude, point.latitude])

            self.get_calculated_data(
                parsed_gpx=segment,
                object_to_update=new_workout_segment,
                stopped_time_between_seg=no_stopped_time,
                stopped_speed_threshold=self.stopped_speed_threshold,
                use_raw_gpx_speed=self.auth_user.use_raw_gpx_speed,
            )
            if (
                new_workout_segment.max_speed
                and new_workout_segment.max_speed > max_speed
            ):
                max_speed = new_workout_segment.max_speed
            db.session.flush()

        self.get_calculated_data(
            parsed_gpx=track,
            object_to_update=new_workout,
            stopped_time_between_seg=stopped_time_between_seg,
            stopped_speed_threshold=self.stopped_speed_threshold,
            use_raw_gpx_speed=self.auth_user.use_raw_gpx_speed,
        )
        new_workout.max_speed = max_speed
        bounds = track.get_bounds()
        new_workout.bounds = (
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

        if self.start_point and self.end_point:
            new_workout.weather_start, new_workout.weather_end = (
                self.get_weather_data(
                    self.start_point,
                    self.end_point,
                )
            )

        db.session.flush()

        return new_workout

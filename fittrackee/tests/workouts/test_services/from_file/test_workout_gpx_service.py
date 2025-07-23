from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict
from unittest.mock import MagicMock, call, patch

import gpxpy
import pytest
from geoalchemy2.shape import to_shape
from shapely import LineString

from fittrackee import db
from fittrackee.tests.fixtures.fixtures_workouts import (
    segment_0_coordinates,
    segment_1_coordinates,
    segment_2_coordinates,
    track_points_part_1_coordinates,
    track_points_part_2_coordinates,
)
from fittrackee.tests.mixins import RandomMixin
from fittrackee.tests.workouts.mixins import (
    WorkoutAssertMixin,
    WorkoutFileMixin,
    WorkoutGpxInfoMixin,
)
from fittrackee.workouts.exceptions import (
    WorkoutExceedingValueException,
    WorkoutFileException,
)
from fittrackee.workouts.models import (
    WORKOUT_VALUES_LIMIT,
    Record,
    Sport,
    Workout,
    WorkoutSegment,
)
from fittrackee.workouts.services import WorkoutGpxService
from fittrackee.workouts.services.workout_from_file.workout_point import (
    WorkoutPoint,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestWorkoutGpxServiceParseFile(RandomMixin, WorkoutFileMixin):
    def test_it_raises_error_when_gpx_file_is_invalid(
        self, app: "Flask", gpx_file_invalid_xml: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing gpx file"
            ),
        ):
            WorkoutGpxService.parse_file(
                self.get_file_content(gpx_file_invalid_xml),
                segments_creation_event="none",
            )

    def test_it_raises_error_when_gpx_file_has_no_tracks(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        gpx_file_wo_track: str,
    ) -> None:
        with (
            pytest.raises(WorkoutFileException, match="no tracks in gpx file"),
        ):
            WorkoutGpxService.parse_file(
                self.get_file_content(gpx_file_wo_track),
                segments_creation_event="none",
            )


class TestWorkoutGpxServiceInstantiation(WorkoutFileMixin):
    def test_it_instantiates_service(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        gpx_file: str,
    ) -> None:
        service = WorkoutGpxService(
            user_1,
            self.get_file_content(gpx_file),
            sport_1_cycling.id,
            sport_1_cycling.stopped_speed_threshold,
        )

        # from BaseWorkoutService
        assert service.auth_user == user_1
        assert service.sport_id == sport_1_cycling.id
        # from BaseWorkoutWithSegmentsCreationService
        assert service.coordinates == []
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.workout_name is None
        assert service.workout_description is None
        assert service.start_point is None
        assert service.end_point is None
        # from WorkoutGpxService
        assert isinstance(service.gpx, gpxpy.gpx.GPX)


class TestWorkoutGpxServiceGetWeatherData:
    def test_it_calls_weather_service(
        self, default_weather_service: MagicMock
    ) -> None:
        start_point = WorkoutPoint(
            6.07367,
            44.68095,
            datetime(2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc),
        )
        end_point = WorkoutPoint(
            6.07442,
            44.67822,
            datetime(2018, 3, 13, 12, 48, 55, tzinfo=timezone.utc),
        )

        WorkoutGpxService.get_weather_data(start_point, end_point)

        default_weather_service.assert_has_calls(
            [
                call(start_point),
                call(end_point),
            ]
        )


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutGpxServiceProcessFile(
    WorkoutGpxInfoMixin, WorkoutFileMixin, WorkoutAssertMixin
):
    @staticmethod
    def assert_workout_records(workout: "Workout") -> None:
        """
        assert workout segment data from 'gpx_file' fixture
        """
        records = Record.query.order_by(Record.record_type.asc()).all()
        assert len(records) == 5
        assert records[0].serialize() == {
            "id": 1,
            "record_type": "AS",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.ave_speed),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[1].serialize() == {
            "id": 2,
            "record_type": "FD",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.distance),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[2].serialize() == {
            "id": 3,
            "record_type": "HA",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.ascent),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[3].serialize() == {
            "id": 4,
            "record_type": "LD",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": str(workout.duration),
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[4].serialize() == {
            "id": 5,
            "record_type": "MS",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.max_speed),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }

    def init_service_with_gpx(
        self,
        user: "User",
        sport: "Sport",
        gpx_content: str,
        get_weather: bool = True,
    ) -> "WorkoutGpxService":
        return WorkoutGpxService(
            user,
            self.get_file_content(gpx_content),
            sport.id,
            sport.stopped_speed_threshold,
            get_weather=get_weather,
        )

    def test_it_raises_error_when_first_point_has_no_time(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        gpx_file_without_time: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_time
        )

        with pytest.raises(
            WorkoutFileException, match="<time> is missing in gpx file"
        ):
            service.process_workout()

    @pytest.mark.parametrize(
        "input_key",
        [
            "ascent",
            "descent",
            "distance",
            "moving_time",
            "max_speed",
            "max_alt",
            "min_alt",
        ],
    )
    def test_it_raises_error_when_gpx_info_exceeds_limit(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        gpx_file: str,
        input_key: str,
    ) -> None:
        service = self.init_service_with_gpx(user_1, sport_1_cycling, gpx_file)
        max_value = WORKOUT_VALUES_LIMIT[input_key]

        with (
            patch.object(
                WorkoutGpxService,
                "get_gpx_info",
                return_value=self.generate_get_gpx_info_return_value(
                    {input_key: max_value + 0.001}
                ),
            ),
            pytest.raises(
                WorkoutExceedingValueException,
                match=(
                    "one or more values, entered or calculated, "
                    "exceed the limits"
                ),
            ),
        ):
            service.process_workout()

    def test_it_creates_workout_and_segment_when_gpx_file_has_one_segment(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file: str,
    ) -> None:
        service = self.init_service_with_gpx(user_1, sport_1_cycling, gpx_file)

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.source is None
        workout_segment = workout.segments[0]
        coordinates = (
            track_points_part_1_coordinates + track_points_part_2_coordinates
        )
        assert to_shape(workout_segment.geom) == LineString(coordinates)
        assert len(workout_segment.points) == len(coordinates)
        assert workout_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_and_segment_when_gpx_file_has_offset(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_offset: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_offset
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.source is None
        workout_segment = workout.segments[0]
        coordinates = (
            track_points_part_1_coordinates + track_points_part_2_coordinates
        )
        assert to_shape(workout_segment.geom) == LineString(coordinates)
        assert len(workout_segment.points) == len(coordinates)
        assert workout_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_and_segment_when_raw_speed_is_true(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1_raw_speed: "User",
        gpx_file: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1_raw_speed, sport_1_cycling, gpx_file
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        # workout
        workout = Workout.query.one()
        assert float(workout.ave_speed) == 4.61
        assert float(workout.max_speed) == 5.25
        # workout segment
        workout_segment = WorkoutSegment.query.one()
        assert float(workout_segment.ave_speed) == 4.61
        assert float(workout_segment.max_speed) == 5.25
        assert workout.source is None
        workout_segment = workout.segments[0]
        coordinates = (
            track_points_part_1_coordinates + track_points_part_2_coordinates
        )
        assert to_shape(workout_segment.geom) == LineString(coordinates)
        assert len(workout_segment.points) == len(coordinates)
        assert workout_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_and_segment_when_gpx_file_has_no_elevation(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        # workout
        workout = Workout.query.one()
        assert workout.duration == timedelta(minutes=4, seconds=10)
        assert workout.ascent is None
        assert float(workout.ave_speed) == 4.57
        assert workout.descent is None
        assert float(workout.distance) == 0.317
        assert workout.max_alt is None
        assert float(workout.max_speed) == 5.1
        assert workout.min_alt is None
        assert workout.moving == timedelta(minutes=4, seconds=10)
        assert workout.pauses == timedelta(seconds=0)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.source is None
        # workout segment
        workout_segment = WorkoutSegment.query.one()
        assert workout_segment.duration == timedelta(minutes=4, seconds=10)
        assert workout_segment.ascent is None
        assert float(workout_segment.ave_speed) == 4.57
        assert workout_segment.descent is None
        assert float(workout_segment.distance) == 0.317
        assert workout_segment.max_alt is None
        assert float(workout_segment.max_speed) == 5.1
        assert workout_segment.min_alt is None
        assert workout_segment.moving == timedelta(minutes=4, seconds=10)
        assert workout_segment.pauses == timedelta(seconds=0)
        assert workout_segment.ave_cadence is None
        assert workout_segment.ave_hr is None
        assert workout_segment.max_cadence is None
        assert workout_segment.max_hr is None
        coordinates = (
            track_points_part_1_coordinates + track_points_part_2_coordinates
        )
        assert to_shape(workout_segment.geom) == LineString(coordinates)
        assert len(workout_segment.points) == len(coordinates)
        assert workout_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": None,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 317.15294405358054,
            "duration": 250,
            "elevation": None,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.22,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_and_segments_when_gpx_file_contains_3_segments(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_3_segments: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_3_segments
        )

        service.process_workout()
        db.session.commit()

        # no description in gpx file, only name is present
        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        # workout
        workout = Workout.query.one()
        assert workout.user_id == user_1.id
        assert workout.sport_id == sport_1_cycling.id
        assert workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 50, tzinfo=timezone.utc
        )
        assert float(workout.ascent) == 0.0
        assert float(workout.ave_speed) == 6.6
        assert workout.bounds == [44.67837, 6.07364, 44.68095, 6.07435]
        assert float(workout.descent) == 6.0
        assert float(workout.distance) == 0.055
        assert workout.duration == timedelta(minutes=2, seconds=30)
        assert float(workout.max_alt) == 998.0
        assert float(workout.max_speed) == 13.83
        assert float(workout.min_alt) == 979.0
        assert workout.moving == timedelta(seconds=30)
        assert workout.pauses == timedelta(minutes=2)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.source is None
        # workout segments
        workout_segments = WorkoutSegment.query.all()
        assert len(workout_segments) == 3
        # first workout segment
        assert workout_segments[0].workout_id == workout.id
        assert workout_segments[0].workout_uuid == workout.uuid
        assert workout_segments[0].segment_id == 0
        assert float(workout_segments[0].ascent) == 0.0
        assert float(workout_segments[0].ave_speed) == 6.32
        assert float(workout_segments[0].descent) == 4.0
        assert float(workout_segments[0].distance) == 0.018
        assert workout_segments[0].duration == timedelta(seconds=10)
        assert float(workout_segments[0].max_alt) == 998.0
        assert float(workout_segments[0].max_speed) == 9.43
        assert float(workout_segments[0].min_alt) == 994.0
        assert workout_segments[0].moving == timedelta(seconds=10)
        assert workout_segments[0].pauses == timedelta(seconds=0)
        assert workout_segments[0].ave_cadence is None
        assert workout_segments[0].ave_hr is None
        assert workout_segments[0].max_cadence is None
        assert workout_segments[0].max_hr is None
        assert to_shape(workout_segments[0].geom) == LineString(
            segment_0_coordinates
        )
        assert len(workout_segments[0].points) == len(segment_0_coordinates)
        assert workout_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "2018-03-13 12:44:50+00:00",
        }
        assert workout_segments[0].points[-1] == {
            "distance": 17.551714568218248,
            "duration": 10,
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
            "speed": 9.43,
            "time": "2018-03-13 12:45:00+00:00",
        }
        # second workout segment
        assert workout_segments[1].workout_id == workout.id
        assert workout_segments[1].workout_uuid == workout.uuid
        assert workout_segments[1].segment_id == 1
        assert float(workout_segments[1].ascent) == 0
        assert float(workout_segments[1].ave_speed) == 4.54
        assert float(workout_segments[1].descent) == 1.0
        assert float(workout_segments[1].distance) == 0.013
        assert workout_segments[1].duration == timedelta(seconds=10)
        assert float(workout_segments[1].max_alt) == 987.0
        assert float(workout_segments[1].max_speed) == 4.84
        assert float(workout_segments[1].min_alt) == 986.0
        assert workout_segments[1].moving == timedelta(seconds=10)
        assert workout_segments[1].pauses == timedelta(seconds=0)
        assert workout_segments[1].ave_cadence is None
        assert workout_segments[1].ave_hr is None
        assert workout_segments[1].max_cadence is None
        assert workout_segments[1].max_hr is None
        assert to_shape(workout_segments[1].geom) == LineString(
            segment_1_coordinates
        )
        assert len(workout_segments[1].points) == len(segment_1_coordinates)
        assert workout_segments[1].points[0] == {
            "distance": 0.0,
            "duration": 70,
            "elevation": 987.0,
            "latitude": 44.67972,
            "longitude": 6.07367,
            "speed": 4.84,
            "time": "2018-03-13 12:46:00+00:00",
        }
        assert workout_segments[1].points[-1] == {
            "distance": 12.598402521897194,
            "duration": 80,
            "elevation": 986.0,
            "latitude": 44.67961,
            "longitude": 6.0737,
            "speed": 4.23,
            "time": "2018-03-13 12:46:10+00:00",
        }
        # third workout segment
        assert workout_segments[2].workout_id == workout.id
        assert workout_segments[2].workout_uuid == workout.uuid
        assert workout_segments[2].segment_id == 2
        assert float(workout_segments[2].ascent) == 0.0
        assert float(workout_segments[2].ave_speed) == 8.94
        assert float(workout_segments[2].descent) == 1.0
        assert float(workout_segments[2].distance) == 0.025
        assert workout_segments[2].duration == timedelta(seconds=10)
        assert float(workout_segments[2].max_alt) == 980.0
        assert float(workout_segments[2].max_speed) == 13.83
        assert float(workout_segments[2].min_alt) == 979.0
        assert workout_segments[2].moving == timedelta(seconds=10)
        assert workout_segments[2].pauses == timedelta(seconds=0)
        assert workout_segments[2].ave_cadence is None
        assert workout_segments[2].ave_hr is None
        assert workout_segments[2].max_cadence is None
        assert workout_segments[2].max_hr is None
        assert to_shape(workout_segments[2].geom) == LineString(
            segment_2_coordinates
        )
        assert len(workout_segments[2].points) == len(segment_2_coordinates)
        assert workout_segments[2].points[0] == {
            "distance": 0.0,
            "duration": 140,
            "elevation": 980.0,
            "latitude": 44.67858,
            "longitude": 6.07425,
            "speed": 13.83,
            "time": "2018-03-13 12:47:10+00:00",
        }
        assert workout_segments[2].points[-1] == {
            "distance": 24.83101225255615,
            "duration": 150,
            "elevation": 979.0,
            "latitude": 44.67837,
            "longitude": 6.07435,
            "speed": 4.05,
            "time": "2018-03-13 12:47:20+00:00",
        }

    def test_it_creates_workout_when_gpx_file_contains_microseconds(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_microseconds: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_microseconds
        )

        service.process_workout()
        db.session.commit()

        # workout
        workout = Workout.query.one()
        assert workout.duration == timedelta(minutes=4, seconds=10)
        assert workout.moving == timedelta(minutes=3, seconds=55)
        assert workout.pauses == timedelta(seconds=14)
        # workout segments
        workout_segments = WorkoutSegment.query.all()
        assert len(workout_segments) == 2
        assert workout_segments[0].duration == timedelta(minutes=1, seconds=30)
        assert workout_segments[0].moving == timedelta(minutes=1, seconds=30)
        assert workout_segments[0].pauses == timedelta(seconds=0)
        assert workout_segments[1].duration == timedelta(minutes=2, seconds=25)
        assert workout_segments[1].moving == timedelta(minutes=2, seconds=25)
        assert workout_segments[1].pauses == timedelta(seconds=0)

    def test_it_creates_workout_and_segments_when_one_segment_has_no_distance(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_zero_distance_segment: str,
    ) -> None:
        # gpx with 3 segments
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_zero_distance_segment
        )

        service.process_workout()
        db.session.commit()

        # no description in gpx file, only name is present
        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        # workout
        workout = Workout.query.one()
        assert workout.user_id == user_1.id
        assert workout.sport_id == sport_1_cycling.id
        assert workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 50, tzinfo=timezone.utc
        )
        assert float(workout.ascent) == 0.0
        assert float(workout.ave_speed) == 7.63
        assert workout.bounds == [44.67837, 6.07364, 44.68095, 6.07435]
        assert float(workout.descent) == 5.0
        assert float(workout.distance) == 0.042
        assert workout.duration == timedelta(minutes=2, seconds=30)
        assert float(workout.max_alt) == 998.0
        assert float(workout.max_speed) == 13.83
        assert float(workout.min_alt) == 979.0
        assert workout.moving == timedelta(seconds=20)
        assert workout.pauses == timedelta(minutes=2, seconds=10)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.source is None
        # workout segments
        workout_segments = WorkoutSegment.query.all()
        assert len(workout_segments) == 2
        # first workout segment
        assert workout_segments[0].workout_id == workout.id
        assert workout_segments[0].workout_uuid == workout.uuid
        assert workout_segments[0].segment_id == 0
        assert float(workout_segments[0].ascent) == 0.0
        assert float(workout_segments[0].ave_speed) == 6.32
        assert float(workout_segments[0].descent) == 4.0
        assert float(workout_segments[0].distance) == 0.018
        assert workout_segments[0].duration == timedelta(seconds=10)
        assert float(workout_segments[0].max_alt) == 998.0
        assert float(workout_segments[0].max_speed) == 9.43
        assert float(workout_segments[0].min_alt) == 994.0
        assert workout_segments[0].moving == timedelta(seconds=10)
        assert workout_segments[0].pauses == timedelta(seconds=0)
        assert to_shape(workout_segments[0].geom) == LineString(
            segment_0_coordinates
        )
        assert len(workout_segments[0].points) == len(segment_0_coordinates)
        assert workout_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": "2018-03-13 12:44:50+00:00",
        }
        assert workout_segments[0].points[-1] == {
            "distance": 17.551714568218248,
            "duration": 10,
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
            "speed": 9.43,
            "time": "2018-03-13 12:45:00+00:00",
        }
        # second workout segment
        assert workout_segments[1].workout_id == workout.id
        assert workout_segments[1].workout_uuid == workout.uuid
        assert workout_segments[1].segment_id == 2
        assert float(workout_segments[1].ascent) == 0.0
        assert float(workout_segments[1].ave_speed) == 8.94
        assert float(workout_segments[1].descent) == 1.0
        assert float(workout_segments[1].distance) == 0.025
        assert workout_segments[1].duration == timedelta(seconds=10)
        assert float(workout_segments[1].max_alt) == 980.0
        assert float(workout_segments[1].max_speed) == 13.83
        assert float(workout_segments[1].min_alt) == 979.0
        assert workout_segments[1].moving == timedelta(seconds=10)
        assert workout_segments[1].pauses == timedelta(seconds=0)
        assert to_shape(workout_segments[1].geom) == LineString(
            segment_2_coordinates
        )
        assert len(workout_segments[1].points) == len(segment_2_coordinates)
        assert workout_segments[1].points[0] == {
            "distance": 0.0,
            "duration": 140,
            "elevation": 980.0,
            "latitude": 44.67858,
            "longitude": 6.07425,
            "speed": 13.83,
            "time": "2018-03-13 12:47:10+00:00",
        }
        assert workout_segments[1].points[-1] == {
            "distance": 24.83101225255615,
            "duration": 150,
            "elevation": 979.0,
            "latitude": 44.67837,
            "longitude": 6.07435,
            "speed": 4.05,
            "time": "2018-03-13 12:47:20+00:00",
        }

        serialized_segment = workout_segments[1].serialize()
        assert serialized_segment == {
            "ascent": 0.0,
            "ave_cadence": None,
            "ave_hr": None,
            "ave_power": None,
            "ave_speed": 8.94,
            "descent": 1.0,
            "distance": 0.025,
            "duration": "0:00:10",
            "max_alt": 980.0,
            "max_cadence": None,
            "max_hr": None,
            "max_power": None,
            "max_speed": 13.83,
            "min_alt": 979.0,
            "moving": "0:00:10",
            "pauses": None,
            "segment_id": 2,
            "workout_id": workout.short_id,
        }

    def test_it_creates_workout_when_gpx_file_has_gpxtpx_extensions(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_gpxtpx_extensions: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_gpxtpx_extensions
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        assert workout.ave_cadence == 52
        assert workout.ave_power == 248
        assert workout.ave_hr == 85
        assert workout.max_cadence == 57
        assert workout.max_hr == 92
        assert workout.max_power == 326
        assert workout.source == "Garmin Connect"

    def test_it_creates_workout_when_gpx_file_has_gpxtpx_extensions_and_power(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_gpxtpx_extensions_and_power: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_gpxtpx_extensions_and_power
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_with_with_gpxtpx_extensions_and_power(workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        assert workout.ave_cadence == 52
        assert workout.ave_hr == 85
        assert workout.ave_power == 248
        assert workout.max_cadence == 57
        assert workout.max_hr == 92
        assert workout.max_power == 326
        assert workout.source == "Garmin Connect"
        assert workout.segments[0].points[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "heart_rate": 92,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "power": 0,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_creates_workout_when_gpx_file_has_cadence_float_value(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_cadence_float_value: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_cadence_float_value
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        assert workout.ave_cadence == 52
        assert workout.ave_hr == 85
        assert workout.ave_power == 248
        assert workout.max_cadence == 57
        assert workout.max_hr == 92
        assert workout.max_power == 326
        assert workout.source == "Garmin Connect"
        assert workout.segments[0].points[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "heart_rate": 92,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "power": 0,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_creates_workout_when_gpx_file_has_cadence_zero_values(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_cadence_zero_values: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_cadence_zero_values
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        workout_segment = WorkoutSegment.query.one()
        self.assert_workout_segment(workout, workout_segment)
        self.assert_workout_records(workout)
        assert workout.ave_cadence is None
        assert workout.ave_hr == 85
        assert workout.max_cadence is None
        assert workout.max_hr == 92
        assert workout.source == "Garmin Connect"
        assert workout_segment.ave_cadence is None
        assert workout_segment.ave_hr == 85
        assert workout_segment.max_cadence is None
        assert workout_segment.max_hr == 92
        assert workout.segments[0].points[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "heart_rate": 92,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "power": 0,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_creates_workout_when_gpx_file_has_ns3_extensions(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_ns3_extensions: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_ns3_extensions
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        assert workout.ave_cadence == 52
        assert workout.ave_hr == 85
        assert workout.ave_power == 248
        assert workout.max_cadence == 57
        assert workout.max_hr == 92
        assert workout.max_power == 326
        assert workout.source == "Garmin Connect"
        assert workout.segments[0].points[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "heart_rate": 92,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "power": 0,
            "speed": 3.21,
            "time": "2018-03-13 12:44:45+00:00",
        }

    @pytest.mark.parametrize("input_get_weather", [{}, {"get_weather": True}])
    def test_it_calls_weather_service_for_start_and_endpoint(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_segments: str,
        default_weather_service: MagicMock,
        input_get_weather: Dict,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_with_segments,
            **input_get_weather,
        )

        service.process_workout()
        db.session.commit()

        default_weather_service.assert_has_calls(
            [
                call(
                    WorkoutPoint(
                        *track_points_part_1_coordinates[0],
                        service.start_point.time,  # type: ignore
                    )
                ),
                call(
                    WorkoutPoint(
                        *track_points_part_2_coordinates[-1],
                        service.end_point.time,  # type: ignore
                    )
                ),
            ]
        )

    def test_it_does_not_call_weather_service_when_flag_is_false(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_segments: str,
        default_weather_service: MagicMock,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_segments, get_weather=False
        )

        service.process_workout()
        db.session.commit()

        default_weather_service.assert_not_called()

    def test_it_processes_file_when_file_contains_description(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1_raw_speed: "User",
        gpx_file_with_description: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1_raw_speed, sport_1_cycling, gpx_file_with_description
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description == "this is workout description"
        assert service.workout_name == "just a workout"

    def test_it_processes_file_when_file_does_not_contain_name(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1_raw_speed: "User",
        gpx_file_wo_name: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1_raw_speed, sport_1_cycling, gpx_file_wo_name
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None

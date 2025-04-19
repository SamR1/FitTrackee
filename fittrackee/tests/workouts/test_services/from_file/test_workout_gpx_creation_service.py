from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import IO, TYPE_CHECKING
from unittest.mock import MagicMock, call, patch

import gpxpy
import pytest
from werkzeug.datastructures import FileStorage

from fittrackee import db
from fittrackee.tests.fixtures.fixtures_workouts import (
    track_points_part_1_coordinates,
    track_points_part_2_coordinates,
)
from fittrackee.tests.mixins import RandomMixin
from fittrackee.tests.workouts.mixins import WorkoutGpxInfoMixin
from fittrackee.visibility_levels import VisibilityLevel
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
from fittrackee.workouts.services import WorkoutGpxCreationService
from fittrackee.workouts.services.workout_from_file.workout_point import (
    WorkoutPoint,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class WorkoutGpxCreationServiceTestCase:
    @staticmethod
    def get_file_storage(
        content: str, file_name: str = "file.gpx"
    ) -> "FileStorage":
        return FileStorage(
            filename=file_name, stream=BytesIO(str.encode(content))
        )

    @staticmethod
    def get_file_content(content: str) -> IO[bytes]:
        return BytesIO(str.encode(content))


class TestWorkoutGpxCreationServiceParseFile(
    RandomMixin, WorkoutGpxCreationServiceTestCase
):
    def test_it_raises_error_when_gpx_file_is_invalid(
        self, app: "Flask", gpx_file_invalid_xml: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing gpx file"
            ),
        ):
            WorkoutGpxCreationService.parse_file(
                self.get_file_content(gpx_file_invalid_xml)
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
            WorkoutGpxCreationService.parse_file(
                self.get_file_content(gpx_file_wo_track)
            )


class TestWorkoutGpxCreationServiceInstantiation(
    WorkoutGpxCreationServiceTestCase
):
    def test_it_instantiates_service(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        gpx_file: str,
    ) -> None:
        service = WorkoutGpxCreationService(
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
        # from WorkoutGpxCreationService
        assert isinstance(service.gpx, gpxpy.gpx.GPX)


class TestWorkoutGpxCreationServiceGetWeatherData:
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

        WorkoutGpxCreationService.get_weather_data(start_point, end_point)

        default_weather_service.assert_has_calls(
            [
                call(start_point),
                call(end_point),
            ]
        )


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutGpxCreationServiceProcessFile(
    WorkoutGpxInfoMixin, WorkoutGpxCreationServiceTestCase
):
    @staticmethod
    def assert_workout(
        user: "User", sport: "Sport", workout: "Workout"
    ) -> None:
        """
        assert workout data from 'gpx_file' fixture
        """
        assert workout.analysis_visibility == VisibilityLevel.PRIVATE
        assert float(workout.ascent) == 0.4  # type: ignore
        assert float(workout.ave_speed) == 4.61  # type: ignore
        assert workout.bounds == [44.67822, 6.07355, 44.68095, 6.07442]
        assert workout.creation_date is not None
        assert float(workout.descent) == 23.4  # type: ignore
        assert workout.description is None
        assert float(workout.distance) == 0.32  # type: ignore
        assert workout.duration == timedelta(minutes=4, seconds=10)
        assert workout.gpx is None
        assert workout.map is None
        assert workout.map_id is None
        assert workout.map_visibility == VisibilityLevel.PRIVATE
        assert float(workout.max_alt) == 998.0  # type: ignore
        assert float(workout.max_speed) == 5.12  # type: ignore
        assert float(workout.min_alt) == 975.0  # type: ignore
        assert workout.modification_date is not None
        assert workout.moving == timedelta(minutes=4, seconds=10)
        assert workout.notes is None
        assert workout.pauses == timedelta(seconds=0)
        assert workout.sport_id == sport.id
        assert workout.suspended_at is None
        assert workout.title is None
        assert workout.user_id == user.id
        assert workout.weather_start is None
        assert workout.weather_end is None
        assert workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
        )
        assert workout.workout_visibility == VisibilityLevel.PRIVATE

    @staticmethod
    def assert_workout_segment(workout: "Workout") -> None:
        """
        assert workout segment data from 'gpx_file' fixture
        """
        assert WorkoutSegment.query.count() == 1
        workout_segment = WorkoutSegment.query.one()
        assert workout_segment.workout_id == workout.id
        assert workout_segment.workout_uuid == workout.uuid
        assert workout_segment.segment_id == 0
        assert float(workout_segment.ascent) == 0.4
        assert float(workout_segment.ave_speed) == 4.61
        assert float(workout_segment.descent) == 23.4
        assert float(workout_segment.distance) == 0.32
        assert workout_segment.duration == timedelta(minutes=4, seconds=10)
        assert float(workout_segment.max_alt) == 998.0
        assert float(workout_segment.max_speed) == 5.12
        assert float(workout_segment.min_alt) == 975.0
        assert workout_segment.moving == timedelta(minutes=4, seconds=10)
        assert workout_segment.pauses == timedelta(seconds=0)

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
    ) -> "WorkoutGpxCreationService":
        return WorkoutGpxCreationService(
            user,
            self.get_file_content(gpx_content),
            sport.id,
            sport.stopped_speed_threshold,
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
                WorkoutGpxCreationService,
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

    def test_it_calls_weather_service_for_start_and_endpoint(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_segments: str,
        default_weather_service: MagicMock,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_segments
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

import re
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict, Optional
from unittest.mock import MagicMock, call, patch

import gpxpy
import pytest
import requests
from geoalchemy2.shape import to_shape
from shapely import LineString, Point

from fittrackee import db
from fittrackee.constants import ElevationDataSource
from fittrackee.tests.fixtures.fixtures_workouts import (
    OPEN_ELEVATION_RESPONSE,
    VALHALLA_RESPONSE,
    VALHALLA_VALUES,
    segment_0_coordinates,
    segment_1_coordinates,
    segment_2_coordinates,
    track_points_part_1_coordinates,
    track_points_part_2_coordinates,
)
from fittrackee.tests.mixins import RandomMixin, ResponseMockMixin
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
from fittrackee.workouts.services.elevation.open_elevation_service import (
    OpenElevationService,
)
from fittrackee.workouts.services.elevation.valhalla_elevation_service import (
    ValhallaElevationService,
)
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
            sport_1_cycling,
            sport_1_cycling.stopped_speed_threshold,
        )

        # from BaseWorkoutWithSegmentsCreationService
        assert service.auth_user == user_1
        assert service.sport == sport_1_cycling
        assert service.coordinates == []
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.workout_name is None
        assert service.workout_description is None
        assert service.start_point is None
        assert service.end_point is None
        assert service.workout is None
        assert service.is_creation is True
        assert service.get_weather is True
        assert service.get_elevation_on_refresh is True
        assert service.change_elevation_source is None
        # from WorkoutGpxService
        assert isinstance(service.gpx, gpxpy.gpx.GPX)

    def test_it_instantiates_service_with_all_parameters(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        gpx_file: str,
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = WorkoutGpxService(
            user_1,
            self.get_file_content(gpx_file),
            sport_1_cycling,
            sport_1_cycling.stopped_speed_threshold,
            False,
            True,
            workout_cycling_user_1,
            ElevationDataSource.FILE,
        )

        # from BaseWorkoutWithSegmentsCreationService
        assert service.auth_user == user_1
        assert service.sport == sport_1_cycling
        assert service.coordinates == []
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.workout_name is None
        assert service.workout_description is None
        assert service.start_point is None
        assert service.end_point is None
        assert service.workout == workout_cycling_user_1
        assert service.is_creation is False
        assert service.get_weather is False
        assert service.get_elevation_on_refresh is True
        assert service.change_elevation_source is ElevationDataSource.FILE
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
class WorkoutGpxServiceProcessFileTestCase(
    WorkoutGpxInfoMixin,
    WorkoutFileMixin,
    WorkoutAssertMixin,
    ResponseMockMixin,
):
    @staticmethod
    def assert_workout_records(workout: "Workout") -> None:
        """
        assert workout segment data from 'gpx_file' fixture
        """
        records = Record.query.order_by(Record.record_type.asc()).all()
        assert len(records) == 7
        assert records[0].serialize() == {
            "id": 1,
            "record_type": "AP",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": str(workout.ave_pace),
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[1].serialize() == {
            "id": 2,
            "record_type": "AS",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.ave_speed),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[2].serialize() == {
            "id": 3,
            "record_type": "BP",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": str(workout.best_pace),
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[3].serialize() == {
            "id": 4,
            "record_type": "FD",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.distance),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[4].serialize() == {
            "id": 5,
            "record_type": "HA",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.ascent),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[5].serialize() == {
            "id": 6,
            "record_type": "LD",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": str(workout.duration),
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[6].serialize() == {
            "id": 7,
            "record_type": "MS",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": float(workout.max_speed),  # type: ignore
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }

    @staticmethod
    def assert_workout_with_two_segments(user: "User", sport: "Sport") -> None:
        # workout
        workout = Workout.query.one()
        assert to_shape(workout.start_point_geom) == Point(
            segment_0_coordinates[0]
        )
        assert workout.user_id == user.id
        assert workout.sport_id == sport.id
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
        assert workout.elevation_data_source == (ElevationDataSource.FILE)
        assert workout.source is None
        assert workout.ave_pace == timedelta(minutes=7, seconds=52)
        assert workout.best_pace == timedelta(minutes=4, seconds=20)
        # workout segments
        workout_segments = WorkoutSegment.query.all()
        assert len(workout_segments) == 2
        # first workout segment
        assert workout_segments[0].workout_id == workout.id
        assert workout_segments[0].workout_uuid == workout.uuid
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
        assert workout_segments[0].ave_pace == timedelta(minutes=9, seconds=30)
        assert workout_segments[0].best_pace == timedelta(
            minutes=6, seconds=22
        )
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
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:50+00:00",
        }
        assert workout_segments[0].points[-1] == {
            "distance": 17.551714568218248,
            "duration": 10,
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
            "pace": 0.3817603393,
            "speed": 9.43,
            "time": "2018-03-13 12:45:00+00:00",
        }
        # second workout segment
        assert workout_segments[1].workout_id == workout.id
        assert workout_segments[1].workout_uuid == workout.uuid
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
        assert workout_segments[1].ave_pace == timedelta(minutes=6, seconds=43)
        assert workout_segments[1].best_pace == timedelta(
            minutes=4, seconds=20
        )
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
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:47:10+00:00",
        }
        assert workout_segments[1].points[-1] == {
            "distance": 24.83101225255615,
            "duration": 150,
            "elevation": 979.0,
            "latitude": 44.67837,
            "longitude": 6.07435,
            "pace": 0.8888888889,
            "speed": 4.05,
            "time": "2018-03-13 12:47:20+00:00",
        }

        serialized_segment = workout_segments[1].serialize()
        assert serialized_segment == {
            "ascent": 0.0,
            "ave_cadence": None,
            "ave_hr": None,
            "ave_pace": None,
            "ave_power": None,
            "ave_speed": 8.94,
            "best_pace": None,
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
            "segment_id": workout_segments[1].short_id,
            "workout_id": workout.short_id,
        }

    @staticmethod
    def assert_workout_without_elevation() -> None:
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
        assert workout_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": None,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 317.15294405358054,
            "duration": 250,
            "elevation": None,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.8530805687,
            "speed": 4.22,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def init_service_with_gpx(
        self,
        user: "User",
        sport: "Sport",
        gpx_content: str,
        get_weather: bool = True,
        get_elevation_on_refresh: Optional[bool] = None,
        workout: Optional["Workout"] = None,
        change_elevation_source: Optional["ElevationDataSource"] = None,
    ) -> "WorkoutGpxService":
        return WorkoutGpxService(
            user,
            self.get_file_content(gpx_content),
            sport,
            sport.stopped_speed_threshold,
            get_weather=get_weather,
            **(
                {}  # type: ignore[arg-type]
                if get_elevation_on_refresh is None
                else {"get_elevation_on_refresh": get_elevation_on_refresh}
            ),
            workout=workout,
            change_elevation_source=change_elevation_source,
        )


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutGpxServiceProcessFileOnCreation(
    WorkoutGpxServiceProcessFileTestCase
):
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

    def test_it_raises_error_file_has_no_valid_segments(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        gpx_file = """<?xml version='1.0' encoding='UTF-8'?>
<gpx
  xmlns:gpxdata="http://www.cluetrust.com/XML/GPXDATA/1/0"
  xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
  xmlns:gpxext="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
  xmlns="http://www.topografix.com/GPX/1/1"
>
  <metadata/>
  <trk>
    <trkseg>
    </trkseg>
    <trkseg>
    </trkseg>
  </trk>
</gpx>
"""
        service = self.init_service_with_gpx(user_1, sport_1_cycling, gpx_file)

        with (
            pytest.raises(
                WorkoutFileException, match="no valid segments in file"
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
        assert to_shape(workout.start_point_geom) == Point(
            track_points_part_1_coordinates[0]
        )
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
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
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
        assert to_shape(workout.start_point_geom) == Point(
            track_points_part_1_coordinates[0]
        )
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
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_and_segment_when_raw_speed_is_true(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1_raw_speed: "User",
        gpx_file_with_3_segments: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1_raw_speed, sport_1_cycling, gpx_file_with_3_segments
        )

        service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        # workout
        workout = Workout.query.one()
        assert to_shape(workout.start_point_geom) == Point(
            segment_0_coordinates[0]
        )
        assert float(workout.ascent) == 0.0
        assert float(workout.ave_speed) == 6.6
        assert float(workout.descent) == 6.0
        assert float(workout.distance) == 0.055
        assert workout.duration == timedelta(minutes=2, seconds=30)
        assert float(workout.max_alt) == 998.0
        assert float(workout.max_speed) == 9.43
        assert float(workout.min_alt) == 979.0
        assert workout.moving == timedelta(seconds=30)
        assert workout.pauses == timedelta(minutes=2)
        # workout segments
        workout_segments = WorkoutSegment.query.all()
        assert len(workout_segments) == 3
        # first workout segment
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
        assert workout_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:50+00:00",
        }
        assert workout_segments[0].points[-1] == {
            "distance": 17.551714568218248,
            "duration": 10,
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
            "pace": 0.3817603393,
            "speed": 9.43,
            "time": "2018-03-13 12:45:00+00:00",
        }
        # third workout segment
        assert float(workout_segments[2].ascent) == 0.0
        assert float(workout_segments[2].ave_speed) == 8.94
        assert float(workout_segments[2].descent) == 1.0
        assert float(workout_segments[2].distance) == 0.025
        assert workout_segments[2].duration == timedelta(seconds=10)
        assert float(workout_segments[2].max_alt) == 980.0
        assert float(workout_segments[2].max_speed) == 8.94
        assert float(workout_segments[2].min_alt) == 979.0
        assert workout_segments[2].moving == timedelta(seconds=10)
        assert workout_segments[2].pauses == timedelta(seconds=0)
        assert workout_segments[2].points[0] == {
            "distance": 0.0,
            "duration": 140,
            "elevation": 980.0,
            "latitude": 44.67858,
            "longitude": 6.07425,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:47:10+00:00",
        }
        assert workout_segments[2].points[-1] == {
            "distance": 24.83101225255615,
            "duration": 150,
            "elevation": 979.0,
            "latitude": 44.67837,
            "longitude": 6.07435,
            "pace": 0.8888888889,
            "speed": 4.05,
            "time": "2018-03-13 12:47:20+00:00",
        }

    def test_it_does_not_call_open_elevation_service_when_file_has_no_missing_elevations(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file: str,
    ) -> None:
        service = self.init_service_with_gpx(user_1, sport_1_cycling, gpx_file)

        with (
            patch.object(
                OpenElevationService, "get_elevations"
            ) as get_elevations_mock,
        ):
            service.process_workout()

        get_elevations_mock.assert_not_called()

    @pytest.mark.parametrize(
        "input_missing_elevations_processing, expected_kwargs",
        [
            (ElevationDataSource.OPEN_ELEVATION, {"smooth": False}),
            (
                ElevationDataSource.OPEN_ELEVATION_SMOOTH,
                {"smooth": True},
            ),
        ],
    )
    def test_it_calls_open_elevation_service_according_to_user_preferences(
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        input_missing_elevations_processing: "ElevationDataSource",
        expected_kwargs: Dict,
    ) -> None:
        user_1.missing_elevations_processing = (
            input_missing_elevations_processing
        )
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_elevations_mock,
        ):
            service.process_workout()

        get_elevations_mock.assert_called_once()
        _, call_kwargs = get_elevations_mock.call_args
        assert call_kwargs == expected_kwargs

    def test_it_calls_valhalla_elevation_service_according_to_user_preferences(
        self,
        app_with_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                ValhallaElevationService, "get_elevations", return_value=[]
            ) as get_elevations_mock,
        ):
            service.process_workout()

        get_elevations_mock.assert_called_once()

    def test_it_does_not_call_elevation_services_when_user_preferences_is_none(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.FILE
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations"
            ) as get_open_elevations_mock,
            patch.object(
                OpenElevationService, "get_elevations"
            ) as get_valhalla_elevations_mock,
        ):
            service.process_workout()

        get_open_elevations_mock.assert_not_called()
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_ignores_update_elevation_value_on_refresh_value(
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=False,
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_elevations_mock,
        ):
            service.process_workout()

        get_elevations_mock.assert_called_once()

    def test_it_ignores_change_elevation_source(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION_SMOOTH
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            change_elevation_source=ElevationDataSource.VALHALLA,
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService, "get_elevations", return_value=[]
            ) as get_valhalla_elevations_mock,
        ):
            service.process_workout()

        get_open_elevations_mock.assert_called_once()
        get_valhalla_elevations_mock.assert_not_called()

    def test_it_creates_workout_and_segment_without_elevation_when_gpx_file_has_no_elevation(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        # Open Elevation API URL is not set, no missing elevation are fetched
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with patch.object(
            OpenElevationService, "get_elevations"
        ) as get_elevations_mock:
            service.process_workout()
            db.session.commit()

        get_elevations_mock.assert_not_called()
        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        # workout
        workout = Workout.query.one()
        assert to_shape(workout.start_point_geom) == Point(
            track_points_part_1_coordinates[0]
        )
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
        assert workout.elevation_data_source == (ElevationDataSource.FILE)
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
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 317.15294405358054,
            "duration": 250,
            "elevation": None,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.8530805687,
            "speed": 4.22,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_and_segment_when_gpx_file_has_invalid_elevation(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_invalid_elevation: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_invalid_elevation
        )

        service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        self.assert_workout(user_1, sport_1_cycling, workout)

    def test_it_creates_workout_for_sport_without_elevation_when_file_contains_elevation(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_5_outdoor_tennis: Sport,
        user_1: "User",
        gpx_file: str,  # file w/ elevation
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1, sport_5_outdoor_tennis, gpx_file
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
            ),
        ):
            service.process_workout()
        db.session.commit()

        self.assert_workout_without_elevation()

    def test_it_creates_workout_for_sport_without_elevation_when_file_does_not_contain_elevation(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_5_outdoor_tennis: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1, sport_5_outdoor_tennis, gpx_file_without_elevation
        )

        with patch.object(
            requests,
            "post",
            return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
        ) as requests_post_mock:
            service.process_workout()
        db.session.commit()

        requests_post_mock.assert_not_called()
        self.assert_workout_without_elevation()

    def test_it_creates_workout_and_segment_when_gpx_file_has_no_elevation_and_open_elevation_api_is_set(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
            ),
        ):
            service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.elevation_data_source == (
            ElevationDataSource.OPEN_ELEVATION
        )
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)
        workout_segment = workout.segments[0]
        coordinates = (
            track_points_part_1_coordinates + track_points_part_2_coordinates
        )
        assert len(workout_segment.points) == len(coordinates)
        assert workout_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout_segment.points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_creates_workout_when_user_preference_is_open_elevation_smooth(
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION_SMOOTH
        )
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
            ),
        ):
            service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.elevation_data_source == (
            ElevationDataSource.OPEN_ELEVATION_SMOOTH
        )

    def test_it_creates_workout_when_user_preference_is_valhalla(
        self,
        app_with_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ),
        ):
            service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.elevation_data_source == (ElevationDataSource.VALHALLA)
        assert workout.segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 1998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_creates_workout_and_segment_when_open_elevation_api_returns_empty_list(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_without_elevation
        )

        with (
            patch.object(
                OpenElevationService,
                "get_elevations",
                return_value=[],
            ),
        ):
            service.process_workout()
        db.session.commit()

        self.assert_workout_without_elevation()

    def test_it_calls_open_elevation_for_each_segment(
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_3_segments: str,
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        regex = re.compile("<ele>(.*)</ele>")
        gpx_file = regex.sub("", gpx_file_with_3_segments)
        service = self.init_service_with_gpx(user_1, sport_1_cycling, gpx_file)

        with (
            patch.object(
                OpenElevationService,
                "get_elevations",
                return_value=[],
            ) as get_elevations_mock,
        ):
            service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        assert len(workout.segments) == 3
        assert get_elevations_mock.call_count == 3

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
        assert to_shape(workout.start_point_geom) == Point(
            segment_0_coordinates[0]
        )
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
        assert workout_segments[0].start_date == datetime(
            2018, 3, 13, 12, 44, 50, tzinfo=timezone.utc
        )
        assert len(workout_segments[0].points) == len(segment_0_coordinates)
        assert workout_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:50+00:00",
        }
        assert workout_segments[0].points[-1] == {
            "distance": 17.551714568218248,
            "duration": 10,
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
            "pace": 0.3817603393,
            "speed": 9.43,
            "time": "2018-03-13 12:45:00+00:00",
        }
        # second workout segment
        assert workout_segments[1].workout_id == workout.id
        assert workout_segments[1].workout_uuid == workout.uuid
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
        assert workout_segments[1].start_date == datetime(
            2018, 3, 13, 12, 46, 0, tzinfo=timezone.utc
        )
        assert len(workout_segments[1].points) == len(segment_1_coordinates)
        assert workout_segments[1].points[0] == {
            "distance": 0.0,
            "duration": 70,
            "elevation": 987.0,
            "latitude": 44.67972,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:46:00+00:00",
        }
        assert workout_segments[1].points[-1] == {
            "distance": 12.598402521897194,
            "duration": 80,
            "elevation": 986.0,
            "latitude": 44.67961,
            "longitude": 6.0737,
            "speed": 4.23,
            "pace": 0.8510638298,
            "time": "2018-03-13 12:46:10+00:00",
        }
        # third workout segment
        assert workout_segments[2].workout_id == workout.id
        assert workout_segments[2].workout_uuid == workout.uuid
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
        assert workout_segments[2].start_date == datetime(
            2018, 3, 13, 12, 47, 10, tzinfo=timezone.utc
        )
        assert len(workout_segments[2].points) == len(segment_2_coordinates)
        assert workout_segments[2].points[0] == {
            "distance": 0.0,
            "duration": 140,
            "elevation": 980.0,
            "latitude": 44.67858,
            "longitude": 6.07425,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:47:10+00:00",
        }
        assert workout_segments[2].points[-1] == {
            "distance": 24.83101225255615,
            "duration": 150,
            "elevation": 979.0,
            "latitude": 44.67837,
            "longitude": 6.07435,
            "pace": 0.8888888889,
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
        # gpx with 3 segments, the second segment has only one point
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_zero_distance_segment
        )

        service.process_workout()
        db.session.commit()

        # no description in gpx file, only name is present
        assert service.workout_description is None
        assert service.workout_name == "just a workout"
        self.assert_workout_with_two_segments(user_1, sport_1_cycling)

    def test_it_creates_workout_and_segments_when_first_segment_has_no_points(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_first_segment_empty: str,
    ) -> None:
        # gpx with 3 segments, first segment is empty
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_first_segment_empty
        )

        service.process_workout()
        db.session.commit()

        # no description in gpx file, only name is present
        assert service.workout_description is None
        assert service.workout_name == "just a workout"

        self.assert_workout_with_two_segments(user_1, sport_1_cycling)

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
            "pace": None,
            "power": 0,
            "speed": 0.0,
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
            "pace": None,
            "power": 0,
            "speed": 0.0,
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
            "pace": None,
            "power": 0,
            "speed": 0.0,
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
            "pace": None,
            "power": 0,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_creates_workout_when_gpx_file_has_calories(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_calories: str,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1, sport_1_cycling, gpx_file_with_calories
        )

        service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.calories == 86
        self.assert_workout(user_1, sport_1_cycling, workout)
        self.assert_workout_segment(workout)
        self.assert_workout_records(workout)

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

    def test_it_does_not_calls_weather_service_when_endpoint_has_no_time(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_time_on_last_point: str,
        default_weather_service: MagicMock,
    ) -> None:
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_time_on_last_point,
            get_weather=True,
        )

        service.process_workout()
        db.session.commit()

        default_weather_service.assert_not_called()

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


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutGpxServiceProcessFileOnRefresh(
    WorkoutGpxServiceProcessFileTestCase
):
    def test_it_refreshes_workout(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_ns3_extensions: str,
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_with_ns3_extensions,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1,
        )

        service.process_workout()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.elevation_data_source == (
            ElevationDataSource.FILE
        )
        self.assert_workout(
            user_1, sport_1_cycling, workout_cycling_user_1, assert_full=False
        )
        assert workout_cycling_user_1.ave_cadence == 52
        assert workout_cycling_user_1.ave_hr == 85
        assert workout_cycling_user_1.ave_power == 248
        assert workout_cycling_user_1.max_cadence == 57
        assert workout_cycling_user_1.max_hr == 92
        assert workout_cycling_user_1.max_power == 326
        assert workout_cycling_user_1.source == "Garmin Connect"
        self.assert_workout_segment(workout_cycling_user_1)
        assert workout_cycling_user_1.segments[0].points[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "heart_rate": 92,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "power": 0,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_calls_elevation_service_when_get_elevation_on_refresh_is_true(
        self,
        app_with_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.FILE
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_called_once()
        db.session.refresh(workout_cycling_user_1_with_coordinates)
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == user_1.missing_elevations_processing
        )
        new_segment = WorkoutSegment.query.one()
        assert (
            new_segment.points[0].get("elevation") == 1998.0  # value updated
        )

    def test_it_does_not_call_elevation_service_when_get_elevation_on_refresh_is_false(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1: "Workout",
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        workout_cycling_user_1.elevation_data_source = ElevationDataSource.FILE
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=False,
            workout=workout_cycling_user_1,
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_not_called()
        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.elevation_data_source
            == ElevationDataSource.FILE  # unchanged
        )
        assert (
            workout_cycling_user_1.segments[0].points[0].get("elevation")
            is None
        )

    def test_it_does_not_call_elevation_service_when_workout_missing_elevations_processing_is_unchanged(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION_SMOOTH
        )
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.OPEN_ELEVATION_SMOOTH
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_not_called()
        db.session.refresh(workout_cycling_user_1_with_coordinates)
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.OPEN_ELEVATION_SMOOTH  # unchanged
        )
        new_segment = WorkoutSegment.query.one()
        assert (
            new_segment.points[0].get("elevation") == 998.0  # value unchanged
        )

    def test_it_calls_elevation_service_when_workout_missing_elevations_processing_is_different(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.OPEN_ELEVATION_SMOOTH
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_called_once()
        db.session.refresh(workout_cycling_user_1_with_coordinates)
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.VALHALLA
        )
        new_segment = WorkoutSegment.query.one()
        assert new_segment.points[0].get("elevation") == 1998.0

    def test_it_does_not_remove_existing_elevation_when_elevation_service_is_disabled(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        # Elevation API URLs have been removed after workout creation
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.OPEN_ELEVATION
        )
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(requests, "post") as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_not_called()
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.OPEN_ELEVATION
        )
        new_segment = WorkoutSegment.query.one()
        assert new_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_does_not_remove_existing_elevation_when_preference_is_none(
        self,
        app: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.VALHALLA
        )
        # user remove elevation service from preference
        user_1.missing_elevations_processing = ElevationDataSource.FILE
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(requests, "post") as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_not_called()
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.VALHALLA
        )
        new_segment = WorkoutSegment.query.one()
        assert new_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_does_not_remove_existing_elevation_when_get_elevation_on_refresh_is_false(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.VALHALLA
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=False,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(requests, "post") as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_not_called()
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.VALHALLA  # unchanged
        )
        new_segment = WorkoutSegment.query.one()
        assert new_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_calls_elevations_when_missing_elevations_were_partially_updated(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_with_2_segments_and_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_without_elevation: "WorkoutSegment",
    ) -> None:
        # due to rate limits issues, not all data could be collected
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.VALHALLA
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_with_2_segments_and_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
        )

        with (
            patch.object(
                requests,
                "post",
                side_effect=[
                    self.get_response({"height": VALHALLA_VALUES[:9]}),
                    self.get_response({"height": VALHALLA_VALUES[9:]}),
                ],
            ) as requests_mock,
        ):
            service.process_workout()

        assert requests_mock.call_count == 2
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.VALHALLA
        )
        new_segments = WorkoutSegment.query.all()
        assert new_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 1998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert new_segments[1].points[0] == {
            "distance": 0.0,
            "duration": 105,
            "elevation": 1987.0,
            "latitude": 44.67977,
            "longitude": 6.07364,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:46:30+00:00",
        }

    def test_it_calls_elevations_when_mismatch_between_workout_and_segments_data(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1: "Workout",
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.VALHALLA
        # This case should not happen
        workout_cycling_user_1.elevation_data_source = (
            ElevationDataSource.VALHALLA
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1,
        )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()

        requests_mock.assert_called_once()
        assert (
            workout_cycling_user_1.elevation_data_source
            == ElevationDataSource.VALHALLA
        )
        new_segment = WorkoutSegment.query.one()
        assert new_segment.points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 1998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_ignores_invalid_change_elevation_source(
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        # check on change_elevation_source is made before calling service
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
            change_elevation_source=ElevationDataSource.VALHALLA,
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService,
                "get_elevations",
                return_value=VALHALLA_VALUES,
            ) as get_valhalla_elevations_mock,
        ):
            service.process_workout()

        get_open_elevations_mock.assert_not_called()
        get_valhalla_elevations_mock.assert_not_called()
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.FILE  # unchanged
        )
        new_segments = WorkoutSegment.query.all()
        assert new_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert new_segments[0].points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_overrides_user_preferences_when_change_elevation_source_is_provided(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
            change_elevation_source=ElevationDataSource.VALHALLA,
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService,
                "get_elevations",
                return_value=VALHALLA_VALUES,
            ) as get_valhalla_elevations_mock,
        ):
            service.process_workout()

        get_open_elevations_mock.assert_not_called()
        get_valhalla_elevations_mock.assert_called_once()
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.VALHALLA
        )
        new_segments = WorkoutSegment.query.all()
        assert new_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 1998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert new_segments[0].points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 1975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_overrides_user_preferences_when_gpx_has_no_elevation(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file_without_elevation: str,
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        user_1.missing_elevations_processing = ElevationDataSource.FILE
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file_without_elevation,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1_with_coordinates,
            change_elevation_source=ElevationDataSource.VALHALLA,
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService,
                "get_elevations",
                return_value=VALHALLA_VALUES,
            ) as get_valhalla_elevations_mock,
        ):
            service.process_workout()

        get_open_elevations_mock.assert_not_called()
        get_valhalla_elevations_mock.assert_called_once()
        assert (
            workout_cycling_user_1_with_coordinates.elevation_data_source
            == ElevationDataSource.VALHALLA
        )
        new_segments = WorkoutSegment.query.all()
        assert new_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 1998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert new_segments[0].points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 1975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

    def test_it_gets_elevation_from_file_when_change_elevation_source_is_file(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: Sport,
        user_1: "User",
        gpx_file: str,
        workout_cycling_user_1: "Workout",
    ) -> None:
        user_1.missing_elevations_processing = (
            ElevationDataSource.OPEN_ELEVATION
        )
        workout_cycling_user_1.elevation_data_source = (
            ElevationDataSource.VALHALLA
        )
        service = self.init_service_with_gpx(
            user_1,
            sport_1_cycling,
            gpx_file,
            get_elevation_on_refresh=True,
            workout=workout_cycling_user_1,
            change_elevation_source=ElevationDataSource.FILE,
        )

        with (
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as get_open_elevations_mock,
            patch.object(
                ValhallaElevationService,
                "get_elevations",
                return_value=[],
            ) as get_valhalla_elevations_mock,
        ):
            service.process_workout()

        get_open_elevations_mock.assert_not_called()
        get_valhalla_elevations_mock.assert_not_called()
        assert (
            workout_cycling_user_1.elevation_data_source
            == ElevationDataSource.FILE
        )
        new_segments = WorkoutSegment.query.all()
        assert new_segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert new_segments[0].points[-1] == {
            "distance": 320.12787035769946,
            "duration": 250,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "pace": 0.831408776,
            "speed": 4.33,
            "time": "2018-03-13 12:48:55+00:00",
        }

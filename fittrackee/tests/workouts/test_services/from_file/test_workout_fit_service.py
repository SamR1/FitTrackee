from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import patch

import gpxpy
import pytest

from fittrackee import db
from fittrackee.tests.fixtures.fixtures_workouts import (
    FILE_STATS_WITH_DATA,
    FILE_STATS_WITH_NONE,
)
from fittrackee.tests.workouts.mixins import WorkoutFileMixin
from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.models import Workout
from fittrackee.workouts.services import WorkoutFitService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestWorkoutFitServiceGetCoordinate(WorkoutFileMixin):
    @pytest.mark.parametrize(
        "input_value,expected_coordinate",
        [
            (512175953, 42.93009244836867),
            (-103307332, -8.659120537340641),
        ],
    )
    def test_it_calculates_coordinate_from_semicircle(
        self, app: "Flask", input_value: int, expected_coordinate: float
    ) -> None:
        coordinate = WorkoutFitService.get_coordinate(input_value)

        assert coordinate == expected_coordinate


class TestWorkoutFitServiceParseFile(WorkoutFileMixin):
    def test_it_raises_error_when_file_is_not_fit(
        self, app: "Flask", invalid_kml_file: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing fit file"
            ),
        ):
            WorkoutFitService.parse_file(
                self.get_fit_file_content(app, file_name="example.kmz"),
                segments_creation_event="none",
            )

    def test_it_returns_gpx_with_fit_content(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        """
        .fit file used for the test does not contain any stats
        """
        gpx, file_stats = WorkoutFitService.parse_file(
            self.get_fit_file_content(app, file_name="example.fit"),
            segments_creation_event="none",
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2
        assert file_stats == FILE_STATS_WITH_NONE


class TestWorkoutFitServiceInstantiation(WorkoutFileMixin):
    def test_it_instantiates_service(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        service = WorkoutFitService(
            user_1,
            self.get_fit_file_content(app, file_name="example.fit"),
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


class TestWorkoutFitServiceProcessWorkout(WorkoutFileMixin):
    def test_it_creates_workout_when_workout_stats_from_file_is_false(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workout_stats_from_file = False
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=FILE_STATS_WITH_DATA,
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(app, file_name="example.fit"),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
            )

            service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        assert float(workout.ascent) == 0.0  # type: ignore
        assert float(workout.ave_speed) == 4.58  # type: ignore
        assert float(workout.descent) == 21.0  # type: ignore
        assert float(workout.distance) == 0.318  # type: ignore
        assert workout.duration == timedelta(minutes=4, seconds=10)
        assert float(workout.max_alt) == 997.0  # type: ignore
        assert float(workout.max_speed) == 5.11  # type: ignore
        assert float(workout.min_alt) == 976.0  # type: ignore
        assert workout.moving == timedelta(minutes=4, seconds=10)
        assert workout.pauses == timedelta(seconds=0)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.ave_power is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.max_power is None
        assert workout.workout_stats_from_file is False

    def test_it_creates_workout_when_stats_are_extracted_from_file(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workout_stats_from_file = True
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=FILE_STATS_WITH_DATA,
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(app, file_name="example.fit"),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
            )

            service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        assert float(workout.ascent) == FILE_STATS_WITH_DATA["ascent"]
        assert float(workout.ave_speed) == pytest.approx(
            FILE_STATS_WITH_DATA["ave_speed"] / 1000 * 3600, 0.01
        )
        assert float(workout.descent) == FILE_STATS_WITH_DATA["descent"]
        assert float(workout.distance) == float(
            FILE_STATS_WITH_DATA["distance"] / 1000
        )
        assert workout.duration == timedelta(
            seconds=FILE_STATS_WITH_DATA["duration"]
        )
        assert float(workout.max_alt) == 997.0  # type: ignore
        assert float(workout.max_speed) == pytest.approx(
            float(FILE_STATS_WITH_DATA["max_speed"] / 1000 * 3600)
        )
        assert float(workout.min_alt) == 976.0  # type: ignore
        assert workout.moving == timedelta(
            seconds=FILE_STATS_WITH_DATA["moving"]
        )
        assert workout.pauses == timedelta(
            seconds=FILE_STATS_WITH_DATA["pauses"]
        )
        assert workout.ave_cadence == FILE_STATS_WITH_DATA["ave_cadence"]
        assert workout.ave_hr == FILE_STATS_WITH_DATA["ave_hr"]
        assert workout.ave_power == FILE_STATS_WITH_DATA["ave_power"]
        assert workout.max_cadence == FILE_STATS_WITH_DATA["max_cadence"]
        assert workout.max_hr == FILE_STATS_WITH_DATA["max_hr"]
        assert workout.max_power == FILE_STATS_WITH_DATA["max_power"]
        assert workout.workout_stats_from_file is True

    def test_it_creates_workout_when_stats_are_none(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workout_stats_from_file = True
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=FILE_STATS_WITH_NONE,
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(app, file_name="example.fit"),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
            )

            service.process_workout()
        db.session.commit()

        assert service.workout_description is None
        assert service.workout_name is None
        workout = Workout.query.one()
        assert workout.ascent is None
        assert float(workout.ave_speed) == 0.0
        assert workout.descent is None
        assert float(workout.distance) == 0.0
        assert workout.duration == timedelta(seconds=0)
        assert float(workout.max_alt) == 997.0  # type: ignore
        assert float(workout.max_speed) == 0.0
        assert float(workout.min_alt) == 976.0  # type: ignore
        assert workout.moving == timedelta(seconds=0)
        assert workout.pauses == timedelta(seconds=0)
        assert workout.ave_cadence is None
        assert workout.ave_hr is None
        assert workout.ave_power is None
        assert workout.max_cadence is None
        assert workout.max_hr is None
        assert workout.max_power is None
        assert workout.workout_stats_from_file is True

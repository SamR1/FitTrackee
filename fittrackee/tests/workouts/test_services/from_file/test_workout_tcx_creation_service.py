from typing import TYPE_CHECKING

import gpxpy
import pytest

from fittrackee.tests.workouts.mixins import (
    WorkoutFileMixin,
)
from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.services import WorkoutTcxCreationService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestWorkoutTcxCreationServiceParseFile(WorkoutFileMixin):
    def test_it_raises_error_when_cx_file_is_invalid(
        self, app: "Flask", invalid_tcx_file: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing tcx file"
            ),
        ):
            WorkoutTcxCreationService.parse_file(
                self.get_file_content(invalid_tcx_file)
            )

    def test_it_raises_error_when_tcx_file_has_no_activities(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_file_wo_activities: str,
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="no activities in tcx file"
            ),
        ):
            WorkoutTcxCreationService.parse_file(
                self.get_file_content(tcx_file_wo_activities)
            )

    def test_it_raises_error_when_tcx_file_has_no_laps(
        self, app: "Flask", sport_1_cycling: "Sport", tcx_file_wo_laps: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="no laps or no tracks in tcx file"
            ),
        ):
            WorkoutTcxCreationService.parse_file(
                self.get_file_content(tcx_file_wo_laps)
            )

    def test_it_raises_error_when_tcx_file_has_no_tracks(
        self, app: "Flask", sport_1_cycling: "Sport", tcx_file_wo_tracks: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="no laps or no tracks in tcx file"
            ),
        ):
            WorkoutTcxCreationService.parse_file(
                self.get_file_content(tcx_file_wo_tracks)
            )

    def test_it_returns_gpx_with_tcx_with_one_lap_and_one_track(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        gpx = WorkoutTcxCreationService.parse_file(
            self.get_file_content(tcx_with_one_lap_and_one_track)
        )

        assert isinstance(gpx, gpxpy.gpx.GPX)
        assert len(gpx.tracks) == 1
        assert gpx.tracks[0].name is None
        assert gpx.tracks[0].description is None
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2

    def test_it_returns_gpx_with_tcx_with_one_lap_and_two_trackss(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        tcx_with_one_lap_and_two_tracks: str,
    ) -> None:
        gpx = WorkoutTcxCreationService.parse_file(
            self.get_file_content(tcx_with_one_lap_and_two_tracks)
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2

    def test_it_returns_gpx_with_tcx_with_two_laps(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_with_two_laps: str,
    ) -> None:
        gpx = WorkoutTcxCreationService.parse_file(
            self.get_file_content(tcx_with_with_two_laps)
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2

    def test_it_returns_gpx_with_tcx_with_two_activities(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_with_two_activities: str,
    ) -> None:
        gpx = WorkoutTcxCreationService.parse_file(
            self.get_file_content(tcx_with_with_two_activities)
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 2
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 235.0
        assert round(moving_data.moving_distance, 1) == 297.5


class TestWorkoutTcxCreationServiceInstantiation(WorkoutFileMixin):
    def test_it_instantiates_service(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        service = WorkoutTcxCreationService(
            user_1,
            self.get_file_content(tcx_with_one_lap_and_one_track),
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
        # from WorkoutGPXCreationService
        assert isinstance(service.gpx, gpxpy.gpx.GPX)

from typing import TYPE_CHECKING

import gpxpy
import pytest

from fittrackee.tests.workouts.mixins import (
    WorkoutFileMixin,
)
from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.services import WorkoutTcxService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestWorkoutTcxServiceParseFile(WorkoutFileMixin):
    @staticmethod
    def assert_gpx(gpx: "gpxpy.gpx.GPX") -> None:
        assert isinstance(gpx, gpxpy.gpx.GPX)
        assert len(gpx.tracks) == 1
        assert gpx.tracks[0].name is None
        assert gpx.tracks[0].description is None
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2

    @staticmethod
    def assert_gpx_with_extensions(gpx: "gpxpy.gpx.GPX") -> None:
        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 90.0
        assert round(moving_data.moving_distance, 1) == 112.4
        first_point = gpx.tracks[0].segments[0].points[0]
        first_point_hr = first_point.extensions[0][0]
        assert first_point_hr.tag == "{gpxtpx}hr"
        assert first_point_hr.text == "92"
        first_point_cad = first_point.extensions[0][1]
        assert first_point_cad.tag == "{gpxtpx}cad"
        assert first_point_cad.text == "0"
        last_point = gpx.tracks[0].segments[0].points[-1]
        last_point_hr = last_point.extensions[0][0]
        assert last_point_hr.tag == "{gpxtpx}hr"
        assert last_point_hr.text == "86"
        last_point_cad = last_point.extensions[0][1]
        assert last_point_cad.tag == "{gpxtpx}cad"
        assert last_point_cad.text == "53"

    def test_it_raises_error_when_cx_file_is_invalid(
        self, app: "Flask", invalid_tcx_file: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing tcx file"
            ),
        ):
            WorkoutTcxService.parse_file(
                self.get_file_content(invalid_tcx_file),
                segments_creation_event="none",
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
            WorkoutTcxService.parse_file(
                self.get_file_content(tcx_file_wo_activities),
                segments_creation_event="none",
            )

    def test_it_raises_error_when_tcx_file_has_no_laps(
        self, app: "Flask", sport_1_cycling: "Sport", tcx_file_wo_laps: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="no laps or no tracks in tcx file"
            ),
        ):
            WorkoutTcxService.parse_file(
                self.get_file_content(tcx_file_wo_laps),
                segments_creation_event="none",
            )

    def test_it_raises_error_when_tcx_file_has_no_tracks(
        self, app: "Flask", sport_1_cycling: "Sport", tcx_file_wo_tracks: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="no laps or no tracks in tcx file"
            ),
        ):
            WorkoutTcxService.parse_file(
                self.get_file_content(tcx_file_wo_tracks),
                segments_creation_event="none",
            )

    def test_it_raises_error_when_tcx_file_has_no_coordinates(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_without_coordinates: str,
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="no coordinates in tcx file"
            ),
        ):
            WorkoutTcxService.parse_file(
                self.get_file_content(tcx_without_coordinates),
                segments_creation_event="none",
            )

    def test_it_returns_gpx_with_tcx_with_one_lap_and_one_track(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_one_lap_and_one_track),
            segments_creation_event="none",
        )

        self.assert_gpx(gpx)

    def test_it_returns_gpx_with_tcx_with_one_lap_and_two_tracks(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        tcx_with_one_lap_and_two_tracks: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_one_lap_and_two_tracks),
            segments_creation_event="none",
        )

        self.assert_gpx(gpx)

    def test_it_returns_gpx_with_tcx_with_two_laps(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_two_laps: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_two_laps),
            segments_creation_event="none",
        )

        self.assert_gpx(gpx)

    def test_it_returns_gpx_with_tcx_with_two_activities(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_two_activities: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_two_activities),
            segments_creation_event="none",
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 2
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 235.0
        assert round(moving_data.moving_distance, 1) == 297.5

    def test_it_ignores_invalid_elevation(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_invalid_elevation: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_invalid_elevation),
            segments_creation_event="none",
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        elevations = gpx.tracks[0].segments[0].get_elevation_extremes()
        assert elevations.minimum is None
        assert elevations.maximum is None

    def test_it_returns_gpx_with_tcx_with_heart_rate_cadence_and_power(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_heart_rate_cadence_and_power: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_heart_rate_cadence_and_power),
            segments_creation_event="none",
        )

        self.assert_gpx_with_extensions(gpx)
        first_point = gpx.tracks[0].segments[0].points[0]
        first_point_cad = first_point.extensions[0][2]
        assert first_point_cad.tag == "{gpxtpx}power"
        assert first_point_cad.text == "0"
        last_point = gpx.tracks[0].segments[0].points[-1]
        last_point_cad = last_point.extensions[0][2]
        assert last_point_cad.tag == "{gpxtpx}power"
        assert last_point_cad.text == "100"

    def test_it_returns_gpx_with_tcx_with_heart_rate_cadence_and_ns3_power(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_heart_rate_cadence_and_ns3_power: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_heart_rate_cadence_and_ns3_power),
            segments_creation_event="none",
        )

        self.assert_gpx_with_extensions(gpx)
        first_point = gpx.tracks[0].segments[0].points[0]
        first_point_cad = first_point.extensions[0][2]
        assert first_point_cad.tag == "{gpxtpx}power"
        assert first_point_cad.text == "0"
        last_point = gpx.tracks[0].segments[0].points[-1]
        last_point_cad = last_point.extensions[0][2]
        assert last_point_cad.tag == "{gpxtpx}power"
        assert last_point_cad.text == "100"

    def test_it_returns_gpx_with_tcx_with_heart_rate_and_run_cadence(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_heart_rate_and_run_cadence: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_heart_rate_and_run_cadence),
            segments_creation_event="none",
        )

        self.assert_gpx_with_extensions(gpx)

    def test_it_returns_gpx_with_tcx_with_heart_rate_and_ns3_run_cadence(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_heart_rate_and_ns3_run_cadence: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_heart_rate_and_ns3_run_cadence),
            segments_creation_event="none",
        )

        self.assert_gpx_with_extensions(gpx)

    def test_it_returns_gpx_with_calories(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        tcx_with_calories: str,
    ) -> None:
        gpx = WorkoutTcxService.parse_file(
            self.get_file_content(tcx_with_calories),
            segments_creation_event="none",
        )

        self.assert_gpx(gpx)
        track_extension = gpx.tracks[0].extensions[0][0]
        assert track_extension.tag == "{gpxtrkx}Calories"
        assert track_extension.text == "86"


class TestWorkoutTcxServiceInstantiation(WorkoutFileMixin):
    def test_it_instantiates_service(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        service = WorkoutTcxService(
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
        # from WorkoutGpxService
        assert isinstance(service.gpx, gpxpy.gpx.GPX)

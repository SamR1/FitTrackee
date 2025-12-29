from typing import TYPE_CHECKING

import gpxpy
import pytest

from fittrackee.tests.workouts.mixins import (
    WorkoutFileMixin,
)
from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.services import WorkoutKmlService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestWorkoutKmlServiceParseFile(WorkoutFileMixin):
    def test_it_raises_error_when_kml_file_is_invalid(
        self, app: "Flask", invalid_kml_file: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing kml file"
            ),
        ):
            WorkoutKmlService.parse_file(
                self.get_file_content(invalid_kml_file),
                segments_creation_event="none",
            )

    def test_it_raises_error_when_kml_file_has_no_tracks(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_file_wo_tracks: str,
    ) -> None:
        with (
            pytest.raises(WorkoutFileException, match="no tracks in kml file"),
        ):
            WorkoutKmlService.parse_file(
                self.get_file_content(kml_file_wo_tracks),
                segments_creation_event="none",
            )

    def test_it_raises_error_when_kml_file_has_folders(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_file_with_folders: str,
    ) -> None:
        with (
            pytest.raises(WorkoutFileException, match="unsupported kml file"),
        ):
            WorkoutKmlService.parse_file(
                self.get_file_content(kml_file_with_folders),
                segments_creation_event="none",
            )

    def test_it_returns_gpx_with_kml_2_2_with_one_track(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_2_with_one_track: str,
    ) -> None:
        gpx = WorkoutKmlService.parse_file(
            self.get_file_content(kml_2_2_with_one_track),
            segments_creation_event="none",
        )

        assert isinstance(gpx, gpxpy.gpx.GPX)
        assert len(gpx.tracks) == 1
        assert gpx.tracks[0].name == "just a workout"
        assert gpx.tracks[0].description == "some description"
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 320.0

    def test_it_returns_gpx_with_kml_2_2_with_two_tracks(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_2_with_two_tracks: str,
    ) -> None:
        gpx = WorkoutKmlService.parse_file(
            self.get_file_content(kml_2_2_with_two_tracks),
            segments_creation_event="none",
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 2
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 235.0
        assert round(moving_data.moving_distance, 1) == 299.5

    def test_it_returns_gpx_with_kml_2_3_with_one_track(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_3_with_one_track: str,
    ) -> None:
        gpx = WorkoutKmlService.parse_file(
            self.get_file_content(kml_2_3_with_one_track),
            segments_creation_event="none",
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 320.0

    def test_it_returns_gpx_with_kml_2_3_with_two_tracks(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_3_with_two_tracks: str,
    ) -> None:
        gpx = WorkoutKmlService.parse_file(
            self.get_file_content(kml_2_3_with_two_tracks),
            segments_creation_event="none",
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 2
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 235.0
        assert round(moving_data.moving_distance, 1) == 299.5

    def test_it_returns_gpx_with_kml_without_name_and_description(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_3_wo_name_and_description: str,
    ) -> None:
        gpx = WorkoutKmlService.parse_file(
            self.get_file_content(kml_2_3_wo_name_and_description),
            segments_creation_event="none",
        )

        assert gpx.name is None
        assert gpx.description is None

    def test_it_returns_gpx_with_kml_2_2_with_extended_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_2_with_extended_data: str,
    ) -> None:
        gpx = WorkoutKmlService.parse_file(
            self.get_file_content(kml_2_2_with_extended_data),
            segments_creation_event="none",
        )

        assert isinstance(gpx, gpxpy.gpx.GPX)
        assert len(gpx.tracks) == 1
        assert gpx.tracks[0].name == "just a workout"
        assert gpx.tracks[0].description == "some description"
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 320.0
        first_point = gpx.tracks[0].segments[0].points[0]
        first_point_hr = first_point.extensions[0][0]
        assert first_point_hr.tag == "{gpxtpx}hr"
        assert first_point_hr.text == "92"
        first_point_cad = first_point.extensions[0][1]
        assert first_point_cad.tag == "{gpxtpx}cad"
        assert first_point_cad.text == "0"
        first_point_cad = first_point.extensions[0][2]
        assert first_point_cad.tag == "{gpxtpx}power"
        assert first_point_cad.text == "0"
        last_point = gpx.tracks[0].segments[0].points[-1]
        last_point_hr = last_point.extensions[0][0]
        assert last_point_hr.tag == "{gpxtpx}hr"
        assert last_point_hr.text == "81"
        last_point_cad = last_point.extensions[0][1]
        assert last_point_cad.tag == "{gpxtpx}cad"
        assert last_point_cad.text == "50"
        last_point_cad = last_point.extensions[0][2]
        assert last_point_cad.tag == "{gpxtpx}power"
        assert last_point_cad.text == "90"


class TestWorkoutKmlServiceInstantiation(WorkoutFileMixin):
    def test_it_instantiates_service(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_2_with_one_track: str,
    ) -> None:
        service = WorkoutKmlService(
            user_1,
            self.get_file_content(kml_2_2_with_one_track),
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

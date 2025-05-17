from typing import TYPE_CHECKING

import gpxpy
import pytest

from fittrackee.tests.workouts.mixins import (
    WorkoutFileMixin,
)
from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.services import WorkoutKmlCreationService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestWorkoutKmlCreationServiceParseFile(WorkoutFileMixin):
    def test_it_raises_error_when_kml_file_is_invalid(
        self, app: "Flask", invalid_kml_file: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing kml file"
            ),
        ):
            WorkoutKmlCreationService.parse_file(
                self.get_file_content(invalid_kml_file)
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
            WorkoutKmlCreationService.parse_file(
                self.get_file_content(kml_file_wo_tracks)
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
            WorkoutKmlCreationService.parse_file(
                self.get_file_content(kml_file_with_folders)
            )

    def test_it_returns_gpx_with_kml_2_2_with_one_track(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_2_with_one_track: str,
    ) -> None:
        gpx = WorkoutKmlCreationService.parse_file(
            self.get_file_content(kml_2_2_with_one_track)
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
        gpx = WorkoutKmlCreationService.parse_file(
            self.get_file_content(kml_2_2_with_two_tracks)
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
        gpx = WorkoutKmlCreationService.parse_file(
            self.get_file_content(kml_2_3_with_one_track)
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
        gpx = WorkoutKmlCreationService.parse_file(
            self.get_file_content(kml_2_3_with_two_tracks)
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
        gpx = WorkoutKmlCreationService.parse_file(
            self.get_file_content(kml_2_3_wo_name_and_description)
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
        gpx = WorkoutKmlCreationService.parse_file(
            self.get_file_content(kml_2_2_with_extended_data)
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
        last_point = gpx.tracks[0].segments[0].points[-1]
        last_point_hr = last_point.extensions[0][0]
        assert last_point_hr.tag == "{gpxtpx}hr"
        assert last_point_hr.text == "81"
        last_point_cad = last_point.extensions[0][1]
        assert last_point_cad.tag == "{gpxtpx}cad"
        assert last_point_cad.text == "50"


class TestWorkoutKmlCreationServiceInstantiation(WorkoutFileMixin):
    def test_it_instantiates_service(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        kml_2_2_with_one_track: str,
    ) -> None:
        service = WorkoutKmlCreationService(
            user_1,
            self.get_file_content(kml_2_2_with_one_track),
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

import os
from io import BytesIO
from typing import IO, TYPE_CHECKING

import gpxpy
import pytest
from werkzeug.datastructures import FileStorage

from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.services import WorkoutFitCreationService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class WorkoutFitCreationServiceTestCase:
    @staticmethod
    def get_fit_content(app: "Flask", file_name: str) -> IO[bytes]:
        file_path = os.path.join(app.root_path, "tests/files", file_name)
        with open(file_path, "rb") as fit_file:
            content = FileStorage(
                filename=file_name, stream=BytesIO(fit_file.read())
            )
        return content.stream


class TestWorkoutFitCreationServiceParseFile(
    WorkoutFitCreationServiceTestCase
):
    def test_it_raises_error_when_file_is_not_fit(
        self, app: "Flask", invalid_kml_file: str
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing fit file"
            ),
        ):
            WorkoutFitCreationService.parse_file(
                self.get_fit_content(app, file_name="example.kmz")
            )

    def test_it_returns_gpx_with_fit_content(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        gpx = WorkoutFitCreationService.parse_file(
            self.get_fit_content(app, file_name="example.fit")
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2


#
class TestWorkoutFitCreationServiceInstantiation(
    WorkoutFitCreationServiceTestCase
):
    def test_it_instantiates_service(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        service = WorkoutFitCreationService(
            user_1,
            self.get_fit_content(app, file_name="example.fit"),
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

from datetime import timedelta
from typing import TYPE_CHECKING, Dict, Union
from unittest.mock import patch

import gpxpy
import pytest
import requests

from fittrackee import db
from fittrackee.constants import ElevationDataSource, ElevationProcessing
from fittrackee.tests.fixtures.fixtures_workouts import (
    FILE_STATS_WITH_DATA,
    FILE_STATS_WITH_NONE,
    OPEN_ELEVATION_RESPONSE,
    VALHALLA_RESPONSE,
)
from fittrackee.tests.mixins import ResponseMockMixin
from fittrackee.tests.workouts.mixins import WorkoutFileMixin
from fittrackee.workouts.exceptions import WorkoutFileException
from fittrackee.workouts.models import Workout, WorkoutSegment
from fittrackee.workouts.services import WorkoutFitService
from fittrackee.workouts.services.elevation.open_elevation_service import (
    OpenElevationService,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class WorkoutFitServiceProcessFileTestCase(WorkoutFileMixin):
    @staticmethod
    def assert_workout_with_calculated_data() -> "Workout":
        workout = Workout.query.one()
        assert float(workout.ascent) == 0.0  # type: ignore
        assert float(workout.ave_speed) == pytest.approx(4.58, 0.01)
        assert float(workout.descent) == 21.0  # type: ignore
        assert float(workout.distance) == pytest.approx(0.318, 0.001)
        assert workout.duration == timedelta(minutes=4, seconds=10)
        assert float(workout.max_alt) == 997.0  # type: ignore
        assert float(workout.max_speed) == pytest.approx(5.11, 0.01)
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
        return workout

    @staticmethod
    def assert_data_from_file(
        object_to_check: Union["Workout", "WorkoutSegment"], file_data: Dict
    ) -> None:
        assert float(object_to_check.ascent) == file_data["ascent"]  # type: ignore
        assert float(object_to_check.ave_speed) == pytest.approx(  # type: ignore
            file_data["ave_speed"] / 1000 * 3600, 0.01
        )
        assert float(object_to_check.descent) == file_data["descent"]  # type: ignore
        assert float(object_to_check.distance) == float(  # type: ignore
            file_data["distance"] / 1000
        )
        assert object_to_check.duration == timedelta(
            seconds=file_data["duration"]
        )
        assert float(object_to_check.max_alt) == 997.0  # type: ignore
        assert float(object_to_check.max_speed) == pytest.approx(  # type: ignore
            float(file_data["max_speed"] / 1000 * 3600)
        )
        assert float(object_to_check.min_alt) == 976.0  # type: ignore
        assert object_to_check.moving == timedelta(seconds=file_data["moving"])
        assert object_to_check.pauses == timedelta(seconds=file_data["pauses"])
        assert object_to_check.ave_cadence == file_data["ave_cadence"]
        assert object_to_check.ave_hr == file_data["ave_hr"]
        assert object_to_check.ave_power == file_data["ave_power"]
        assert object_to_check.max_cadence == file_data["max_cadence"]
        assert object_to_check.max_hr == file_data["max_hr"]
        assert object_to_check.max_power == file_data["max_power"]
        if isinstance(object_to_check, Workout):
            assert object_to_check.workout_stats_from_file is True


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
        self, app: "Flask", invalid_kml_file: str, sport_1_cycling: "Sport"
    ) -> None:
        with (
            pytest.raises(
                WorkoutFileException, match="error when parsing fit file"
            ),
        ):
            WorkoutFitService.parse_file(
                self.get_fit_file_content(app, file_name="example.kmz"),
                segments_creation_event="none",
                sport=sport_1_cycling,
            )

    def test_it_returns_gpx_with_fit_content(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        """
        .fit file used for the test does not contain any stats
        """
        gpx, file_stats, sessions_stats = WorkoutFitService.parse_file(
            self.get_fit_file_content(app, file_name="example.fit"),
            segments_creation_event="none",
            sport=sport_1_cycling,
        )

        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        moving_data = gpx.get_moving_data()
        assert moving_data.moving_time == 250.0
        assert round(moving_data.moving_distance, 1) == 318.2
        assert file_stats == FILE_STATS_WITH_NONE
        assert sessions_stats == []


class TestWorkoutFitServiceInstantiationOnCreation(WorkoutFileMixin):
    def test_it_instantiates_service_with_default_preferences(
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
        assert service.get_elevation_on_refresh is False
        assert service.updated_elevation_data_source is None
        assert service.elevation_processing == ElevationProcessing.NONE
        assert service.all_data_from_file is False
        # from WorkoutGpxService
        assert isinstance(service.gpx, gpxpy.gpx.GPX)

    def test_it_instantiates_service_when_workout_stats_are_extracted_from_file(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_coordinates: "WorkoutSegment",
    ) -> None:
        """
        In this case, it ignores elevation data source and elevation processing
        """
        user_1.elevation_data_source = ElevationDataSource.OPEN_ELEVATION
        user_1.elevation_processing = ElevationProcessing.FLAT_WINDOW
        user_1.process_only_missing_elevations = False
        user_1.workout_stats_from_file = True

        service = WorkoutFitService(
            user_1,
            self.get_fit_file_content(
                app_with_open_elevation_url, file_name="example.fit"
            ),
            sport_1_cycling,
            sport_1_cycling.stopped_speed_threshold,
        )

        assert service.updated_elevation_data_source is None
        assert service.elevation_processing == ElevationProcessing.NONE
        assert service.get_elevation_on_refresh is False
        assert service.reuse_existing_elevation is False
        assert service.update_existing_elevation is False
        assert service.workout_has_missing_elevation is False
        assert service.elevation_service is None
        assert service.all_data_from_file is True


class TestWorkoutFitServiceInstantiationOnRefresh(WorkoutFileMixin):
    def test_it_instantiates_service_when_workout_stats_are_extracted_from_file_and_no_elevation_parameters(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
    ) -> None:
        """
        In this case, it ignores elevation data source and elevation processing
        """
        user_1.elevation_data_source = ElevationDataSource.OPEN_ELEVATION
        user_1.elevation_processing = ElevationProcessing.FLAT_WINDOW
        user_1.process_only_missing_elevations = False
        user_1.workout_stats_from_file = True
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.OPEN_ELEVATION
        )
        workout_cycling_user_1_with_coordinates.elevation_processing = (
            ElevationProcessing.FLAT_WINDOW
        )
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.FILE
        )
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_DATA, [FILE_STATS_WITH_DATA]),
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(
                    app_with_open_elevation_url,
                    file_name="example.fit",
                ),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
                get_elevation_on_refresh=True,
                workout=workout_cycling_user_1_with_coordinates,
            )

        assert (
            service.updated_elevation_data_source == ElevationDataSource.FILE
        )
        assert service.elevation_processing == ElevationProcessing.NONE
        assert service.get_elevation_on_refresh is True
        assert service.reuse_existing_elevation is False
        assert service.update_existing_elevation is True
        assert service.workout_has_missing_elevation is False
        assert service.elevation_service is None
        assert service.all_data_from_file is True

    def test_it_instantiates_service_when_workout_stats_are_extracted_from_file_and_elevation_parameters(  # noqa
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
    ) -> None:
        """
        In this case, it ignores elevation data source and elevation processing
        """
        user_1.elevation_data_source = ElevationDataSource.VALHALLA
        user_1.elevation_processing = ElevationProcessing.NONE
        user_1.process_only_missing_elevations = False
        user_1.workout_stats_from_file = True
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.FILE
        )
        workout_cycling_user_1_with_coordinates.elevation_processing = (
            ElevationProcessing.NONE
        )

        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_DATA, [FILE_STATS_WITH_DATA]),
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(
                    app_with_open_elevation_and_valhalla_url,
                    file_name="example.fit",
                ),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
                get_elevation_on_refresh=True,
                workout=workout_cycling_user_1_with_coordinates,
                change_elevation_source=ElevationDataSource.OPEN_ELEVATION,
                elevation_processing=ElevationProcessing.FLAT_WINDOW,
            )

        assert (
            service.updated_elevation_data_source
            == ElevationDataSource.OPEN_ELEVATION
        )
        assert service.elevation_processing == ElevationProcessing.FLAT_WINDOW
        assert service.get_elevation_on_refresh is True
        assert service.reuse_existing_elevation is False
        assert service.update_existing_elevation is True
        assert service.workout_has_missing_elevation is False
        assert isinstance(
            service.elevation_service.elevation_service,  # type: ignore
            OpenElevationService,
        )
        assert service.all_data_from_file is False


class TestWorkoutFitServiceProcessWorkout(
    WorkoutFitServiceProcessFileTestCase
):
    def test_it_creates_workout_when_workout_stats_from_file_is_false(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workout_stats_from_file = False
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(
                FILE_STATS_WITH_DATA,
                [
                    {
                        **FILE_STATS_WITH_DATA,
                        "sport_id": None,
                        "is_transition": False,
                    }
                ],
            ),
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
        workout = self.assert_workout_with_calculated_data()
        assert workout.elevation_data_source == ElevationDataSource.FILE

    def test_it_creates_workout_when_stats_are_extracted_from_file(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workout_stats_from_file = True
        segment_file_data = {
            **FILE_STATS_WITH_DATA,
            "sport_id": sport_1_cycling.id,
            "is_transition": False,
        }
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_DATA, [segment_file_data]),
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
        self.assert_data_from_file(workout, FILE_STATS_WITH_DATA)
        assert workout.elevation_data_source == ElevationDataSource.FILE
        segments = workout.segments
        assert len(segments) == 1
        self.assert_data_from_file(segments[0], segment_file_data)

    def test_it_creates_workout_when_stats_are_none(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workout_stats_from_file = True
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_NONE, []),
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
        assert workout.elevation_data_source == ElevationDataSource.FILE
        segments = workout.segments
        assert len(segments) == 1
        assert segments[0].sport_id is None
        assert segments[0].is_transition is False


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutFitServiceProcessFileOnRefresh(
    WorkoutFitServiceProcessFileTestCase, ResponseMockMixin
):
    @pytest.mark.parametrize("input_workout_stats_from_file", [True, False])
    def test_it_refreshes_workout_when_get_elevation_on_refresh_is_False(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_coordinates: "WorkoutSegment",
        input_workout_stats_from_file: bool,
    ) -> None:
        user_1.elevation_data_source = ElevationDataSource.VALHALLA
        user_1.workout_stats_from_file = input_workout_stats_from_file
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.FILE
        )
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_DATA, [FILE_STATS_WITH_DATA]),
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(
                    app_with_open_elevation_and_valhalla_url,
                    file_name="example.fit",
                ),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
                get_elevation_on_refresh=False,
                workout=workout_cycling_user_1_with_coordinates,
            )

        service.process_workout()
        db.session.commit()

        workout = Workout.query.one()
        if input_workout_stats_from_file:
            self.assert_data_from_file(workout, FILE_STATS_WITH_DATA)
        else:
            self.assert_workout_with_calculated_data()
        assert workout.elevation_data_source == ElevationDataSource.FILE
        assert workout.workout_stats_from_file == input_workout_stats_from_file

    @pytest.mark.parametrize("input_workout_stats_from_file", [True, False])
    def test_it_refreshes_workout_when_elevation_parameters_are_provided(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_coordinates: "WorkoutSegment",
        input_workout_stats_from_file: bool,
    ) -> None:
        """
        It ignores 'workout_stats_from_file' when True
        """
        user_1.elevation_data_source = ElevationDataSource.OPEN_ELEVATION
        user_1.workout_stats_from_file = input_workout_stats_from_file
        workout_cycling_user_1_with_coordinates.elevation_data_source = (
            ElevationDataSource.FILE
        )
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_DATA, [FILE_STATS_WITH_DATA]),
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(
                    app_with_open_elevation_and_valhalla_url,
                    file_name="example.fit",
                ),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
                get_elevation_on_refresh=True,
                workout=workout_cycling_user_1_with_coordinates,
                change_elevation_source=ElevationDataSource.VALHALLA,
                elevation_processing=ElevationProcessing.NONE,
            )

        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(VALHALLA_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()
            db.session.commit()

        requests_mock.assert_called()
        workout = Workout.query.one()
        assert float(workout.ascent) == 0.0
        assert float(workout.descent) == 20.0
        assert float(workout.max_alt) == 996.0  # type: ignore
        assert float(workout.min_alt) == 976.0  # type: ignore
        assert workout.elevation_data_source == ElevationDataSource.VALHALLA
        assert workout.elevation_processing == ElevationProcessing.NONE
        assert workout.workout_stats_from_file is False
        assert workout.segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 996.0,
            "latitude": 44.68094998039305,
            "longitude": 6.073670033365488,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }

    def test_it_refreshes_when_changing_workout_from_stats(
        self,
        app_with_open_elevation_and_valhalla_url: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        """
        user refresh workout on UI
        """
        # user preferences
        user_1.elevation_data_source = ElevationDataSource.OPEN_ELEVATION
        user_1.elevation_processing = ElevationProcessing.FLAT_WINDOW
        user_1.process_only_missing_elevations = False
        user_1.workout_stats_from_file = False

        # workout creation with calculated stats smooth elevation from
        # OpenElevation
        service = WorkoutFitService(
            user_1,
            self.get_fit_file_content(
                app_with_open_elevation_and_valhalla_url,
                file_name="example.fit",
            ),
            sport_1_cycling,
            sport_1_cycling.stopped_speed_threshold,
        )
        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()
        db.session.commit()

        requests_mock.assert_called_once()
        workout = Workout.query.one()
        assert workout.elevation_data_source == (
            ElevationDataSource.OPEN_ELEVATION
        )
        assert workout.elevation_processing == (
            ElevationProcessing.FLAT_WINDOW
        )
        assert workout.segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 993,  # smoothed
            "latitude": 44.68094998039305,
            "longitude": 6.073670033365488,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout.segments[0].points[-1] == {
            "distance": 318.1085348379698,
            "duration": 250,
            "elevation": 976,  # smoothed
            "latitude": 44.67821999453008,
            "longitude": 6.074419962242246,
            "pace": 0.8530805687,
            "speed": 4.22,
            "time": "2018-03-13 12:48:55+00:00",
        }

        # change preference in order to get workouts stats from file
        user_1.workout_stats_from_file = True

        # refresh workout
        with patch.object(
            WorkoutFitService,
            "get_file_stats",
            return_value=(FILE_STATS_WITH_DATA, [FILE_STATS_WITH_DATA]),
        ):
            service = WorkoutFitService(
                user_1,
                self.get_fit_file_content(
                    app_with_open_elevation_and_valhalla_url,
                    file_name="example.fit",
                ),
                sport_1_cycling,
                sport_1_cycling.stopped_speed_threshold,
                get_elevation_on_refresh=False,
                workout=workout,
            )
        service.process_workout()
        db.session.commit()

        # refresh workout (data from file)
        db.session.refresh(workout)
        self.assert_data_from_file(workout, FILE_STATS_WITH_DATA)
        assert workout.elevation_data_source == ElevationDataSource.FILE
        assert workout.elevation_processing == ElevationProcessing.NONE
        assert workout.segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 997.0,  # original value
            "latitude": 44.68094998039305,
            "longitude": 6.073670033365488,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout.segments[0].points[-1] == {
            "distance": 318.2150026297633,
            "duration": 250,
            "elevation": 976.0,  # original value
            "latitude": 44.67821999453008,
            "longitude": 6.074419962242246,
            "pace": 0.8470588235,
            "speed": 4.25,
            "time": "2018-03-13 12:48:55+00:00",
        }

        # change preference back to initial values
        user_1.workout_stats_from_file = False

        # refresh workout (data from file, since no refresh on elevation)
        service = WorkoutFitService(
            user_1,
            self.get_fit_file_content(
                app_with_open_elevation_and_valhalla_url,
                file_name="example.fit",
            ),
            sport_1_cycling,
            sport_1_cycling.stopped_speed_threshold,
            get_elevation_on_refresh=False,
            workout=workout,
        )
        with (
            patch.object(
                requests,
                "post",
                return_value=self.get_response(OPEN_ELEVATION_RESPONSE),
            ) as requests_mock,
        ):
            service.process_workout()
        db.session.commit()

        requests_mock.assert_not_called()
        db.session.refresh(workout)
        assert workout.elevation_data_source == ElevationDataSource.FILE
        assert workout.elevation_processing == ElevationProcessing.NONE
        assert workout.segments[0].points[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 997.0,  # original value
            "latitude": 44.68094998039305,
            "longitude": 6.073670033365488,
            "pace": None,
            "speed": 0.0,
            "time": "2018-03-13 12:44:45+00:00",
        }
        assert workout.segments[0].points[-1] == {
            "distance": 318.2150026297633,
            "duration": 250,
            "elevation": 976.0,  # original value
            "latitude": 44.67821999453008,
            "longitude": 6.074419962242246,
            "pace": 0.8470588235,
            "speed": 4.25,
            "time": "2018-03-13 12:48:55+00:00",
        }

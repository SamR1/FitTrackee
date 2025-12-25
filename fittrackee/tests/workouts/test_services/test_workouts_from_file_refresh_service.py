import os
import zipfile
from datetime import datetime, timezone
from logging import getLogger
from typing import TYPE_CHECKING, Dict
from unittest.mock import MagicMock, call, mock_open, patch

import pytest

from fittrackee import db
from fittrackee.constants import MissingElevationsProcessing
from fittrackee.files import get_absolute_file_path
from fittrackee.tests.workouts.mixins import (
    WorkoutAssertMixin,
)
from fittrackee.workouts.exceptions import (
    WorkoutFileException,
    WorkoutRefreshException,
)
from fittrackee.workouts.models import Record, Workout
from fittrackee.workouts.services.elevation.open_elevation_service import (
    OpenElevationService,
)
from fittrackee.workouts.services.weather.base_weather import BaseWeather
from fittrackee.workouts.services.workouts_from_file_refresh_service import (
    WorkoutFromFileRefreshService,
    WorkoutsFromFileRefreshService,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User, UserSportPreference
    from fittrackee.workouts.models import Sport, WorkoutSegment

# files from gpx_test.zip
TEST_FILES_LIST = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]

test_logger = getLogger("test logger")


class TestWorkoutFromFileRefreshServiceInstantiation:
    def test_it_raises_exception_when_workout_has_no_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        with pytest.raises(
            WorkoutRefreshException, match="workout without original file"
        ):
            WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

    def test_it_instantiates_service_when_only_workout_is_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        assert service.original_file == workout_cycling_user_1.original_file
        assert service.workout == workout_cycling_user_1
        assert service.user == user_1
        assert service.sport == sport_1_cycling
        assert service.sport_preferences is None
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.update_weather is False
        assert service.get_elevation_on_refresh is True

    def test_it_instantiates_service_when_user_has_sport_preferences(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        assert service.workout == workout_cycling_user_1
        assert service.user == user_1
        assert service.sport == sport_1_cycling
        assert service.sport_preferences == user_1_sport_1_preference
        assert (
            service.stopped_speed_threshold
            == user_1_sport_1_preference.stopped_speed_threshold
        )
        assert service.update_weather is False
        assert service.get_elevation_on_refresh is True

    def test_it_instantiates_service_when_update_weather_is_true(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        service = WorkoutFromFileRefreshService(
            workout=workout_cycling_user_1, update_weather=True
        )

        assert service.workout == workout_cycling_user_1
        assert service.user == user_1
        assert service.sport == sport_1_cycling
        assert service.sport_preferences is None
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.update_weather is True
        assert service.get_elevation_on_refresh is True

    def test_it_instantiates_service_when_get_elevation_on_refresh_is_false(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        service = WorkoutFromFileRefreshService(
            workout=workout_cycling_user_1, get_elevation_on_refresh=False
        )

        assert service.workout == workout_cycling_user_1
        assert service.user == user_1
        assert service.sport == sport_1_cycling
        assert service.sport_preferences is None
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.update_weather is False
        assert service.get_elevation_on_refresh is False


class TestWorkoutFromFileRefreshServiceGetFileContent:
    def test_it_raises_exception_when_original_file_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        workout_cycling_user_1.original_file = "invalid_file_path.gpx"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with pytest.raises(
            WorkoutFileException, match="error when opening original file"
        ):
            service.get_file_content("gpx")

    def test_it_calls_open_with_original_file_absolute_path(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with patch(
            "builtins.open", new_callable=mock_open, read_data=""
        ) as open_mock:
            service.get_file_content("gpx")

        open_mock.assert_called_once_with(
            get_absolute_file_path(workout_cycling_user_1.original_file),  # type: ignore[arg-type]
            "rb",
        )

    def test_it_returns_original_file_content(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file: str,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_file
        ):
            file_content = service.get_file_content("gpx")

        assert file_content == gpx_file

    def test_it_returns_kmz_file_content_from_zipfile(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file: str,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.kmz"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with patch(
            "fittrackee.workouts.services.workouts_from_file_refresh_service.get_absolute_file_path",
            return_value=os.path.join(
                app.root_path, "tests/files", "example.kmz"
            ),
        ):
            file_content = service.get_file_content("kmz")

        assert isinstance(file_content, zipfile.ZipExtFile)


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutFromFileRefreshServiceRefresh(WorkoutAssertMixin):
    def test_it_raises_exception_when_original_file_extension_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        # this case should not happen
        workout_cycling_user_1.original_file = "workouts/1/example.zip"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with pytest.raises(
            WorkoutRefreshException, match="invalid file extension"
        ):
            service.refresh()

    def test_it_refreshes_data_for_gpx_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file_with_gpxtpx_extensions_and_power: str,
    ) -> None:
        """
        note: workout_cycling_user_1 has no data related to gpx file
        """
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions_and_power,
        ):
            service.refresh()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        self.assert_workout(
            user_1,
            sport_1_cycling,
            workout_cycling_user_1,
            assert_full=False,
        )
        self.assert_workout_with_with_gpxtpx_extensions_and_power(
            workout_cycling_user_1
        )
        self.assert_workout_segment(workout_cycling_user_1)
        records = Record.query.order_by(Record.record_type.asc()).all()
        assert len(records) == 7
        assert records[0].serialize() == {
            "id": 1,
            "record_type": "AP",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": str(workout_cycling_user_1.ave_pace),
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[1].serialize() == {
            "id": 2,
            "record_type": "AS",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.ave_speed),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[2].serialize() == {
            "id": 3,
            "record_type": "BP",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": str(workout_cycling_user_1.best_pace),
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[3].serialize() == {
            "id": 4,
            "record_type": "FD",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.distance),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[4].serialize() == {
            "id": 7,
            "record_type": "HA",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.ascent),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[5].serialize() == {
            "id": 5,
            "record_type": "LD",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": str(workout_cycling_user_1.duration),
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[6].serialize() == {
            "id": 6,
            "record_type": "MS",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.max_speed),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }

    def test_it_calls_weather_service_when_update_weather_is_true(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file: str,
        default_weather_service: MagicMock,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(
            workout=workout_cycling_user_1, update_weather=True
        )

        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_file
        ):
            service.refresh()

        default_weather_service.assert_called()

    def test_it_does_not_call_weather_service_when_workout_has_already_weather_data(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file: str,
        default_weather_service: MagicMock,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        workout_cycling_user_1.weather_start = {
            "icon": "partly-cloudy-day",
            "temperature": 18.9,
            "humidity": 0.47,
            "wind": 2.9166666666666665,
            "windBearing": 17.0,
        }
        workout_cycling_user_1.weather_end = {
            "icon": "partly-cloudy-day",
            "temperature": 19.1,
            "humidity": 0.48,
            "wind": 2.50,
            "windBearing": 14.0,
        }
        service = WorkoutFromFileRefreshService(
            workout=workout_cycling_user_1, update_weather=True
        )

        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_file
        ):
            service.refresh()

        default_weather_service.assert_not_called()

    @pytest.mark.disable_autouse_default_weather_service
    def test_it_does_not_remove_weather_when_weather_service_returns_none(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file: str,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        weather_start = {
            "icon": "partly-cloudy-day",
            "temperature": 18.9,
            "humidity": 0.47,
            "wind": 2.9166666666666665,
            "windBearing": 17.0,
        }
        weather_end = {
            "icon": "partly-cloudy-day",
            "temperature": 19.1,
            "humidity": 0.48,
            "wind": 2.50,
            "windBearing": 14.0,
        }
        workout_cycling_user_1.weather_start = weather_start
        workout_cycling_user_1.weather_end = weather_end
        with (
            patch("builtins.open", new_callable=mock_open, read_data=gpx_file),
            patch.object(BaseWeather, "get_weather", return_value=None),
        ):
            service = WorkoutFromFileRefreshService(
                workout=workout_cycling_user_1, update_weather=True
            )

            service.refresh()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.weather_start == weather_start
        assert workout_cycling_user_1.weather_end == weather_end

    def test_it_calls_elevation_service_when_get_elevation_on_refresh_is_true(
        self,
        app_with_open_elevation_url: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file_without_elevation: str,
        default_weather_service: MagicMock,
    ) -> None:
        user_1.missing_elevations_processing = (
            MissingElevationsProcessing.OPEN_ELEVATION
        )
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(
            workout=workout_cycling_user_1, get_elevation_on_refresh=True
        )

        with (
            patch(
                "builtins.open",
                new_callable=mock_open,
                read_data=gpx_file_without_elevation,
            ),
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as elevation_service_mock,
        ):
            service.refresh()

        elevation_service_mock.assert_called_once()

    def test_it_does_not_call_elevation_service_when_get_elevation_on_refresh_is_false(  # noqa
        self,
        app_with_open_elevation_url: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file_without_elevation: str,
        default_weather_service: MagicMock,
    ) -> None:
        user_1.missing_elevations_processing = (
            MissingElevationsProcessing.OPEN_ELEVATION
        )
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(
            workout=workout_cycling_user_1, get_elevation_on_refresh=False
        )

        with (
            patch(
                "builtins.open",
                new_callable=mock_open,
                read_data=gpx_file_without_elevation,
            ),
            patch.object(
                OpenElevationService, "get_elevations", return_value=[]
            ) as elevation_service_mock,
        ):
            service.refresh()

        elevation_service_mock.assert_not_called()

    def test_it_returns_workout(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
        gpx_file_from_tcx_with_one_lap_and_one_track: str,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.tcx"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)
        open_mock = mock_open(read_data=tcx_with_one_lap_and_one_track)

        with patch("builtins.open", open_mock):
            updated_workout = service.refresh()

        assert isinstance(updated_workout, Workout)

    def test_it_refreshes_workout_with_equipment(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
        gpx_file_from_tcx_with_one_lap_and_one_track: str,
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.tcx"
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)
        open_mock = mock_open(read_data=tcx_with_one_lap_and_one_track)

        with patch("builtins.open", open_mock):
            service.refresh()

        db.session.refresh(equipment_bike_user_1)
        assert (
            equipment_bike_user_1.total_distance
            == workout_cycling_user_1.distance
        )
        assert (
            equipment_bike_user_1.total_duration
            == workout_cycling_user_1.duration
        )
        assert (
            equipment_bike_user_1.total_moving == workout_cycling_user_1.moving
        )
        assert equipment_bike_user_1.total_workouts == 1


class TestWorkoutsFromFileRefreshServiceInstantiation:
    def test_it_instantiates_service_when_no_values_provided(
        self, app: "Flask"
    ) -> None:
        service = WorkoutsFromFileRefreshService(logger=test_logger)

        assert service.per_page == 10
        assert service.page == 1
        assert service.order == "asc"
        assert service.username is None
        assert service.extension is None
        assert service.sport_id is None
        assert service.date_from is None
        assert service.date_to is None
        assert service.logger == test_logger
        assert service.with_weather is False
        assert service.with_elevation is False

    def test_it_instantiates_service_with_given_values(
        self, app: "Flask"
    ) -> None:
        date_from = datetime(2018, 8, 1, 0, 0, tzinfo=timezone.utc)
        date_to = datetime(2018, 8, 12, 0, 0, tzinfo=timezone.utc)
        service = WorkoutsFromFileRefreshService(
            logger=test_logger,
            per_page=50,
            page=2,
            order="desc",
            user="Test",
            extension=".fit",
            sport_id=1,
            date_from=date_from,
            date_to=date_to,
            with_weather=True,
            with_elevation=True,
        )

        assert service.per_page == 50
        assert service.page == 2
        assert service.order == "desc"
        assert service.username == "Test"
        assert service.extension == ".fit"
        assert service.sport_id == 1
        assert service.date_from == date_from
        assert service.date_to == date_to
        assert service.logger == test_logger
        assert service.with_weather is True
        assert service.with_elevation is True


class TestWorkoutsFromFileRefreshServiceRefresh:
    @pytest.mark.parametrize("input_with_elevation", [True, False])
    @pytest.mark.parametrize("input_with_weather", [True, False])
    def test_it_instantiates_workout_from_file_refresh_service(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        input_with_elevation: bool,
        input_with_weather: bool,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger,
            with_weather=input_with_weather,
            with_elevation=input_with_elevation,
        )

        with patch.object(
            WorkoutFromFileRefreshService, "__init__", return_value=None
        ) as service_init_mock:
            service.refresh()

        service_init_mock.assert_called_once_with(
            workout_cycling_user_1,
            update_weather=input_with_weather,
            get_elevation_on_refresh=input_with_elevation,
        )

    def test_it_returns_0_when_no_workouts_with_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = WorkoutsFromFileRefreshService(logger=test_logger)

        count = service.refresh()

        assert count == 0

    def test_it_calls_workout_from_file_refresh_service_for_each_file(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        workout_cycling_user_2: "Workout",
        workout_cycling_user_2_segment: "WorkoutSegment",
    ) -> None:
        service = WorkoutsFromFileRefreshService(logger=test_logger)

        with patch.object(
            WorkoutFromFileRefreshService, "refresh"
        ) as refresh_mock:
            service.refresh()

        assert refresh_mock.call_count == 2

    def test_it_refreshes_only_user_1_workout(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_cycling_user_2: "Workout",
        workout_cycling_user_2_segment: "WorkoutSegment",
        tcx_with_heart_rate_cadence_and_power: str,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger, user=user_1.username
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_heart_rate_cadence_and_power,
        ):
            count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert float(workout_cycling_user_1.distance) == 0.112  # type: ignore[arg-type]

    def test_it_refreshes_only_workout_with_given_extension(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        workout_cycling_user_1.original_file = "file.gpx"
        service = WorkoutsFromFileRefreshService(
            logger=test_logger, extension=".tcx"
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            count = service.refresh()

        assert count == 1
        db.session.refresh(workout_running_user_1)
        assert float(workout_running_user_1.distance) == 0.318  # type: ignore[arg-type]

    def test_it_refreshes_workout_associated_to_given_sport(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger, sport_id=sport_2_running.id
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            count = service.refresh()

        assert count == 1
        db.session.refresh(workout_running_user_1)
        assert float(workout_running_user_1.distance) == 0.318  # type: ignore[arg-type]

    def test_it_refreshes_workout_date_from_given_date(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger,
            date_from=datetime(2018, 4, 2, 0, 0, tzinfo=timezone.utc),
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            count = service.refresh()

        assert count == 1
        db.session.refresh(workout_running_user_1)
        assert float(workout_running_user_1.distance) == 0.318  # type: ignore[arg-type]

    def test_it_refreshes_workout_to_given_date(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger,
            date_to=datetime(2018, 1, 1, 0, 0, tzinfo=timezone.utc),
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert float(workout_cycling_user_1.distance) == 0.318  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "input_params",
        [
            {"page": 1, "per_page": 1, "order": "asc"},
            {"page": 2, "per_page": 1, "order": "desc"},
        ],
    )
    def test_it_refreshes_workout_depending_on_given_pagination_parameters(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
        input_params: Dict,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger, **input_params
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            count = service.refresh()

        assert count == 1
        db.session.refresh(workout_cycling_user_1)
        assert float(workout_cycling_user_1.distance) == 0.318  # type: ignore[arg-type]

    def test_it_does_not_call_weather_service_when_with_weather_is_false(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
        default_weather_service: MagicMock,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger, with_weather=False
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            service.refresh()

        default_weather_service.assert_not_called()

    def test_it_calls_weather_service_when_with_weather_is_true(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
        default_weather_service: MagicMock,
    ) -> None:
        service = WorkoutsFromFileRefreshService(
            logger=test_logger, with_weather=True
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            service.refresh()

        default_weather_service.assert_called()

    def test_it_displays_logs_when_verbose_is_true(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
    ) -> None:
        logger_mock = MagicMock()
        service = WorkoutsFromFileRefreshService(
            logger=logger_mock, verbose=True
        )

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=tcx_with_one_lap_and_one_track,
        ):
            service.refresh()

        assert logger_mock.info.call_count == 4
        logger_mock.info.assert_has_calls(
            [
                call("Number of workouts to refresh: 2"),
                call("Refreshing workout 1/2..."),
                call("Refreshing workout 2/2..."),
                call(
                    "\nRefresh done:\n"
                    "- updated workouts: 2\n"
                    "- errored workouts: 0"
                ),
            ]
        )

    def test_it_displays_message_when_logger_is_provided_and_no_workouts_to_refresh(  # noqa
        self, app: "Flask"
    ) -> None:
        """A message will be displayed by CLI"""
        logger_mock = MagicMock()
        service = WorkoutsFromFileRefreshService(logger=logger_mock)

        service.refresh()

        assert logger_mock.info.call_count == 1
        logger_mock.info.assert_has_calls([call("No workouts to refresh.")])

    def test_it_continues_on_error(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_running_user_1: "Workout",
        workout_running_user_1_segment: "WorkoutSegment",
        tcx_with_one_lap_and_one_track: str,
        gpx_file_from_tcx_with_one_lap_and_one_track: str,
    ) -> None:
        logger_mock = MagicMock()
        open_mock = MagicMock()
        mock_files = [
            Exception(),
            mock_open(read_data=tcx_with_one_lap_and_one_track).return_value,
            mock_open(
                read_data=gpx_file_from_tcx_with_one_lap_and_one_track
            ).return_value,
        ]
        service = WorkoutsFromFileRefreshService(
            logger=logger_mock, verbose=True
        )

        with patch(
            "builtins.open", return_value=open_mock, side_effect=mock_files
        ):
            count = service.refresh()

        assert count == 1
        assert logger_mock.info.call_count == 4
        logger_mock.info.assert_has_calls(
            [
                call("Number of workouts to refresh: 2"),
                call("Refreshing workout 1/2..."),
                call("Refreshing workout 2/2..."),
                call(
                    "\nRefresh done:\n"
                    "- updated workouts: 1\n"
                    "- errored workouts: 1"
                ),
            ]
        )
        logger_mock.error.assert_has_calls(
            [
                call(
                    "Error when refreshing workout "
                    f"'{workout_cycling_user_1.short_id}' "
                    f"(user: {user_1.username}): "
                    "error when opening original file"
                )
            ]
        )

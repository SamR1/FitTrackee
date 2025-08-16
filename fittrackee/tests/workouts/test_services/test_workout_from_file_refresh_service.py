from typing import TYPE_CHECKING
from unittest.mock import MagicMock, mock_open, patch

import pytest

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.tests.workouts.mixins import (
    WorkoutAssertMixin,
)
from fittrackee.workouts.exceptions import (
    WorkoutFileException,
    WorkoutRefreshException,
)
from fittrackee.workouts.models import Record, Workout
from fittrackee.workouts.services.weather.base_weather import BaseWeather
from fittrackee.workouts.services.workout_from_file_refresh_service import (
    WorkoutFromFileRefreshService,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User, UserSportPreference
    from fittrackee.workouts.models import Sport, WorkoutSegment

# files from gpx_test.zip
TEST_FILES_LIST = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]


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

    def test_it_instantiates_service_when_workout_has_only_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        # for workouts uploaded before FitTrackee v0.10.0
        workout_cycling_user_1.original_file = None

        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.original_file == workout_cycling_user_1.gpx
        )
        assert service.original_file == workout_cycling_user_1.gpx
        assert service.workout == workout_cycling_user_1
        assert service.user == user_1
        assert service.sport == sport_1_cycling
        assert service.sport_preferences is None
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )
        assert service.update_weather is False

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
            service.get_file_content()

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
            service.get_file_content()

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
            file_content = service.get_file_content()

        assert file_content == gpx_file


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
        assert len(records) == 5
        assert records[0].serialize() == {
            "id": 1,
            "record_type": "AS",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.ave_speed),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[1].serialize() == {
            "id": 2,
            "record_type": "FD",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.distance),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[2].serialize() == {
            "id": 5,
            "record_type": "HA",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": float(workout_cycling_user_1.ascent),  # type: ignore
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[3].serialize() == {
            "id": 3,
            "record_type": "LD",
            "sport_id": workout_cycling_user_1.sport_id,
            "user": workout_cycling_user_1.user.username,
            "value": str(workout_cycling_user_1.duration),
            "workout_date": workout_cycling_user_1.workout_date,
            "workout_id": workout_cycling_user_1.short_id,
        }
        assert records[4].serialize() == {
            "id": 4,
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

    def test_it_does_not_store_new_gpx_file_when_file_extensions_is_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        gpx_file_with_gpxtpx_extensions_and_power: str,
    ) -> None:
        workout_cycling_user_1.original_file = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)

        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions_and_power,
        ) as open_mock:
            service.refresh()

        open_mock.assert_called_once()

    def test_it_stores_new_gpx_file_when_file_extensions_is_not_gpx(
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
        workout_cycling_user_1.gpx = "workouts/1/example.gpx"
        service = WorkoutFromFileRefreshService(workout=workout_cycling_user_1)
        open_mock = mock_open(read_data=tcx_with_one_lap_and_one_track)

        with patch("builtins.open", open_mock):
            service.refresh()

        open_mock.assert_called_with(
            get_absolute_file_path(workout_cycling_user_1.gpx), "w"
        )
        handle = open_mock()
        handle.write.assert_called_once_with(
            gpx_file_from_tcx_with_one_lap_and_one_track
        )

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
        workout_cycling_user_1.gpx = "workouts/1/example.gpx"
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
        workout_cycling_user_1.gpx = "workouts/1/example.gpx"
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

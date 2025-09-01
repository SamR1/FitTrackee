from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import IO, TYPE_CHECKING, Dict, Optional
from uuid import UUID

import pytest
from werkzeug.datastructures import FileStorage

from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import WorkoutSegment
from fittrackee.workouts.services.workout_from_file import GpxInfo

from ..mixins import ApiTestCaseMixin

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


@pytest.mark.disable_autouse_update_records_patch
class WorkoutApiTestCaseMixin(ApiTestCaseMixin):
    pass


class WorkoutGpxInfoMixin:
    @staticmethod
    def generate_get_gpx_info_return_value(
        updated_data: Dict,
    ) -> "GpxInfo":
        parsed_data = {
            "duration": 250.0,
            "distance": 0.32012787035769946,
            "moving_time": 250.0,
            "stopped_time": 0.0,
            "max_speed": 5.1165730571530394,
            "max_alt": 998.0,
            "min_alt": 975.0,
            "ascent": 0.39999999999997726,
            "descent": 23.399999999999977,
            **updated_data,
        }
        return GpxInfo(**parsed_data)


class WorkoutFileMixin:
    @staticmethod
    def get_file_storage(
        content: str, file_name: str = "file.gpx"
    ) -> "FileStorage":
        return FileStorage(
            filename=file_name, stream=BytesIO(str.encode(content))
        )

    @staticmethod
    def get_file_content(content: str) -> IO[bytes]:
        return BytesIO(str.encode(content))


class WorkoutAssertMixin:
    @staticmethod
    def assert_workout(
        user: "User",
        sport: "Sport",
        workout: "Workout",
        assert_full: bool = True,
    ) -> None:
        """
        assert workout data from 'gpx_file' fixture
        """
        assert workout.analysis_visibility == VisibilityLevel.PRIVATE
        assert float(workout.ascent) == 0.4  # type: ignore
        assert float(workout.ave_speed) == 4.61  # type: ignore
        assert workout.bounds == [44.67822, 6.07355, 44.68095, 6.07442]
        assert workout.creation_date is not None
        assert float(workout.descent) == 23.4  # type: ignore
        assert workout.description is None
        assert float(workout.distance) == 0.32  # type: ignore
        assert workout.duration == timedelta(minutes=4, seconds=10)
        if assert_full:
            assert workout.gpx is None
        assert workout.map is None
        assert workout.map_id is None
        assert workout.map_visibility == VisibilityLevel.PRIVATE
        assert float(workout.max_alt) == 998.0  # type: ignore
        assert float(workout.max_speed) == 5.12  # type: ignore
        assert float(workout.min_alt) == 975.0  # type: ignore
        assert workout.modification_date is not None
        assert workout.moving == timedelta(minutes=4, seconds=10)
        assert workout.notes is None
        if assert_full:
            assert workout.original_file is None
        assert workout.pauses == timedelta(seconds=0)
        assert workout.sport_id == sport.id
        assert workout.suspended_at is None
        assert workout.title is None
        assert workout.user_id == user.id
        assert workout.weather_start is None
        assert workout.weather_end is None
        if assert_full:
            assert workout.workout_date == datetime(
                2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
            )
        assert workout.workout_visibility == VisibilityLevel.PRIVATE

    @staticmethod
    def assert_workout_segment(
        workout: "Workout", workout_segment: Optional["WorkoutSegment"] = None
    ) -> None:
        """
        assert workout segment data from 'gpx_file' fixture
        """
        assert WorkoutSegment.query.count() == 1
        if workout_segment is None:
            workout_segment = WorkoutSegment.query.one()
        assert workout_segment.workout_id == workout.id
        assert workout_segment.workout_uuid == workout.uuid
        assert workout_segment.segment_id == 0
        assert isinstance(workout_segment.uuid, UUID)
        assert float(workout_segment.ascent) == 0.4  # type: ignore[arg-type]
        assert float(workout_segment.ave_speed) == 4.61  # type: ignore[arg-type]
        assert float(workout_segment.descent) == 23.4  # type: ignore[arg-type]
        assert float(workout_segment.distance) == 0.32  # type: ignore[arg-type]
        assert workout_segment.duration == timedelta(minutes=4, seconds=10)
        assert float(workout_segment.max_alt) == 998.0  # type: ignore[arg-type]
        assert float(workout_segment.max_speed) == 5.12  # type: ignore[arg-type]
        assert float(workout_segment.min_alt) == 975.0  # type: ignore[arg-type]
        assert workout_segment.moving == timedelta(minutes=4, seconds=10)
        assert workout_segment.pauses == timedelta(seconds=0)
        assert workout_segment.start_date == datetime(
            2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
        )

    @staticmethod
    def assert_workout_with_with_gpxtpx_extensions_and_power(
        workout: "Workout",
    ) -> None:
        assert workout.ave_cadence == 52
        assert workout.ave_hr == 85
        assert workout.ave_power == 248
        assert workout.max_cadence == 57
        assert workout.max_hr == 92
        assert workout.max_power == 326
        assert workout.source == "Garmin Connect"

from io import BytesIO
from typing import IO, Dict

import pytest
from werkzeug.datastructures import FileStorage

from fittrackee.workouts.services.workout_from_file import GpxInfo

from ..mixins import ApiTestCaseMixin


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

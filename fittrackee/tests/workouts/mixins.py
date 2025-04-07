from typing import Dict

import pytest

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

from statistics import mean
from typing import List

import pytest

from fittrackee.workouts.utils.workouts import get_average_speed


class TestWorkoutAverageSpeed:
    @pytest.mark.parametrize(
        'ave_speeds_list',
        [
            ([0]),
            ([10]),
            ([0, 0]),
            ([10, 20]),
            ([10, 0, 20, 10]),
            ([1.5, 2, 3.7, 4.2]),
        ],
    )
    def test_it_calculates_average_speed(self, ave_speeds_list: List) -> None:
        nb_workouts = len(ave_speeds_list)
        total_average_speed = (
            sum(ave_speeds_list[:-1]) / (len(ave_speeds_list) - 1)
            if len(ave_speeds_list) > 1
            else ave_speeds_list[0]
        )
        workout_average_speed = ave_speeds_list[-1]

        assert get_average_speed(
            nb_workouts, total_average_speed, workout_average_speed
        ) == mean(ave_speeds_list)

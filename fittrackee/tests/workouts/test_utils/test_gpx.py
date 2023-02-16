from datetime import timedelta
from unittest.mock import call, patch

import pytest
from flask import Flask
from gpxpy.gpx import IGNORE_TOP_SPEED_PERCENTILES, MovingData
from werkzeug.datastructures import FileStorage

from fittrackee.tests.utils import random_string
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Sport
from fittrackee.workouts.utils.workouts import get_gpx_info, process_files

folders = {
    'extract_dir': '/tmp/fitTrackee/uploads',
    'tmp_dir': '/tmp/fitTrackee/uploads/tmp',
}
moving_data = MovingData(
    moving_time=1,
    stopped_time=1,
    moving_distance=1,
    stopped_distance=1,
    max_speed=1,
)


class TestStoppedSpeedThreshold:
    @pytest.mark.parametrize(
        'sport_id, expected_threshold',
        [(1, 1.0), (2, 0.1)],
    )
    def test_it_calls_get_moving_data_with_threshold_depending_on_sport(
        self,
        app: Flask,
        user_1: User,
        gpx_file_storage: FileStorage,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        sport_id: int,
        expected_threshold: float,
    ) -> None:
        with patch(
            'fittrackee.workouts.utils.workouts.get_new_file_path',
            return_value='/tmp/fitTrackee/uploads/test.png',
        ), patch(
            'gpxpy.gpx.GPXTrackSegment.get_moving_data',
            return_value=moving_data,
        ) as gpx_track_segment_mock:
            process_files(
                auth_user=user_1,
                folders=folders,
                workout_data={'sport_id': sport_id},
                workout_file=gpx_file_storage,
            )

        assert gpx_track_segment_mock.call_args_list[0] == call(
            stopped_speed_threshold=expected_threshold
        )
        gpx_track_segment_mock.assert_called_with(
            expected_threshold,  # stopped_speed_threshold
            False,  # raw
            IGNORE_TOP_SPEED_PERCENTILES,  # speed_extreemes_percentiles
            True,  # ignore_nonstandard_distances
        )

    def test_it_calls_get_moving_data_with_threshold_depending_from_user_preference(  # noqa
        self,
        app: Flask,
        user_1: User,
        gpx_file_storage: FileStorage,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        expected_threshold = 0.7
        user_sport_1_preference.stopped_speed_threshold = expected_threshold
        with patch(
            'fittrackee.workouts.utils.workouts.get_new_file_path',
            return_value='/tmp/fitTrackee/uploads/test.png',
        ), patch(
            'gpxpy.gpx.GPXTrackSegment.get_moving_data',
            return_value=moving_data,
        ) as gpx_track_segment_mock:
            process_files(
                auth_user=user_1,
                folders=folders,
                workout_data={'sport_id': sport_1_cycling.id},
                workout_file=gpx_file_storage,
            )

        assert gpx_track_segment_mock.call_args_list[0] == call(
            stopped_speed_threshold=expected_threshold
        )
        gpx_track_segment_mock.assert_called_with(
            expected_threshold,  # stopped_speed_threshold
            False,  # raw
            IGNORE_TOP_SPEED_PERCENTILES,  # speed_extreemes_percentiles
            True,  # ignore_nonstandard_distances
        )


class TestGetGpxInfoStopTime:
    def test_stop_time_equals_to_0_when_gpx_file_contains_one_segment(
        self, gpx_file: str
    ) -> None:
        """
        stopped_speed_threshold to 0 to avoid calculated stopped time
        in segments
        """
        with patch('builtins.open', return_value=gpx_file):
            gpx_data, _, _ = get_gpx_info(
                gpx_file=random_string(), stopped_speed_threshold=0.0
            )

        assert gpx_data['stop_time'] == timedelta(seconds=0)

    def test_stop_time_equals_to_stopped_time_sum_between_all_segments(
        self, gpx_file_with_3_segments: str
    ) -> None:
        """
        stopped_speed_threshold to 0 to avoid calculated stopped time
        in segments
        """
        with patch('builtins.open', return_value=gpx_file_with_3_segments):
            gpx_data, _, _ = get_gpx_info(
                gpx_file=random_string(), stopped_speed_threshold=0.0
            )

        assert gpx_data['stop_time'] == timedelta(seconds=120)

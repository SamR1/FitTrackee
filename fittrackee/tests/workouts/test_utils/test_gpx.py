from datetime import datetime, timedelta, timezone
from unittest.mock import call, mock_open, patch

import pytest
from flask import Flask
from gpxpy.gpx import IGNORE_TOP_SPEED_PERCENTILES, MovingData
from werkzeug.datastructures import FileStorage

from fittrackee.tests.utils import random_string
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Sport
from fittrackee.workouts.utils.gpx import get_chart_data, get_gpx_info
from fittrackee.workouts.utils.workouts import process_files

folders = {
    "extract_dir": "/tmp/fitTrackee/uploads",
    "tmp_dir": "/tmp/fitTrackee/uploads/tmp",
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
        "sport_id, expected_threshold",
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
        with (
            patch(
                "fittrackee.workouts.utils.workouts.get_new_file_path",
                return_value="/tmp/fitTrackee/uploads/test.png",
            ),
            patch(
                "gpxpy.gpx.GPXTrackSegment.get_moving_data",
                return_value=moving_data,
            ) as gpx_track_segment_mock,
        ):
            process_files(
                auth_user=user_1,
                folders=folders,
                workout_data={"sport_id": sport_id},
                workout_file=gpx_file_storage,
            )

        assert gpx_track_segment_mock.call_args_list[0] == call(
            stopped_speed_threshold=expected_threshold, raw=False
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
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        expected_threshold = 0.7
        user_1_sport_1_preference.stopped_speed_threshold = expected_threshold
        with (
            patch(
                "fittrackee.workouts.utils.workouts.get_new_file_path",
                return_value="/tmp/fitTrackee/uploads/test.png",
            ),
            patch(
                "gpxpy.gpx.GPXTrackSegment.get_moving_data",
                return_value=moving_data,
            ) as gpx_track_segment_mock,
        ):
            process_files(
                auth_user=user_1,
                folders=folders,
                workout_data={"sport_id": sport_1_cycling.id},
                workout_file=gpx_file_storage,
            )

        assert gpx_track_segment_mock.call_args_list[0] == call(
            stopped_speed_threshold=expected_threshold, raw=False
        )
        gpx_track_segment_mock.assert_called_with(
            expected_threshold,  # stopped_speed_threshold
            False,  # raw
            IGNORE_TOP_SPEED_PERCENTILES,  # speed_extreemes_percentiles
            True,  # ignore_nonstandard_distances
        )


class TestUseRawGpxSpeed:
    @pytest.mark.parametrize("input_use_raw_gpx_speed", [True, False])
    def test_it_calls_get_moving_data_with_user_use_raw_gpx_speed_preference(
        self,
        app: Flask,
        user_1: User,
        gpx_file_storage: FileStorage,
        sport_1_cycling: Sport,
        input_use_raw_gpx_speed: bool,
    ) -> None:
        user_1.use_raw_gpx_speed = input_use_raw_gpx_speed
        with (
            patch(
                "fittrackee.workouts.utils.workouts.get_new_file_path",
                return_value="/tmp/fitTrackee/uploads/test.png",
            ),
            patch(
                "gpxpy.gpx.GPXTrackSegment.get_moving_data",
                return_value=moving_data,
            ) as gpx_track_segment_mock,
        ):
            process_files(
                auth_user=user_1,
                folders=folders,
                workout_data={"sport_id": sport_1_cycling.id},
                workout_file=gpx_file_storage,
            )

        assert gpx_track_segment_mock.call_args_list[0] == call(
            stopped_speed_threshold=sport_1_cycling.stopped_speed_threshold,
            raw=input_use_raw_gpx_speed,
        )
        gpx_track_segment_mock.assert_called_with(
            sport_1_cycling.stopped_speed_threshold,  # stopped_speed_threshold
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
        with patch("builtins.open", return_value=gpx_file):
            gpx_data, _, _ = get_gpx_info(
                gpx_file=random_string(), stopped_speed_threshold=0.0
            )

        assert gpx_data["stop_time"] == timedelta(seconds=0)

    def test_stop_time_equals_to_stopped_time_sum_between_all_segments(
        self, gpx_file_with_3_segments: str
    ) -> None:
        """
        stopped_speed_threshold to 0 to avoid calculated stopped time
        in segments
        """
        with patch("builtins.open", return_value=gpx_file_with_3_segments):
            gpx_data, _, _ = get_gpx_info(
                gpx_file=random_string(), stopped_speed_threshold=0.0
            )

        assert gpx_data["stop_time"] == timedelta(seconds=120)


class TestGetChartData:
    def test_it_returns_none_when_gpx_has_no_tracks(
        self, gpx_file_wo_track: str
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_wo_track,
        ):
            chart_data = get_chart_data(gpx_file_wo_track)

        assert chart_data is None

    def test_it_returns_chart_data_for_gpx(self, gpx_file: str) -> None:
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_file
        ):
            chart_data = get_chart_data(gpx_file)

        assert chart_data is not None
        assert chart_data[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": datetime(2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc),
        }
        assert chart_data[-1] == {
            "distance": 0.32,
            "duration": 250.0,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": datetime(2018, 3, 13, 12, 48, 55, tzinfo=timezone.utc),
        }

    def test_it_returns_chart_data_for_segment(
        self, gpx_file_with_3_segments: str
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_3_segments,
        ):
            chart_data = get_chart_data(gpx_file_with_3_segments, 1)

        assert chart_data is not None
        assert chart_data[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": datetime(2018, 3, 13, 12, 44, 50, tzinfo=timezone.utc),
        }
        assert chart_data[-1] == {
            "distance": 0.02,
            "duration": 10.0,
            "elevation": 994.0,
            "latitude": 44.6808,
            "longitude": 6.07364,
            "speed": 9.43,
            "time": datetime(2018, 3, 13, 12, 45, 0, tzinfo=timezone.utc),
        }

    def test_it_returns_chart_data_when_gpx_file_contains_microseconds(
        self, gpx_file_with_microseconds: str
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_microseconds,
        ):
            chart_data = get_chart_data(gpx_file_with_microseconds)

        assert chart_data is not None
        assert chart_data[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.13,
            "time": datetime(
                2018, 3, 13, 13, 44, 45, 787000, tzinfo=timezone.utc
            ),
        }
        assert chart_data[-1] == {
            "distance": 0.32,
            "duration": 250.0,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.34,
            "time": datetime(
                2018, 3, 13, 13, 48, 55, 891000, tzinfo=timezone.utc
            ),
        }

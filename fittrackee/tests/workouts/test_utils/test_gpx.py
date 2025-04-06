from datetime import datetime, timezone
from unittest.mock import mock_open, patch

from fittrackee.workouts.utils.gpx import get_chart_data


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

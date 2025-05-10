from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, Optional
from unittest.mock import mock_open, patch

from fittrackee.workouts.utils.gpx import get_chart_data

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.workouts.models import Sport


class TestGetChartData:
    def test_it_returns_none_when_gpx_has_no_tracks(
        self, app: "Flask", gpx_file_wo_track: str, sport_1_cycling: "Sport"
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_wo_track,
        ):
            chart_data = get_chart_data(
                gpx_file_wo_track,
                sport_1_cycling.label,
                can_see_heart_rate=True,
            )

        assert chart_data is None

    def test_it_returns_chart_data_for_gpx(
        self, app: "Flask", gpx_file: str, sport_1_cycling: "Sport"
    ) -> None:
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_file
        ):
            chart_data = get_chart_data(
                gpx_file, sport_1_cycling.label, can_see_heart_rate=True
            )

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
        self,
        app: "Flask",
        gpx_file_with_3_segments: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_3_segments,
        ):
            chart_data = get_chart_data(
                gpx_file_with_3_segments,
                sport_1_cycling.label,
                can_see_heart_rate=True,
                segment_id=1,
            )

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
        self,
        app: "Flask",
        gpx_file_with_microseconds: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_microseconds,
        ):
            chart_data = get_chart_data(
                gpx_file_with_microseconds,
                sport_1_cycling.label,
                can_see_heart_rate=True,
            )

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

    @staticmethod
    def assert_chart_data(chart_data: Optional[List[Dict]]) -> None:
        assert chart_data is not None
        assert chart_data[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "hr": 92,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": datetime(2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc),
        }
        assert chart_data[-1] == {
            "cadence": 50,
            "distance": 0.32,
            "duration": 250.0,
            "elevation": 975.0,
            "hr": 81,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": datetime(2018, 3, 13, 12, 48, 55, tzinfo=timezone.utc),
        }

    def test_it_returns_chart_data_for_gpx_with_gpxtx_extensions(
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data(
                gpx_file_with_gpxtpx_extensions,
                sport_1_cycling.label,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_for_gpx_with_ns3_extensions(
        self,
        app: "Flask",
        gpx_file_with_ns3_extensions: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_ns3_extensions,
        ):
            chart_data = get_chart_data(
                gpx_file_with_ns3_extensions,
                sport_1_cycling.label,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_for_gpx_file_without_track_point_extension(
        self,
        app: "Flask",
        gpx_file_without_track_point_extension: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_without_track_point_extension,
        ):
            chart_data = get_chart_data(
                gpx_file_without_track_point_extension,
                sport_1_cycling.label,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_for_gpx_file_with_power_before_track_point_extension(  # noqa
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions_and_power: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions_and_power,
        ):
            chart_data = get_chart_data(
                gpx_file_with_gpxtpx_extensions_and_power,
                sport_1_cycling.label,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_does_not_return_cadence_when_sport_is_not_valid(
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions: str,
        sport_4_paragliding: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data(
                gpx_file_with_gpxtpx_extensions,
                sport_4_paragliding.label,
                can_see_heart_rate=True,
            )

        assert chart_data is not None
        assert chart_data[0] == {
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "hr": 92,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": datetime(2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc),
        }
        assert chart_data[-1] == {
            "distance": 0.32,
            "duration": 250.0,
            "elevation": 975.0,
            "hr": 81,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": datetime(2018, 3, 13, 12, 48, 55, tzinfo=timezone.utc),
        }

    def test_it_does_not_returns_heart_rate_when_flag_is_false(
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions: str,
        sport_1_cycling: "Sport",
    ) -> None:
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data(
                gpx_file_with_gpxtpx_extensions,
                sport_1_cycling.label,
                can_see_heart_rate=False,
            )

        assert chart_data is not None
        assert chart_data[0] == {
            "cadence": 0,
            "distance": 0.0,
            "duration": 0,
            "elevation": 998.0,
            "latitude": 44.68095,
            "longitude": 6.07367,
            "speed": 3.21,
            "time": datetime(2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc),
        }
        assert chart_data[-1] == {
            "cadence": 50,
            "distance": 0.32,
            "duration": 250.0,
            "elevation": 975.0,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": datetime(2018, 3, 13, 12, 48, 55, tzinfo=timezone.utc),
        }

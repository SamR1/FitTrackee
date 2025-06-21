from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, Optional
from unittest.mock import mock_open, patch

import pytest

from fittrackee.workouts.exceptions import WorkoutGPXException
from fittrackee.workouts.utils.gpx import (
    get_chart_data,
    get_chart_data_from_gpx,
    get_chart_data_from_segment_points,
    get_geojson_from_segments,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout, WorkoutSegment


class TestGetChartDataFromGpx:
    def test_it_returns_none_when_gpx_has_no_tracks(
        self, app: "Flask", gpx_file_wo_track: str, sport_1_cycling: "Sport"
    ) -> None:
        workout_ave_cadence = None
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_wo_track,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_wo_track,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

        assert chart_data is None

    def test_it_returns_chart_data_for_gpx(
        self, app: "Flask", gpx_file: str, sport_1_cycling: "Sport"
    ) -> None:
        workout_ave_cadence = None
        with patch(
            "builtins.open", new_callable=mock_open, read_data=gpx_file
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
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
        workout_ave_cadence = None
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_3_segments,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_3_segments,
                sport_1_cycling.label,
                workout_ave_cadence,
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
        workout_ave_cadence = None
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_microseconds,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_microseconds,
                sport_1_cycling.label,
                workout_ave_cadence,
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
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_gpxtpx_extensions,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_for_gpx_with_cadence_float_value(
        self,
        app: "Flask",
        gpx_file_with_cadence_float_value: str,
        sport_1_cycling: "Sport",
    ) -> None:
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_cadence_float_value,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_cadence_float_value,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_without_cadence_when_no_ave_cadence(
        self,
        app: "Flask",
        gpx_file_with_cadence_zero_values: str,
        sport_1_cycling: "Sport",
    ) -> None:
        workout_ave_cadence = None
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_cadence_zero_values,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_cadence_zero_values,
                sport_1_cycling.label,
                workout_ave_cadence,
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

    def test_it_returns_chart_data_for_gpx_with_ns3_extensions(
        self,
        app: "Flask",
        gpx_file_with_ns3_extensions: str,
        sport_1_cycling: "Sport",
    ) -> None:
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_ns3_extensions,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_ns3_extensions,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_for_gpx_file_without_track_point_extension(
        self,
        app: "Flask",
        gpx_file_without_track_point_extension: str,
        sport_1_cycling: "Sport",
    ) -> None:
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_without_track_point_extension,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_without_track_point_extension,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_chart_data_for_gpx_file_with_power_before_track_point_extension(  # noqa
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions_and_power: str,
        sport_1_cycling: "Sport",
    ) -> None:
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions_and_power,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_gpxtpx_extensions_and_power,
                sport_1_cycling.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

        self.assert_chart_data(chart_data)

    def test_it_returns_cadence_when_sport_is_running(
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions: str,
        sport_2_running: "Sport",
    ) -> None:
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_gpxtpx_extensions,
                sport_2_running.label,
                workout_ave_cadence,
                can_see_heart_rate=True,
            )

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
            "cadence": 100,
            "distance": 0.32,
            "duration": 250.0,
            "elevation": 975.0,
            "hr": 81,
            "latitude": 44.67822,
            "longitude": 6.07442,
            "speed": 4.33,
            "time": datetime(2018, 3, 13, 12, 48, 55, tzinfo=timezone.utc),
        }

    def test_it_does_not_return_cadence_when_sport_is_not_valid(
        self,
        app: "Flask",
        gpx_file_with_gpxtpx_extensions: str,
        sport_4_paragliding: "Sport",
    ) -> None:
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_gpxtpx_extensions,
                sport_4_paragliding.label,
                workout_ave_cadence,
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
        workout_ave_cadence = 70
        with patch(
            "builtins.open",
            new_callable=mock_open,
            read_data=gpx_file_with_gpxtpx_extensions,
        ):
            chart_data = get_chart_data_from_gpx(
                gpx_file_with_gpxtpx_extensions,
                sport_1_cycling.label,
                workout_ave_cadence,
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


class TestGetGeojsonFromSegments:
    def test_it_returns_none_when_no_geometry(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        geojson = get_geojson_from_segments(workout_cycling_user_1)

        assert geojson is None

    def test_it_returns_geojson_for_workout_when_workout_has_only_one_segment(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_cycling_user_1_segment_2: "WorkoutSegment",
    ) -> None:
        segment_1_coordinates = [
            [6.07367, 44.68095],
            [6.07367, 44.68091],
            [6.07364, 44.6808],
            [6.07361, 44.68049],
        ]
        workout_cycling_user_1_segment.store_geometry(segment_1_coordinates)
        segment_2_coordinates = [
            [6.07361, 44.68049],
            [6.07364, 44.6808],
            [6.07367, 44.68091],
            [6.07367, 44.68095],
        ]
        workout_cycling_user_1_segment_2.store_geometry(segment_2_coordinates)

        geojson = get_geojson_from_segments(workout_cycling_user_1)

        assert geojson == {
            "type": "MultiLineString",
            "coordinates": [segment_1_coordinates, segment_2_coordinates],
        }

    def test_it_returns_geojson_for_workout_when_workout_has_more_than_one_segment(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_cycling_user_1_segment_2: "WorkoutSegment",
    ) -> None:
        segment_1_coordinates = [
            [6.07367, 44.68095],
            [6.07367, 44.68091],
            [6.07364, 44.6808],
            [6.07361, 44.68049],
        ]
        workout_cycling_user_1_segment.store_geometry(segment_1_coordinates)
        segment_2_coordinates = [
            [6.07361, 44.68049],
            [6.07364, 44.6808],
            [6.07367, 44.68091],
            [6.07367, 44.68095],
        ]
        workout_cycling_user_1_segment_2.store_geometry(segment_2_coordinates)

        geojson = get_geojson_from_segments(
            workout_cycling_user_1,
        )

        assert geojson == {
            "type": "MultiLineString",
            "coordinates": [segment_1_coordinates, segment_2_coordinates],
        }

    def test_it_returns_geojson_for_a_given_segment(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
        workout_cycling_user_1_segment_2: "WorkoutSegment",
    ) -> None:
        segments_coordinates = [
            [6.07367, 44.68095],
            [6.07367, 44.68091],
            [6.07364, 44.6808],
            [6.07361, 44.68049],
        ]
        workout_cycling_user_1_segment_2.store_geometry(segments_coordinates)

        geojson = get_geojson_from_segments(
            workout_cycling_user_1,
            segment_id=workout_cycling_user_1_segment_2.segment_id,
        )

        assert geojson == {
            "type": "LineString",
            "coordinates": segments_coordinates,
        }

    def test_it_returns_none_when_segment_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        geojson = get_geojson_from_segments(
            workout_cycling_user_1, segment_id=2
        )

        assert geojson is None


class TestGetChartDataFromSegmentPoints:
    def test_it_returns_empty_list_when_no_segments(
        self, app: "Flask", sport_1_cycling: "Sport"
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [],
            sport_1_cycling.label,
            workout_ave_cadence=None,
            can_see_heart_rate=True,
        )

        assert chart_data == []

    def test_it_returns_empty_list_when_no_segment_points(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment],
            sport_1_cycling.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
        )

        assert chart_data == []

    def test_it_returns_chart_data_for_one_segment(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment_0_with_coordinates],
            sport_1_cycling.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
        )

        assert len(chart_data) == len(
            workout_cycling_user_1_segment_0_with_coordinates.points
        )
        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "cadence": first_point["cadence"],
            "distance": first_point["distance"],
            "duration": 0,
            "elevation": first_point["elevation"],
            "hr": first_point["heart_rate"],
            "latitude": first_point["latitude"],
            "longitude": first_point["longitude"],
            "speed": first_point["speed"],
            "time": first_point["time"],
        }
        last_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            -1
        ]
        assert chart_data[-1] == {
            "cadence": last_point["cadence"],
            "distance": 0.11,
            "duration": last_point["duration"],
            "elevation": last_point["elevation"],
            "hr": last_point["heart_rate"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }

    def test_it_returns_chart_data_for_segments(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [
                workout_cycling_user_1_segment_0_with_coordinates,
                workout_cycling_user_1_segment_1_with_coordinates,
            ],
            sport_1_cycling.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
        )

        assert len(chart_data) == len(
            workout_cycling_user_1_segment_0_with_coordinates.points
            + workout_cycling_user_1_segment_1_with_coordinates.points
        )
        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "cadence": first_point["cadence"],
            "distance": first_point["distance"],
            "duration": 0,
            "elevation": first_point["elevation"],
            "hr": first_point["heart_rate"],
            "latitude": first_point["latitude"],
            "longitude": first_point["longitude"],
            "speed": first_point["speed"],
            "time": first_point["time"],
        }
        last_point = workout_cycling_user_1_segment_1_with_coordinates.points[
            -1
        ]
        assert chart_data[-1] == {
            "cadence": last_point["cadence"],
            "distance": 0.41,
            "duration": last_point["duration"],
            "elevation": last_point["elevation"],
            "hr": last_point["heart_rate"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }

    def test_it_does_not_return_heart_rate_when_flag_is_false(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment_0_with_coordinates],
            sport_1_cycling.label,
            workout_ave_cadence=70,
            can_see_heart_rate=False,
        )

        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "cadence": first_point["cadence"],
            "distance": first_point["distance"],
            "duration": 0,
            "elevation": first_point["elevation"],
            "latitude": first_point["latitude"],
            "longitude": first_point["longitude"],
            "speed": first_point["speed"],
            "time": first_point["time"],
        }
        last_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            -1
        ]
        assert chart_data[-1] == {
            "cadence": last_point["cadence"],
            "distance": 0.11,
            "duration": last_point["duration"],
            "elevation": last_point["elevation"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }

    def test_it_does_not_return_cadence_when_sport_is_not_associated_with_cadence(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_4_paragliding: "Sport",
        user_1: "User",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment_0_with_coordinates],
            sport_4_paragliding.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
        )

        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "distance": first_point["distance"],
            "duration": 0,
            "elevation": first_point["elevation"],
            "hr": first_point["heart_rate"],
            "latitude": first_point["latitude"],
            "longitude": first_point["longitude"],
            "speed": first_point["speed"],
            "time": first_point["time"],
        }
        last_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            -1
        ]
        assert chart_data[-1] == {
            "distance": 0.11,
            "duration": last_point["duration"],
            "elevation": last_point["elevation"],
            "hr": last_point["heart_rate"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }

    def test_it_does_not_return_cadence_when_ave_cadence_equals_0(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_4_paragliding: "Sport",
        user_1: "User",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment_0_with_coordinates],
            sport_4_paragliding.label,
            workout_ave_cadence=0,
            can_see_heart_rate=True,
        )

        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "distance": first_point["distance"],
            "duration": 0,
            "elevation": first_point["elevation"],
            "hr": first_point["heart_rate"],
            "latitude": first_point["latitude"],
            "longitude": first_point["longitude"],
            "speed": first_point["speed"],
            "time": first_point["time"],
        }
        last_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            -1
        ]
        assert chart_data[-1] == {
            "distance": 0.11,
            "duration": last_point["duration"],
            "elevation": last_point["elevation"],
            "hr": last_point["heart_rate"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }


class TestGetChartData:
    def test_it_raises_error_when_no_segments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        with pytest.raises(WorkoutGPXException, match="No segments"):
            get_chart_data(
                workout_cycling_user_1,
                can_see_heart_rate=True,
            )

    def test_it_raises_error_when_segment_id_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        with pytest.raises(WorkoutGPXException, match="Incorrect segment id"):
            get_chart_data(
                workout_cycling_user_1, can_see_heart_rate=True, segment_id=0
            )

    def test_it_raises_error_when_segment_not_found(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        with pytest.raises(
            WorkoutGPXException, match="No segment with id '9999'"
        ):
            get_chart_data(
                workout_cycling_user_1,
                can_see_heart_rate=True,
                segment_id=9999,
            )

    def test_it_returns_empty_list_when_no_points_and_not_gpx(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data(
            workout_cycling_user_1,
            can_see_heart_rate=True,
        )

        assert chart_data == []

    def test_it_calls_get_chart_data_from_gpx_when_no_points(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        workout_cycling_user_1.gpx = "some/file.gpx"
        with patch(
            "fittrackee.workouts.utils.gpx.get_chart_data_from_gpx"
        ) as get_chart_data_from_gpx_mock:
            get_chart_data(
                workout_cycling_user_1,
                can_see_heart_rate=True,
            )

        get_chart_data_from_gpx_mock.assert_called_once_with(
            f"{app.config['UPLOAD_FOLDER']}/{workout_cycling_user_1.gpx}",
            workout_cycling_user_1.sport.label,
            workout_cycling_user_1.ave_cadence,
            can_see_heart_rate=True,
            segment_id=None,
        )

    def test_it_calls_get_chart_data_from_gpx_with_segment_id_and_no_points(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        workout_cycling_user_1.gpx = "some/file.gpx"
        with patch(
            "fittrackee.workouts.utils.gpx.get_chart_data_from_gpx"
        ) as get_chart_data_from_gpx_mock:
            get_chart_data(
                workout_cycling_user_1,
                can_see_heart_rate=True,
                segment_id=1,
            )

        get_chart_data_from_gpx_mock.assert_called_once_with(
            f"{app.config['UPLOAD_FOLDER']}/{workout_cycling_user_1.gpx}",
            workout_cycling_user_1.sport.label,
            workout_cycling_user_1.ave_cadence,
            can_see_heart_rate=True,
            segment_id=1,
        )

    def test_it_calls_get_chart_data_from_segment_points_when_segments_have_points(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
    ) -> None:
        with patch(
            "fittrackee.workouts.utils.gpx.get_chart_data_from_segment_points"
        ) as get_chart_data_from_segment_points_mock:
            get_chart_data(
                workout_cycling_user_1_with_coordinates,
                can_see_heart_rate=True,
            )
        get_chart_data_from_segment_points_mock.assert_called_once_with(
            [
                workout_cycling_user_1_segment_0_with_coordinates,
                workout_cycling_user_1_segment_1_with_coordinates,
            ],
            workout_cycling_user_1_with_coordinates.sport.label,
            workout_ave_cadence=None,
            can_see_heart_rate=True,
        )

    def test_it_calls_get_chart_data_from_segment_points_with_segment_id(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        with patch(
            "fittrackee.workouts.utils.gpx.get_chart_data_from_segment_points"
        ) as get_chart_data_from_segment_points_mock:
            get_chart_data(
                workout_cycling_user_1_with_coordinates,
                can_see_heart_rate=True,
                segment_id=1,
            )
        get_chart_data_from_segment_points_mock.assert_called_once_with(
            [workout_cycling_user_1_segment_0_with_coordinates],
            workout_cycling_user_1_with_coordinates.sport.label,
            workout_ave_cadence=None,
            can_see_heart_rate=True,
        )

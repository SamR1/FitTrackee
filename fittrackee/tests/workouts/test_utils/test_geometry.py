from typing import TYPE_CHECKING

import pytest

from fittrackee.workouts.exceptions import (
    InvalidCoordinatesException,
    InvalidRadiusException,
    WorkoutException,
)
from fittrackee.workouts.utils.geometry import (
    get_buffered_location,
    get_chart_data_from_segment_points,
    get_geojson_from_segment,
    get_geojson_from_segments,
)

from ...mixins import GeometryMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout, WorkoutSegment


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
    ) -> None:
        segment_1_coordinates = [
            [6.07367, 44.68095],
            [6.07367, 44.68091],
            [6.07364, 44.6808],
            [6.07361, 44.68049],
        ]
        workout_cycling_user_1_segment.store_geometry(segment_1_coordinates)
        geojson = get_geojson_from_segments(workout_cycling_user_1)

        assert geojson == {
            "type": "LineString",
            "coordinates": segment_1_coordinates,
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


class TestGetGeojsonFromSegment:
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

        geojson = get_geojson_from_segment(
            workout_cycling_user_1,
            segment_id=workout_cycling_user_1_segment_2.segment_id + 1,
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
        geojson = get_geojson_from_segment(
            workout_cycling_user_1, segment_id=2
        )

        assert geojson is None

    def test_it_raises_exception_when_segment_id_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
        workout_cycling_user_1_segment: "WorkoutSegment",
    ) -> None:
        with pytest.raises(WorkoutException, match="Incorrect segment id"):
            get_geojson_from_segment(workout_cycling_user_1, segment_id=-1)


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
            [workout_cycling_user_1_segment.points],
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
            [workout_cycling_user_1_segment_0_with_coordinates.points],
            sport_1_cycling.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
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
            "power": first_point["power"],
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
            "power": last_point["power"],
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
                workout_cycling_user_1_segment_0_with_coordinates.points,
                workout_cycling_user_1_segment_1_with_coordinates.points,
            ],
            sport_1_cycling.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
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
            "power": first_point["power"],
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
            "power": last_point["power"],
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
            [workout_cycling_user_1_segment_0_with_coordinates.points],
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
            "power": first_point["power"],
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
            "power": last_point["power"],
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
            [workout_cycling_user_1_segment_0_with_coordinates.points],
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
            [workout_cycling_user_1_segment_0_with_coordinates.points],
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

    def test_it_does_not_return_elevation_when_sport_is_outdoor_tennis(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_5_outdoor_tennis: "Sport",
        user_1: "User",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment_0_with_coordinates.points],
            sport_5_outdoor_tennis.label,
            workout_ave_cadence=70,
            can_see_heart_rate=True,
        )

        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "distance": first_point["distance"],
            "duration": 0,
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
            "hr": last_point["heart_rate"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }

    def test_it_does_not_return_power_when_sport_is_not_associated_with_power(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        chart_data = get_chart_data_from_segment_points(
            [workout_cycling_user_1_segment_0_with_coordinates.points],
            sport_2_running.label,
            workout_ave_cadence=140,
            can_see_heart_rate=True,
        )

        first_point = workout_cycling_user_1_segment_0_with_coordinates.points[
            0
        ]
        assert chart_data[0] == {
            "cadence": 0,
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
            "cadence": 106,
            "distance": 0.11,
            "duration": last_point["duration"],
            "elevation": last_point["elevation"],
            "hr": last_point["heart_rate"],
            "latitude": last_point["latitude"],
            "longitude": last_point["longitude"],
            "speed": last_point["speed"],
            "time": last_point["time"],
        }


class TestGetBufferedLocation(GeometryMixin):
    @pytest.mark.parametrize("input_radius", ["invalid", "", "0", "-1"])
    def test_it_raises_exception_when_radius_is_invalid(
        self, app: "Flask", input_radius: str
    ) -> None:
        with pytest.raises(
            InvalidRadiusException,
            match="invalid radius, must be an float greater than zero",
        ):
            get_buffered_location(
                coordinates="48.85341,2.3488", radius_str=input_radius
            )

    @pytest.mark.parametrize("input_coordinates", ["", "invalid,coordinates"])
    def test_it_raises_exception_when_coordinates_are_invalid(
        self,
        app: "Flask",
        input_coordinates: str,
    ) -> None:
        with pytest.raises(
            InvalidCoordinatesException,
            match=(
                "invalid coordinates, must be a string with latitude and "
                "longitude, separated by a comma"
            ),
        ):
            get_buffered_location(input_coordinates, radius_str="10")

    @pytest.mark.parametrize("input_radius", ["1", "1.0"])
    def test_it_returns_buffered_polygon_with_4326_srid(
        self, app: "Flask", paris_with_10km_buffer: str, input_radius: str
    ) -> None:
        paris_coordinates = "48.85341,2.3488"

        buffer = get_buffered_location(paris_coordinates, input_radius)

        srid, geometry = buffer.split(";")
        assert srid == "SRID=4326"
        assert geometry == paris_with_10km_buffer

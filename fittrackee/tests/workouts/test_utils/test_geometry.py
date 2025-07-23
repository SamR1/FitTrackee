from typing import TYPE_CHECKING

from fittrackee.workouts.utils.geometry import get_geojson_from_segments

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

from typing import TYPE_CHECKING

import pytest

from fittrackee import VERSION
from fittrackee.workouts.exceptions import WorkoutGPXException
from fittrackee.workouts.utils.gpx import generate_gpx

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout, WorkoutSegment


class TestGenerateGpx:
    def test_it_raises_error_when_workout_was_no_segments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1: "Workout",
    ) -> None:
        with pytest.raises(WorkoutGPXException, match="No segments"):
            generate_gpx(workout_cycling_user_1)

    def test_it_generates_gpx_from_segments_points(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_segment_1_with_coordinates: "WorkoutSegment",
        workout_cycling_user_1_generated_gpx: str,
    ) -> None:
        gpx_xml = generate_gpx(workout_cycling_user_1_with_coordinates)

        assert gpx_xml == workout_cycling_user_1_generated_gpx

    def test_it_adds_source_when_workout_has_source(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        source = "Garmin Forerunner"
        workout_cycling_user_1_with_coordinates.source = source
        gpx_xml = generate_gpx(workout_cycling_user_1_with_coordinates)

        assert f"FitTrackee v{VERSION} (from {source})" in gpx_xml

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from fittrackee.workouts.exceptions import WorkoutGPXException
from fittrackee.workouts.utils.chart import get_chart_data

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout, WorkoutSegment


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
        workout_cycling_user_1.gpx = None

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
            "fittrackee.workouts.utils.chart.get_chart_data_from_gpx"
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
            "fittrackee.workouts.utils.chart.get_chart_data_from_gpx"
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
            "fittrackee.workouts.utils.chart.get_chart_data_from_segment_points"
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
            "fittrackee.workouts.utils.chart.get_chart_data_from_segment_points"
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

from typing import TYPE_CHECKING

from fittrackee.workouts.models import WorkoutHeatmapCell
from fittrackee.workouts.services.heatmap_cells_service import (
    HeatmapCellsService,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout, WorkoutSegment


class TestHeatmapCellsServiceGetCells:
    def test_it_returns_empty_list_when_workout_has_no_geometry(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = HeatmapCellsService()

        cells = service.get_cells(workout_cycling_user_1.id)

        assert cells == []

    def test_it_returns_cells_with_default_zoom(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        # HEATMAP_BASE_ZOOM = 20
        service = HeatmapCellsService()

        cells = service.get_cells(workout_cycling_user_1_with_coordinates.id)

        assert cells == [
            (17690, 145774),
            (17690, 145775),
            (17690, 145776),
            (17690, 145777),
            (17690, 145778),
        ]

    def test_it_returns_cells_with_zoom_set_to_22(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        app.config["HEATMAP_BASE_ZOOM"] = 22
        service = HeatmapCellsService()

        cells = service.get_cells(workout_cycling_user_1_with_coordinates.id)

        assert cells == [
            (70761, 583100),
            (70762, 583097),
            (70762, 583098),
            (70762, 583099),
            (70762, 583100),
            (70762, 583101),
            (70762, 583102),
            (70762, 583103),
            (70762, 583104),
            (70762, 583105),
            (70762, 583106),
            (70762, 583107),
            (70762, 583108),
            (70762, 583109),
            (70763, 583109),
            (70763, 583110),
            (70763, 583111),
            (70763, 583112),
            (70763, 583113),
        ]


class TestHeatmapCellsServiceDeleteCells:
    def test_it_deletes_cells_for_a_given_workout(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
        workout_running_user_1_with_coordinates: "Workout",
        workout_running_user_1_segment_with_coordinates: "WorkoutSegment",
    ) -> None:
        service = HeatmapCellsService()
        service.get_cells(workout_cycling_user_1_with_coordinates.id)
        service.get_cells(workout_running_user_1_with_coordinates.id)

        service.delete_cells(workout_cycling_user_1_with_coordinates.id)

        assert (
            WorkoutHeatmapCell.query.filter_by(
                workout_id=workout_cycling_user_1_with_coordinates.id
            ).count()
            == 0
        )
        assert (
            WorkoutHeatmapCell.query.filter_by(
                workout_id=workout_running_user_1_with_coordinates.id
            ).count()
            != 0
        )


class TestHeatmapCellsServiceRefreshCells:
    def test_it_refreshes_cells_depending_on_zoom(
        self,
        app: "Flask",
        user_1: "User",
        workout_cycling_user_1_with_coordinates: "Workout",
        workout_cycling_user_1_segment_0_with_coordinates: "WorkoutSegment",
    ) -> None:
        service = HeatmapCellsService()

        app.config["HEATMAP_BASE_ZOOM"] = 22
        service.refresh_cells(workout_cycling_user_1_with_coordinates.id)
        assert WorkoutHeatmapCell.query.count() == 19

        app.config["HEATMAP_BASE_ZOOM"] = 20
        service.refresh_cells(workout_cycling_user_1_with_coordinates.id)
        assert WorkoutHeatmapCell.query.count() == 5

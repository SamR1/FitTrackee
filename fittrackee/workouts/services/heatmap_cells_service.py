from typing import Any, Sequence

from sqlalchemy import Row, delete, func, insert, select

from fittrackee import db

from ..constants import SUBDIVIDE_MAX_VERTICES, WEB_MERCATOR_CRS
from ..models import Workout, WorkoutHeatmapCell, WorkoutSegment
from ..utils.heatmap import get_base_cell_size


class HeatmapCellsService:
    @staticmethod
    def get_cells(workout_id: int) -> Sequence["Row[Any]"]:
        """
        Indices of the cells crossed by the workout segments. They only depend
        on the cell size, so cells from different workouts are comparable.
        """
        # a grid covers the whole extent of the geometry it is given, so
        # gridding a long track directly generates the cells of its bounding
        # box: subdividing it first keeps that proportional to its length
        pieces = (
            select(
                func.ST_Subdivide(
                    func.ST_Transform(WorkoutSegment.geom, WEB_MERCATOR_CRS),
                    SUBDIVIDE_MAX_VERTICES,
                ).label("geom")
            )
            .where(
                WorkoutSegment.workout_id == workout_id,
                WorkoutSegment.geom != None,  # noqa
            )
            .subquery()
        )
        grid = (
            func.ST_SquareGrid(get_base_cell_size(), pieces.c.geom)
            .table_valued("geom", "i", "j")
            .lateral("grid")
        )

        return db.session.execute(
            select(grid.c.i, grid.c.j)
            .select_from(pieces)
            .join(grid, func.ST_Intersects(grid.c.geom, pieces.c.geom))
            .distinct()
        ).all()

    @classmethod
    def refresh_cells(cls, workout_id: int) -> None:
        cells = cls.get_cells(workout_id)
        cls.delete_cells(workout_id)
        workout = db.session.get(Workout, workout_id)
        # the workout may be on its way out, its segments deleted along with it
        if not cells or workout is None:
            return
        db.session.execute(
            insert(WorkoutHeatmapCell),
            [
                {
                    "workout_id": workout_id,
                    "user_id": workout.user_id,
                    "i": cell.i,
                    "j": cell.j,
                }
                for cell in cells
            ],
        )

    @staticmethod
    def delete_cells(workout_id: int) -> None:
        db.session.execute(
            delete(WorkoutHeatmapCell).where(
                WorkoutHeatmapCell.workout_id == workout_id
            )
        )

"""add workout heatmap cells

Revision ID: e5f7a2c1d9b8
Revises: 2e3a59ebbc59
Create Date: 2026-08-06 13:07:19.442065

"""

import sqlalchemy as sa
from alembic import op
from flask import current_app

# revision identifiers, used by Alembic.
revision = "e5f7a2c1d9b8"
down_revision = "2e3a59ebbc59"
branch_labels = None
depends_on = None

# must match the constants in fittrackee/workouts/constants.py
WEB_MERCATOR_WORLD_SIZE = 40075016.6855785
SUBDIVIDE_MAX_VERTICES = 8


def upgrade():
    op.create_table(
        "workout_heatmap_cells",
        sa.Column("workout_id", sa.Integer(), nullable=False),
        sa.Column("i", sa.Integer(), nullable=False),
        sa.Column("j", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workout_id"], ["workouts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("workout_id", "i", "j"),
    )
    op.create_index(
        "workout_heatmap_cells_user_cell",
        "workout_heatmap_cells",
        ["user_id", "i", "j"],
    )

    if not current_app.config["ENABLE_HEATMAP"]:
        print(
            "\nHeatmap cells calculation skipped (ENABLE_HEATMAP is not set "
            "to 'true').\n"
            "Please run 'ftcli workouts rebuild_heatmap', then set "
            "ENABLE_HEATMAP to 'true' to display the heatmap.\n"
        )
        return

    # the cells are stored at the configured resolution, so that a instance
    # short on space can trade detail for rows
    cell_size = WEB_MERCATOR_WORLD_SIZE / 2 ** current_app.config[
        "HEATMAP_BASE_ZOOM"
    ]
    # a grid covers the whole extent of the geometry it is given, so gridding
    # a long track directly generates the cells of its bounding box:
    # subdividing it first keeps that proportional to its length
    op.execute(
        f"""
        INSERT INTO workout_heatmap_cells (workout_id, user_id, i, j)
        SELECT DISTINCT sub.workout_id, sub.user_id, grid.i, grid.j
        FROM (
            SELECT s.workout_id,
                   w.user_id,
                   ST_Subdivide(
                       ST_Transform(s.geom, 3857), {SUBDIVIDE_MAX_VERTICES}
                   ) AS geom
            FROM workout_segments s
            JOIN workouts w ON w.id = s.workout_id
            WHERE s.geom IS NOT NULL
        ) sub
        CROSS JOIN LATERAL ST_SquareGrid({cell_size}, sub.geom) AS grid
        WHERE ST_Intersects(grid.geom, sub.geom)
        """
    )


def downgrade():
    op.drop_index("workout_heatmap_cells_user_cell", "workout_heatmap_cells")
    op.drop_table("workout_heatmap_cells")

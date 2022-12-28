"""update elevation precision

Revision ID: 0f375c44e659
Revises: a8cc0adfe1d3
Create Date: 2022-12-14 18:01:54.662987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f375c44e659'
down_revision = 'a8cc0adfe1d3'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'workouts',
        'descent',
        existing_type=sa.NUMERIC(precision=7, scale=2),
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        'workouts',
        'ascent',
        existing_type=sa.NUMERIC(precision=7, scale=3),
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        'workout_segments',
        'descent',
        existing_type=sa.NUMERIC(precision=7, scale=2),
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )
    op.alter_column(
        'workout_segments',
        'ascent',
        existing_type=sa.NUMERIC(precision=7, scale=3),
        type_=sa.Numeric(precision=8, scale=3),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        'workout_segments',
        'ascent',
        existing_type=sa.NUMERIC(precision=8, scale=3),
        type_=sa.Numeric(precision=7, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        'workout_segments',
        'descent',
        existing_type=sa.NUMERIC(precision=8, scale=3),
        type_=sa.Numeric(precision=7, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        'workouts',
        'ascent',
        existing_type=sa.NUMERIC(precision=8, scale=3),
        type_=sa.Numeric(precision=7, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        'workouts',
        'descent',
        existing_type=sa.NUMERIC(precision=8, scale=3),
        type_=sa.Numeric(precision=7, scale=2),
        existing_nullable=True,
    )

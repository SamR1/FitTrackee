"""refactoring elevation processing

Revision ID: 0bbe0c8372cf
Revises: 267735b7574f
Create Date: 2025-12-29 16:12:55.425386

Note: since the migration will be released in the same version as the previous
migrations introducing elevation processing, updating existing data is not
necessary.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0bbe0c8372cf'
down_revision = '267735b7574f'
branch_labels = None
depends_on = None


def upgrade():
    elevation_data_source = postgresql.ENUM(
        'FILE', 'OPEN_ELEVATION', 'OPEN_ELEVATION_SMOOTH', 'VALHALLA',
        name="elevation_data_source"
    )
    elevation_data_source.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("missing_elevations_processing")
        batch_op.add_column(
            sa.Column(
                "missing_elevations_processing",
                elevation_data_source,
                server_default="FILE",
                nullable=False,
            )
        )

    with op.batch_alter_table("workouts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "elevation_data_source",
                elevation_data_source,
                server_default="FILE",
                nullable=False,
            )
        )
        batch_op.drop_column("missing_elevations_processing")

    op.execute("DROP TYPE elevations_processing")

def downgrade():
    missing_elevations_processing = postgresql.ENUM(
        'NONE', 'OPEN_ELEVATION', 'OPEN_ELEVATION_SMOOTH', 'VALHALLA',
        name="missing_elevations_processing"
    )
    missing_elevations_processing.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("missing_elevations_processing")
        batch_op.add_column(
            sa.Column(
                "missing_elevations_processing",
                missing_elevations_processing,
                server_default="NONE",
                nullable=False,
            )
        )
    with op.batch_alter_table("workouts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "missing_elevations_processing",
                missing_elevations_processing,
                server_default="NONE",
                nullable=False,
            )
        )
        batch_op.drop_column("elevation_data_source")

    op.execute("DROP TYPE elevation_data_source")
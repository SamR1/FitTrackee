"""add new preference to allow smoothing elevation event when elevation is not missing

Revision ID: 28a548e58b3f
Revises: 85e262f5150d
Create Date: 2026-08-26 09:50:32.677695

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "28a548e58b3f"
down_revision = "85e262f5150d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "process_only_missing_elevations",
                sa.Boolean(),
                server_default="True",
                nullable=False,
            )
        )

    op.execute(
        """
        ALTER TABLE users
            RENAME COLUMN missing_elevations_data_source TO elevation_data_source;
        UPDATE users 
            SET process_only_missing_elevations = True
            WHERE elevation_data_source <> 'FILE'
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE users
            RENAME COLUMN elevation_data_source TO missing_elevations_data_source;
    """
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("process_only_missing_elevations")

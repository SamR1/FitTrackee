"""add windsurfing

Revision ID: 514c727b7feb
Revises: 61ecbc76f410
Create Date: 2025-05-10 10:45:00.915019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '514c727b7feb'
down_revision = '61ecbc76f410'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Windsurfing', True, 1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Windsurfing';
        """
    )

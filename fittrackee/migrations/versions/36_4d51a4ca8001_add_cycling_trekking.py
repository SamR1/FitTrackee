"""add cycling (trekking) sport

Revision ID: 4d51a4ca8001
Revises: 14f48e46f320
Create Date: 2023-12-20 13:45:48.654139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d51a4ca8001'
down_revision = '14f48e46f320'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Cycling (Trekking)', True, 1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Cycling (Trekking)';
        """
    )

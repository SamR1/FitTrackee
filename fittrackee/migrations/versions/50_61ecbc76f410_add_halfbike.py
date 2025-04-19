"""add Halfbike

Revision ID: 61ecbc76f410
Revises: 78a90b587a9b
Create Date: 2025-04-15 23:03:32.375827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61ecbc76f410'
down_revision = '78a90b587a9b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Halfbike', True, 1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Halfbike';
        """
    )

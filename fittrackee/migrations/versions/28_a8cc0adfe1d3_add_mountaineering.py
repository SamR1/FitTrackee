"""add Mountaineering

Revision ID: a8cc0adfe1d3
Revises: bf13b8f5589d
Create Date: 2022-12-11 11:03:01.216734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8cc0adfe1d3'
down_revision = 'bf13b8f5589d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Mountaineering', True, 0.1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Mountaineering';
        """
    )

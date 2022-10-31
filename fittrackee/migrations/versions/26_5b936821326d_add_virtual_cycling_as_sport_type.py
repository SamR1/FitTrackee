"""add virtual cycling as sport type

Revision ID: 5b936821326d
Revises: 84d840ce853b
Create Date: 2022-10-26 17:43:20.114104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b936821326d'
down_revision = '84d840ce853b'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Cycling (Virtual)', True, 1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Cycling (Virtual)';
        """
    )

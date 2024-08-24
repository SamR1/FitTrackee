"""add swimrun

Revision ID: c9c6a5a4dd6d
Revises: 032ba0846eea
Create Date: 2024-08-24 08:37:37.751827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9c6a5a4dd6d'
down_revision = '032ba0846eea'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Swimrun', True, 0.1)
        """
    )

def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Swimrun';
        """
    )

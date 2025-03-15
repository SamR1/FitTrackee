"""add Kayaking and Canoeing

Revision ID: 78a90b587a9b
Revises: ce68b3914ff7
Create Date: 2025-03-02 16:08:56.898458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78a90b587a9b'
down_revision = 'ce68b3914ff7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Kayaking', True, 1),
               ('Canoeing', True, 1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Kayaking' OR label = 'Canoeing';
        """
    )

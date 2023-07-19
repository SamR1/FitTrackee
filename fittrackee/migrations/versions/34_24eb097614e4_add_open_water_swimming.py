"""add open water swimming

Revision ID: 24eb097614e4
Revises: d22670a89a54
Create Date: 2023-07-19 10:34:40.297525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24eb097614e4'
down_revision = 'd22670a89a54'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Open Water Swimming', True, 0.1)
        """
    )

def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Open Water Swimming';
        """
    )

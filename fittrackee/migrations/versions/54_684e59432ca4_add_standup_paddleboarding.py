"""add standup paddleboarding

Revision ID: 684e59432ca4
Revises: 1648fe51cbd1
Create Date: 2025-06-15 14:38:00.820841

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '684e59432ca4'
down_revision = '1648fe51cbd1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Standup Paddleboarding', True, 1);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Standup Paddleboarding';
        """
    )

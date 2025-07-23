"""add tennis (outdoor)

Revision ID: 4eeeecd3936d
Revises: 684e59432ca4
Create Date: 2025-07-06 13:09:54.462631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eeeecd3936d'
down_revision = '684e59432ca4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Tennis (Outdoor)', True, 0.1);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE
        FROM sports
        WHERE label = 'Tennis (Outdoor)';
        """
    )

"""add padel (outdoor)

Revision ID: 67ae8866b18f
Revises: 0a2e2369b972
Create Date: 2025-09-24 13:13:35.236703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67ae8866b18f'
down_revision = '0a2e2369b972'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Padel (Outdoor)', True, 0.1);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE
        FROM sports
        WHERE label = 'Padel (Outdoor)';
        """
    )

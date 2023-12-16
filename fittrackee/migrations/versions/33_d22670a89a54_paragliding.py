"""add paragliding sport

Revision ID: d22670a89a54
Revises: eff1c16c43eb
Create Date: 2023-07-12 21:00:11.291517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd22670a89a54'
down_revision = 'eff1c16c43eb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Paragliding', True, 0.1)
        """
    )

def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Paragliding';
        """
    )

"""add skating sports

Revision ID: 84394acbebcf
Revises: 076d33eab04f
Create Date: 2026-03-04 16:21:27.343612

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '84394acbebcf'
down_revision = '076d33eab04f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Ice Skating', True, 1.0), ('Inline Skating', True, 1.0)
        """
    )
    op.execute(
        """
        INSERT INTO equipment_types (label, is_active)
        VALUES ('Skates', True);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM equipment_types
        WHERE label IN ('Skates');
        """
    )
    op.execute(
        """
        DELETE FROM sports
        WHERE label IN ('Ice Skating', 'Inline Skating');
        """
    )


"""add whitewater sports

Revision ID: e120ac5a4c5a
Revises: 141d3978536a
Create Date: 2026-01-07 10:06:44.130021

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "e120ac5a4c5a"
down_revision = "d8416412506b"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Canoeing (Whitewater)', True, 1),
               ('Kayaking (Whitewater)', True, 1);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE
        FROM sports
        WHERE label IN ('Canoeing (Whitewater)', 'Kayaking (Whitewater)');
        """
    )

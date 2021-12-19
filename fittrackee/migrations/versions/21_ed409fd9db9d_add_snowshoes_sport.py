"""add snowshoes sport

Revision ID: ed409fd9db9d
Revises: 07188ca7620a
Create Date: 2021-12-19 09:09:37.531543

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'ed409fd9db9d'
down_revision = '07188ca7620a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Snowshoes', True, 0.1)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Snowshoes';
        """
    )

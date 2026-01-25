"""change split_workout_charts default value

Revision ID: ff53544547cd
Revises: e120ac5a4c5a
Create Date: 2026-01-21 09:07:29.233113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff53544547cd'
down_revision = 'e120ac5a4c5a'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('users', "split_workout_charts", server_default="true")


def downgrade():
    op.alter_column('users', "split_workout_charts", server_default="false")

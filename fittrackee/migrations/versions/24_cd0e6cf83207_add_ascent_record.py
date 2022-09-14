"""add ascent record

Revision ID: cd0e6cf83207
Revises: 5e3a3a31c432
Create Date: 2022-03-22 20:21:13.661883

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd0e6cf83207'
down_revision = '5e3a3a31c432'
branch_labels = None
depends_on = None


def upgrade():
    # workaround for PostgreSQL<12
    # (can not use ALTER TYPE to add values in migrations)
    op.execute("ALTER TYPE record_types RENAME TO record_types_old")
    op.execute("CREATE TYPE record_types AS ENUM('AS', 'FD', 'LD', 'MS', 'HA')")
    op.execute(
        """
        ALTER TABLE records ALTER COLUMN record_type TYPE record_types
        USING record_type::text::record_types
    """
    )
    op.execute("DROP TYPE record_types_old")

    op.add_column(
        'users', sa.Column('display_ascent', sa.Boolean(), nullable=True)
    )
    op.execute("UPDATE users SET display_ascent = true")
    op.alter_column('users', 'display_ascent', nullable=False)


def downgrade():
    op.drop_column('users', 'display_ascent')

    op.execute("DELETE FROM records WHERE record_type = 'HA';")
    op.execute("ALTER TYPE record_types RENAME TO record_types_old")
    op.execute("CREATE TYPE record_types AS ENUM('AS', 'FD', 'LD', 'MS')")
    op.execute(
        """
        ALTER TABLE records ALTER COLUMN record_type TYPE record_types
        USING record_type::text::record_types
    """
    )
    op.execute("DROP TYPE record_types_old")

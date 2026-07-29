"""add 'elevation_processing' to 'users' and 'workouts' tables

Revision ID: 37e8d3d85f0c
Revises: cbee82450dd3
Create Date: 2026-06-29 10:54:42.153340

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '37e8d3d85f0c'
down_revision = 'cbee82450dd3'
branch_labels = None
depends_on = None

elevation_processing = postgresql.ENUM(
    'NONE', 'FLAT_WINDOW',
    name="elevation_processing"
)
try:
    elevation_processing.create(op.get_bind(), checkfirst=True)
except NameError:
    # workaround to avoid error when generating revision (empty migration)
    pass



def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('elevation_processing', elevation_processing, server_default='NONE', nullable=False))

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('elevation_processing', elevation_processing, server_default='NONE', nullable=False))


    op.execute(
        f"""
        UPDATE workouts 
        SET elevation_data_source = 'OPEN_ELEVATION', elevation_processing = 'FLAT_WINDOW'
        WHERE workouts.elevation_data_source = 'OPEN_ELEVATION_SMOOTH';
"""
    )
    op.execute("ALTER TYPE elevation_data_source RENAME TO elevation_data_source_old")
    op.execute("CREATE TYPE elevation_data_source AS ENUM('FILE', 'OPEN_ELEVATION', 'VALHALLA')")

    op.execute(
        """
        ALTER TABLE users 
            ALTER COLUMN missing_elevations_processing DROP DEFAULT,
            ALTER COLUMN missing_elevations_processing TYPE elevation_data_source USING missing_elevations_processing::text::elevation_data_source,
            ALTER COLUMN missing_elevations_processing SET DEFAULT 'FILE';
        ALTER TABLE users
            RENAME COLUMN missing_elevations_processing TO missing_elevations_data_source;
        ALTER TABLE workouts 
            ALTER COLUMN elevation_data_source DROP DEFAULT,
            ALTER COLUMN elevation_data_source TYPE elevation_data_source USING elevation_data_source::text::elevation_data_source,
            ALTER COLUMN elevation_data_source SET DEFAULT 'FILE';
    """
    )
    op.execute("DROP TYPE elevation_data_source_old")



def downgrade():

    op.execute("ALTER TYPE elevation_data_source RENAME TO elevation_data_source_old")
    op.execute("CREATE TYPE elevation_data_source AS ENUM('FILE', 'OPEN_ELEVATION', 'OPEN_ELEVATION_SMOOTH', 'VALHALLA')")
    op.execute(
        """
        ALTER TABLE workouts 
            ALTER COLUMN elevation_data_source DROP DEFAULT,
            ALTER COLUMN elevation_data_source TYPE elevation_data_source USING elevation_data_source::text::elevation_data_source,
            ALTER COLUMN elevation_data_source SET DEFAULT 'FILE';
        ALTER TABLE users
            RENAME COLUMN missing_elevations_data_source TO  missing_elevations_processing;
        ALTER TABLE users 
            ALTER COLUMN missing_elevations_processing DROP DEFAULT,
            ALTER COLUMN missing_elevations_processing TYPE elevation_data_source USING missing_elevations_processing::text::elevation_data_source,
            ALTER COLUMN missing_elevations_processing SET DEFAULT 'FILE';
    """
    )

    op.execute(
        f"""
            UPDATE workouts 
            SET elevation_data_source = 'OPEN_ELEVATION_SMOOTH'
            WHERE workouts.elevation_data_source = 'OPEN_ELEVATION' and elevation_processing = 'FLAT_WINDOW';
    """
    )
    op.execute("DROP TYPE elevation_data_source_old")

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.drop_column('elevation_processing')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('elevation_processing')

    elevation_processing.drop(op.get_bind())

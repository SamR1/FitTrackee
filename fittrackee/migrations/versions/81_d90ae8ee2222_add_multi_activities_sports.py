"""add multi activities sports

Revision ID: d90ae8ee2222
Revises: 37e8d3d85f0c
Create Date: 2026-07-19 13:18:53.429415

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = 'd90ae8ee2222'
down_revision = '37e8d3d85f0c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('multi_activities_sports',
    sa.Column('sport_id', sa.Integer(), nullable=False),
    sa.Column('sub_sport_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
    sa.ForeignKeyConstraint(['sub_sport_id'], ['sports.id'], ),
    sa.PrimaryKeyConstraint('sport_id', 'sub_sport_id')
    )
    with op.batch_alter_table('workout_segments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sport_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_transition', sa.Boolean(), server_default='False', nullable=False))
        batch_op.add_column(sa.Column('calories', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_workout_segments_sport_id'), ['sport_id'], unique=False)
        batch_op.create_foreign_key('workout_segments_sport_id_fkey', 'sports', ['sport_id'], ['id'])
        batch_op.alter_column('geom',
               existing_type=Geometry(geometry_type='LINESTRING', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry', _spatial_index_reflected=True),
               type_=Geometry(srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry'),
               existing_nullable=True)

    op.execute(
        """
        INSERT INTO sports (label, is_active, stopped_speed_threshold)
        VALUES ('Triathlon', True, 1.0)
        """
    )

def downgrade():
    op.execute(
        f"""
        UPDATE workout_segments SET geom = NULL 
        WHERE ST_geometrytype(geom) = 'ST_Point';
    """)

    with op.batch_alter_table('workout_segments', schema=None) as batch_op:
        batch_op.alter_column('geom',
               existing_type=Geometry(srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry'),
               type_=Geometry(geometry_type='LINESTRING', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry', _spatial_index_reflected=True),
               existing_nullable=True)
        batch_op.drop_constraint('workout_segments_sport_id_fkey', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_workout_segments_sport_id'))
        batch_op.drop_column('calories')
        batch_op.drop_column('is_transition')
        batch_op.drop_column('sport_id')

    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Triathlon';
        """
    )

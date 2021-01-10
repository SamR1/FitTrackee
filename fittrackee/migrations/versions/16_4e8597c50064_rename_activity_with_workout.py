"""rename 'activity' with 'workout'

Revision ID: 4e8597c50064
Revises: 3243cd25eca7
Create Date: 2021-01-09 19:41:26.589237

"""
import os

import sqlalchemy as sa
from alembic import op
from flask import current_app
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4e8597c50064'
down_revision = '3243cd25eca7'
branch_labels = None
depends_on = None


def rename_upload_folder(src, dst):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    src_directory = f'{upload_folder}/{src}'
    if os.path.exists(src_directory):
        try:
            os.rename(src_directory, f'{upload_folder}/{dst}')
        except Exception as e:
            print(
                f'ERROR: can not rename upload folder \'{src}\' to \'{dst}\':'
                f'\n      {e}.'
                f'\n      Please rename it manually.')


def upgrade():

    op.create_table('workouts',
        sa.Column('id', sa.Integer(), server_default=sa.text("nextval('workouts_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('gpx', sa.String(length=255), nullable=True),
        sa.Column('creation_date', sa.DateTime(), nullable=True),
        sa.Column('modification_date', sa.DateTime(), nullable=True),
        sa.Column('workout_date', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.Interval(), nullable=False),
        sa.Column('pauses', sa.Interval(), nullable=True),
        sa.Column('moving', sa.Interval(), nullable=True),
        sa.Column('distance', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('min_alt', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('max_alt', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('descent', sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column('ascent', sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column('max_speed', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('ave_speed', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('bounds', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('map', sa.String(length=255), nullable=True),
        sa.Column('map_id', sa.String(length=50), nullable=True),
        sa.Column('weather_start', sa.JSON(), nullable=True),
        sa.Column('weather_end', sa.JSON(), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.execute(
        "SELECT setval('workouts_id_seq', (SELECT max(id) FROM activities));"
    )

    op.create_table('workout_segments',
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('workout_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('segment_id', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Interval(), nullable=False),
        sa.Column('pauses', sa.Interval(), nullable=True),
        sa.Column('moving', sa.Interval(), nullable=True),
        sa.Column('distance', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('min_alt', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('max_alt', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('descent', sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column('ascent', sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column('max_speed', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('ave_speed', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ),
        sa.PrimaryKeyConstraint('workout_id', 'segment_id')
    )

    op.add_column('records', sa.Column('workout_date', sa.DateTime(), nullable=True))
    op.add_column('records', sa.Column('workout_id', sa.Integer(), nullable=True))
    op.add_column('records', sa.Column('workout_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('records_workout_id_fkey', 'records', 'workouts', ['workout_id'], ['id'])

    op.execute(
        """
        INSERT INTO workouts (id, user_id, sport_id, title, gpx, 
        creation_date, modification_date, workout_date, duration, pauses, 
        moving, distance, min_alt, max_alt, descent, ascent, max_speed, 
        ave_speed, bounds, map, map_id, weather_start, weather_end, notes, uuid)
        SELECT id, user_id, sport_id, title, REPLACE(gpx, 'activities/', 'workouts/'), 
        creation_date, modification_date, activity_date, duration, pauses, 
        moving, distance, min_alt, max_alt, descent, ascent, max_speed, 
        ave_speed, bounds, REPLACE(map, 'activities/', 'workouts/'), map_id, 
        weather_start, weather_end, notes, uuid 
        FROM activities;
        """
    )

    op.execute(
        """
        INSERT INTO workout_segments (workout_id, workout_uuid, segment_id,
        duration, pauses, moving, distance, min_alt, max_alt, descent, 
        ascent, max_speed, ave_speed)
         SELECT activity_id, activity_uuid, segment_id,
        duration, pauses, moving, distance, min_alt, max_alt, descent, 
        ascent, max_speed, ave_speed FROM activity_segments;
        """
    )

    op.execute(
        'UPDATE records SET workout_id = activity_id, '
        '                   workout_uuid = activity_uuid, '
        '                   workout_date = activity_date;'
    )

    op.alter_column('records', 'workout_date', nullable=False)
    op.alter_column('records', 'workout_id', nullable=False)
    op.alter_column('records', 'workout_uuid', nullable=False)
    op.drop_column('records', 'activity_date')
    op.drop_column('records', 'activity_id')
    op.drop_column('records', 'activity_uuid')

    op.drop_table('activity_segments')

    op.drop_table('activities')

    rename_upload_folder('activities', 'workouts')


def downgrade():
    op.create_table('activities',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('activities_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('sport_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('gpx', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('creation_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('modification_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('activity_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.Column('duration', postgresql.INTERVAL(), autoincrement=False, nullable=False),
        sa.Column('pauses', postgresql.INTERVAL(), autoincrement=False, nullable=True),
        sa.Column('moving', postgresql.INTERVAL(), autoincrement=False, nullable=True),
        sa.Column('distance', sa.NUMERIC(precision=6, scale=3), autoincrement=False, nullable=True),
        sa.Column('min_alt', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('max_alt', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('descent', sa.NUMERIC(precision=7, scale=2), autoincrement=False, nullable=True),
        sa.Column('ascent', sa.NUMERIC(precision=7, scale=2), autoincrement=False, nullable=True),
        sa.Column('max_speed', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('ave_speed', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('bounds', postgresql.ARRAY(postgresql.DOUBLE_PRECISION(precision=53)), autoincrement=False, nullable=True),
        sa.Column('map', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('map_id', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('weather_end', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
        sa.Column('weather_start', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
        sa.Column('notes', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
        sa.Column('uuid', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['sport_id'], ['sports.id'], name='activities_sport_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='activities_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='activities_pkey'),
        sa.UniqueConstraint('uuid', name='activities_uuid_key'),
        postgresql_ignore_search_path=False
    )
    op.execute(
        "SELECT setval('activities_id_seq', (SELECT max(id) FROM workouts));"
    )

    op.create_table('activity_segments',
        sa.Column('activity_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('segment_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('duration', postgresql.INTERVAL(), autoincrement=False, nullable=False),
        sa.Column('pauses', postgresql.INTERVAL(), autoincrement=False, nullable=True),
        sa.Column('moving', postgresql.INTERVAL(), autoincrement=False, nullable=True),
        sa.Column('distance', sa.NUMERIC(precision=6, scale=3), autoincrement=False, nullable=True),
        sa.Column('min_alt', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('max_alt', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('descent', sa.NUMERIC(precision=7, scale=2), autoincrement=False, nullable=True),
        sa.Column('ascent', sa.NUMERIC(precision=7, scale=2), autoincrement=False, nullable=True),
        sa.Column('max_speed', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('ave_speed', sa.NUMERIC(precision=6, scale=2), autoincrement=False, nullable=True),
        sa.Column('activity_uuid', postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], name='activity_segments_activity_id_fkey'),
        sa.PrimaryKeyConstraint('activity_id', 'segment_id', name='activity_segments_pkey')
    )

    op.execute(
        """
        INSERT INTO activities (id, user_id, sport_id, title, gpx, 
        creation_date, modification_date, activity_date, duration, pauses, 
        moving, distance, min_alt, max_alt, descent, ascent, max_speed, 
        ave_speed, bounds, map, map_id, weather_start, weather_end, notes, uuid)
        SELECT id, user_id, sport_id, title, REPLACE(gpx, 'workouts/', 'activities/'),
        creation_date, modification_date, workout_date, duration, pauses, 
        moving, distance, min_alt, max_alt, descent, ascent, max_speed, 
        ave_speed, bounds, REPLACE(map, 'workouts/', 'activities/'), map_id, 
        weather_start, weather_end, notes, uuid 
        FROM workouts;
        """
    )

    op.execute(
        """
        INSERT INTO activity_segments (activity_id, activity_uuid, segment_id,
        duration, pauses, moving, distance, min_alt, max_alt, descent, 
        ascent, max_speed, ave_speed)
         SELECT workout_id, workout_uuid, segment_id,
        duration, pauses, moving, distance, min_alt, max_alt, descent, 
        ascent, max_speed, ave_speed FROM workout_segments;
        """
    )

    op.add_column('records', sa.Column('activity_uuid', postgresql.UUID(), autoincrement=False, nullable=True))
    op.add_column('records', sa.Column('activity_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('records', sa.Column('activity_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.create_foreign_key('records_activity_id_fkey', 'records', 'activities', ['activity_id'], ['id'])

    op.execute(
        'UPDATE records SET activity_id = workout_id, '
        '                   activity_uuid = workout_uuid, '
        '                   activity_date = workout_date;'
    )

    op.alter_column('records', 'activity_date', nullable=False)
    op.alter_column('records', 'activity_id', nullable=False)
    op.alter_column('records', 'activity_uuid', nullable=False)
    op.drop_column('records', 'workout_uuid')
    op.drop_column('records', 'workout_id')
    op.drop_column('records', 'workout_date')

    op.drop_table('workout_segments')

    op.drop_table('workouts')

    rename_upload_folder('workouts', 'activities')

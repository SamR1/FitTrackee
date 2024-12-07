"""init social features

Revision ID: aa7802092404
Revises: 4d51a4ca8001
Create Date: 2023-04-13 11:28:53.769936

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from fittrackee.users.roles import UserRole

# revision identifiers, used by Alembic.
revision = 'aa7802092404'
down_revision = '6988082918f8'
branch_labels = None
depends_on = None


visibility_levels = postgresql.ENUM(
    'PUBLIC',
    'FOLLOWERS_AND_REMOTE',  # for a next version, not used for now
    'FOLLOWERS',
    'PRIVATE',
    name='visibility_levels',
)


def upgrade():
    visibility_levels.create(op.get_bind())

    op.create_table(
        'follow_requests',
        sa.Column('follower_user_id', sa.Integer(), nullable=False),
        sa.Column('followed_user_id', sa.Integer(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['followed_user_id'],
            ['users.id'],
        ),
        sa.ForeignKeyConstraint(
            ['follower_user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('follower_user_id', 'followed_user_id'),
    )
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workout_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('modification_date', sa.DateTime(), nullable=True),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('suspended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['workout_id'], ['workouts.id'], ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
    )

    op.add_column(
        'comments',
        sa.Column(
            'text_visibility',
            visibility_levels,
            server_default='PRIVATE',
            nullable=False,
        ),
    )

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_comments_user_id'), ['user_id'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_comments_workout_id'), ['workout_id'], unique=False
        )

    op.create_table(
        'workout_likes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['workout_id'], ['workouts.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id', 'workout_id', name='user_id_workout_id_unique'
        ),
    )
    op.create_table(
        'comment_likes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['comment_id'], ['comments.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id', 'comment_id', name='user_id_comment_id_unique'
        ),
    )
    op.create_table(
        'mentions',
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['comment_id'], ['comments.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('comment_id', 'user_id'),
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'manually_approves_followers', sa.Boolean(), nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                'hide_profile_in_users_directory', sa.Boolean(), nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                'workouts_visibility',
                visibility_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'map_visibility',
                visibility_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column('suspended_at', sa.DateTime(), nullable=True)
        )
        batch_op.add_column(sa.Column('role', sa.Integer(), nullable=True))
    user_helper = sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin', sa.String(length=10), nullable=False),
    )
    connection = op.get_bind()
    for user in connection.execute(user_helper.select()):
        op.execute(f"""
            UPDATE users
            SET manually_approves_followers = True,
                hide_profile_in_users_directory = True,
                workouts_visibility = 'PRIVATE',
                map_visibility = 'PRIVATE',
                role = 
                    CASE 
                        WHEN {user.admin} IS TRUE THEN {UserRole.ADMIN.value}
                        ELSE  {UserRole.USER.value}
                    END
            WHERE users.id = {user.id}
            """)
    op.alter_column('users', 'manually_approves_followers', nullable=False)
    op.alter_column('users', 'hide_profile_in_users_directory', nullable=False)
    op.alter_column('users', 'workouts_visibility', nullable=False)
    op.alter_column('users', 'map_visibility', nullable=False)
    op.alter_column('users', 'role', nullable=False)
    op.create_check_constraint(
        'ck_users_role',
        'users',
        f"role IN ({', '.join(UserRole.db_values())})",
    )
    op.drop_column('users', 'admin')

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'workout_visibility',
                visibility_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'map_visibility',
                visibility_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column('suspended_at', sa.DateTime(), nullable=True)
        )
    op.execute(
        "UPDATE workouts "
        "SET workout_visibility = 'PRIVATE', "
        "    map_visibility = 'PRIVATE' "
    )
    op.alter_column('workouts', 'workout_visibility', nullable=False)
    op.alter_column('workouts', 'map_visibility', nullable=False)

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('from_user_id', sa.Integer(), nullable=True),
        sa.Column('to_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('marked_as_read', sa.Boolean(), nullable=False),
        sa.Column('event_object_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ['from_user_id'], ['users.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['to_user_id'], ['users.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'from_user_id',
            'to_user_id',
            'event_type',
            'event_object_id',
            name='users_event_unique',
        ),
    )
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_notifications_from_user_id'),
            ['from_user_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_notifications_to_user_id'),
            ['to_user_id'],
            unique=False,
        )

    op.create_table(
        'blocked_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['by_user_id'], ['users.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id', 'by_user_id', name='blocked_users_unique'
        ),
    )
    with op.batch_alter_table('blocked_users', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_blocked_users_by_user_id'),
            ['by_user_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_blocked_users_user_id'), ['user_id'], unique=False
        )

    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('reported_by', sa.Integer(), nullable=True),
        sa.Column('reported_comment_id', sa.Integer(), nullable=True),
        sa.Column('reported_user_id', sa.Integer(), nullable=True),
        sa.Column('reported_workout_id', sa.Integer(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False),
        sa.Column('object_type', sa.String(length=50), nullable=False),
        sa.Column('note', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['reported_by'], ['users.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['reported_comment_id'], ['comments.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['reported_user_id'], ['users.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['reported_workout_id'], ['workouts.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['resolved_by'], ['users.id'], ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_reports_reported_by'), ['reported_by'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_reports_reported_comment_id'),
            ['reported_comment_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_reports_reported_user_id'),
            ['reported_user_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_reports_reported_workout_id'),
            ['reported_workout_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_reports_resolved_by'), ['resolved_by'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_reports_object_type'), ['object_type'], unique=False
        )

    op.create_table(
        'report_comments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('report_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('comment', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['report_id'], ['reports.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('report_comments', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_report_comments_report_id'),
            ['report_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_comments_user_id'), ['user_id'], unique=False
        )

    with op.batch_alter_table('records', schema=None) as batch_op:
        batch_op.create_index(
            'workout_records', ['workout_id', 'record_type'], unique=False
        )

    op.create_table(
        'report_actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('workout_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ['moderator_id'], ['users.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['report_id'], ['reports.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['comment_id'], ['comments.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['workout_id'], ['workouts.id'], ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
    )
    with op.batch_alter_table('report_actions', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_report_actions_moderator_id'),
            ['moderator_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_actions_report_id'),
            ['report_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_actions_comment_id'),
            ['comment_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_actions_user_id'), ['user_id'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_report_actions_workout_id'),
            ['workout_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_actions_created_at'),
            ['created_at'],
            unique=False,
        )

    op.create_table(
        'report_action_appeals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ['action_id'], ['report_actions.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['moderator_id'], ['users.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'action_id', 'user_id', name='action_id_user_id_unique'
        ),
        sa.UniqueConstraint('uuid'),
    )
    with op.batch_alter_table('report_action_appeals', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_report_action_appeals_action_id'),
            ['action_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_action_appeals_moderator_id'),
            ['moderator_id'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_report_action_appeals_user_id'),
            ['user_id'],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table('report_action_appeals', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_report_action_appeals_user_id'))
        batch_op.drop_index(
            batch_op.f('ix_report_action_appeals_moderator_id')
        )
        batch_op.drop_index(batch_op.f('ix_report_action_appeals_action_id'))

    op.drop_table('report_action_appeals')

    with op.batch_alter_table('report_actions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_report_actions_created_at'))
        batch_op.drop_index(batch_op.f('ix_report_actions_user_id'))
        batch_op.drop_index(batch_op.f('ix_report_actions_report_id'))
        batch_op.drop_index(batch_op.f('ix_report_actions_moderator_id'))

    op.drop_table('report_actions')

    with op.batch_alter_table('records', schema=None) as batch_op:
        batch_op.drop_index('workout_records')

    with op.batch_alter_table('report_comments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_report_comments_user_id'))
        batch_op.drop_index(batch_op.f('ix_report_comments_report_id'))

    op.drop_table('report_comments')
    with op.batch_alter_table('reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reports_object_type'))
        batch_op.drop_index(batch_op.f('ix_reports_resolved_by'))
        batch_op.drop_index(batch_op.f('ix_reports_reported_workout_id'))
        batch_op.drop_index(batch_op.f('ix_reports_reported_user_id'))
        batch_op.drop_index(batch_op.f('ix_reports_reported_comment_id'))
        batch_op.drop_index(batch_op.f('ix_reports_reported_by'))

    op.drop_table('reports')

    with op.batch_alter_table('blocked_users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_blocked_users_user_id'))
        batch_op.drop_index(batch_op.f('ix_blocked_users_by_user_id'))

    op.drop_table('blocked_users')

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notifications_to_user_id'))
        batch_op.drop_index(batch_op.f('ix_notifications_from_user_id'))
    op.drop_table('notifications')

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.drop_column('map_visibility')
        batch_op.drop_column('workout_visibility')
        batch_op.drop_column('suspended_at')

    op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=True))
    batch_op.drop_constraint(batch_op.f('ck_users_role'))

    user_helper = sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Integer(), nullable=False),
    )
    connection = op.get_bind()
    for user in connection.execute(user_helper.select()):
        op.execute(f"""
            UPDATE users
            SET admin = {user.role} <> {UserRole.USER.value}
            WHERE users.id = {user.id}
            """)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('admin', nullable=False)
        batch_op.drop_column('role')
        batch_op.drop_column('suspended_at')
        batch_op.drop_column('map_visibility')
        batch_op.drop_column('workouts_visibility')
        batch_op.drop_column('hide_profile_in_users_directory')
        batch_op.drop_column('manually_approves_followers')

    op.drop_table('mentions')
    op.drop_table('comment_likes')
    op.drop_table('workout_likes')
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comments_workout_id'))
        batch_op.drop_index(batch_op.f('ix_comments_user_id'))

    op.drop_table('comments')
    op.drop_table('follow_requests')
    visibility_levels.drop(op.get_bind())

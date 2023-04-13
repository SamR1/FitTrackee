"""init social features

Revision ID: aa7802092404
Revises: db58d195c5bf
Create Date: 2023-04-13 11:28:53.769936

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aa7802092404'
down_revision = 'db58d195c5bf'
branch_labels = None
depends_on = None


privacy_levels = postgresql.ENUM(
    'PUBLIC',
    'FOLLOWERS_AND_REMOTE',  # for a next version, not used for now
    'FOLLOWERS',
    'PRIVATE',
    name='privacy_levels',
)


def upgrade():
    privacy_levels.create(op.get_bind())

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
        sa.Column('reply_to', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('modification_date', sa.DateTime(), nullable=True),
        sa.Column('text', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['reply_to'], ['comments.id'], ondelete='SET NULL'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
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
            privacy_levels,
            server_default='PRIVATE',
            nullable=False,
        ),
    )

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_comments_reply_to'), ['reply_to'], unique=False
        )
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
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
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
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
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
                'workouts_visibility',
                privacy_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'map_visibility',
                privacy_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
    user_helper = sa.Table(
        'users', sa.MetaData(), sa.Column('id', sa.Integer(), nullable=False)
    )
    connection = op.get_bind()
    for user in connection.execute(user_helper.select()):
        op.execute(
            "UPDATE users "
            "SET manually_approves_followers = True, "
            "    workouts_visibility = 'PRIVATE', "
            "    map_visibility = 'PRIVATE' "
            f"WHERE users.id = {user.id}"
        )
    op.alter_column('users', 'manually_approves_followers', nullable=False)
    op.alter_column('users', 'workouts_visibility', nullable=False)
    op.alter_column('users', 'map_visibility', nullable=False)

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'workout_visibility',
                privacy_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'map_visibility',
                privacy_levels,
                server_default='PRIVATE',
                nullable=True,
            )
        )
    op.execute(
        "UPDATE workouts "
        "SET workout_visibility = 'PRIVATE', "
        "    map_visibility = 'PRIVATE' "
    )
    op.alter_column('workouts', 'workout_visibility', nullable=False)
    op.alter_column('workouts', 'map_visibility', nullable=False)


def downgrade():
    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.drop_column('map_visibility')
        batch_op.drop_column('workout_visibility')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('map_visibility')
        batch_op.drop_column('workouts_visibility')
        batch_op.drop_column('manually_approves_followers')

    op.drop_table('mentions')
    op.drop_table('comment_likes')
    op.drop_table('workout_likes')
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comments_workout_id'))
        batch_op.drop_index(batch_op.f('ix_comments_user_id'))
        batch_op.drop_index(batch_op.f('ix_comments_reply_to'))

    op.drop_table('comments')
    op.drop_table('follow_requests')
    privacy_levels.drop(op.get_bind())

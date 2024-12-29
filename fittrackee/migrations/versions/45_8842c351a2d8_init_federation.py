"""init federation

Revision ID: 8842c351a2d8
Revises: aa7802092404
Create Date: 2021-01-10 16:02:43.811023

"""
import os
from datetime import datetime

from alembic import op
import sqlalchemy as sa

from fittrackee.federation.utils import (
    generate_keys,
    get_ap_url,
    remove_url_scheme,
)


# revision identifiers, used by Alembic.
revision = '8842c351a2d8'
down_revision = '8a80bec0a410'
branch_labels = None
depends_on = None


def upgrade():
    domain_table = op.create_table(
        'domains',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_allowed', sa.Boolean(), nullable=False),
        sa.Column('software_name', sa.String(length=255), nullable=True),
        sa.Column('software_version', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    # create local domain (even if federation is not enabled)
    domain = remove_url_scheme(os.environ['UI_URL'])
    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    op.execute(
        "INSERT INTO domains (name, created_at, is_allowed, software_name)"
        f"VALUES ('{domain}', '{created_at}'::timestamp, True, 'fittrackee')"
    )

    actors_table = op.create_table(
        'actors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('activitypub_id', sa.String(length=255), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column(
            'type',
            sa.Enum('APPLICATION', 'GROUP', 'PERSON', name='actor_types'),
            server_default='PERSON',
            nullable=True,
        ),
        sa.Column('preferred_username', sa.String(length=255), nullable=False),
        sa.Column('public_key', sa.String(length=5000), nullable=True),
        sa.Column('private_key', sa.String(length=5000), nullable=True),
        sa.Column('profile_url', sa.String(length=255), nullable=False),
        sa.Column('inbox_url', sa.String(length=255), nullable=False),
        sa.Column('outbox_url', sa.String(length=255), nullable=False),
        sa.Column('followers_url', sa.String(length=255), nullable=False),
        sa.Column('following_url', sa.String(length=255), nullable=False),
        sa.Column('shared_inbox_url', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_fetch_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['domain_id'],
            ['domains.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('activitypub_id'),
        sa.UniqueConstraint(
            'domain_id', 'preferred_username', name='domain_username_unique'
        ),
    )
    op.create_table(
        'remote_actors_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=False),
        sa.Column('items', sa.Integer(), nullable=False),
        sa.Column('followers', sa.Integer(), nullable=False),
        sa.Column('following', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['actor_id'],
            ['actors.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('remote_actors_stats', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_remote_actors_stats_actor_id'),
            ['actor_id'],
            unique=True,
        )

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ap_id', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('remote_url', sa.Text(), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('actor_id', sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column('is_remote', sa.Boolean(), nullable=True)
        )
        batch_op.alter_column(
            'email', existing_type=sa.VARCHAR(length=255), nullable=True
        )
        batch_op.alter_column(
            'password', existing_type=sa.VARCHAR(length=255), nullable=True
        )
        batch_op.drop_constraint('users_username_key', type_='unique')
        batch_op.create_unique_constraint(
            'username_actor_id_unique', ['username', 'actor_id']
        )
        batch_op.create_unique_constraint('users_actor_id_key', ['actor_id'])
        batch_op.create_foreign_key(
            'users_actor_id_fkey', 'actors', ['actor_id'], ['id']
        )

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ap_id', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('remote_url', sa.Text(), nullable=True))

    # create local actors with keys (even if federation is not enabled)
    # and update users
    user_helper = sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
    )
    connection = op.get_bind()
    domain = connection.execute(domain_table.select()).fetchone()
    for user in connection.execute(user_helper.select()):
        op.execute(
            f"UPDATE users SET is_remote = False WHERE users.id = {user.id}"
        )
        created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        public_key, private_key = generate_keys()
        op.execute(
            "INSERT INTO actors ("
            "activitypub_id, domain_id, preferred_username, public_key, "
            "private_key, followers_url, following_url, profile_url, "
            "inbox_url, outbox_url, shared_inbox_url, created_at) "
            "VALUES ("
            f"'{get_ap_url(user.username, 'user_url')}', "
            f"{domain.id}, '{user.username}', "
            f"'{public_key}', '{private_key}', "
            f"'{get_ap_url(user.username, 'followers')}', "
            f"'{get_ap_url(user.username, 'following')}', "
            f"'{get_ap_url(user.username, 'profile_url')}', "
            f"'{get_ap_url(user.username, 'inbox')}', "
            f"'{get_ap_url(user.username, 'outbox')}', "
            f"'{get_ap_url(user.username, 'shared_inbox')}', "
            f"'{created_at}'::timestamp) RETURNING id"
        )
        actor = connection.execute(
            actors_table.select().where(
                actors_table.c.preferred_username == user.username
            )
        ).fetchone()
        op.execute(
            f'UPDATE users SET actor_id = {actor.id} WHERE users.id = {user.id}'
        )
    op.alter_column('users', 'is_remote', nullable=False)

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reply_to', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_comments_reply_to'), ['reply_to'], unique=False)
        batch_op.create_foreign_key('comments_reply_to_fkey', 'comments', ['reply_to'], ['id'], ondelete='SET NULL')



def downgrade():
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('comments_reply_to_fkey', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_comments_reply_to'))
        batch_op.drop_column('reply_to')

    with op.batch_alter_table('workouts', schema=None) as batch_op:
        batch_op.drop_column('remote_url')
        batch_op.drop_column('ap_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_actor_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('users_actor_id_key', type_='unique')
        batch_op.drop_constraint('username_actor_id_unique', type_='unique')
        batch_op.create_unique_constraint('users_username_key', ['username'])
        batch_op.alter_column(
            'password', existing_type=sa.VARCHAR(length=255), nullable=False
        )
        batch_op.alter_column(
            'email', existing_type=sa.VARCHAR(length=255), nullable=False
        )
        batch_op.drop_column('is_remote')
        batch_op.drop_column('actor_id')

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('remote_url')
        batch_op.drop_column('ap_id')

    with op.batch_alter_table('remote_actors_stats', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_remote_actors_stats_actor_id'))

    op.drop_table('remote_actors_stats')
    op.drop_table('actors')
    op.execute('DROP TYPE actor_types')
    op.drop_table('domains')

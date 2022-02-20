"""init federation with ActivityPub Actor

Revision ID: 8842c351a2d8
Revises: 4e8597c50064
Create Date: 2021-01-10 16:02:43.811023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8842c351a2d8'
down_revision = 'e30007d681cb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'app_config',
        sa.Column(
            'federation_enabled', sa.Boolean(), nullable=True, default=False
        ),
    )
    op.execute('UPDATE app_config SET federation_enabled = false')
    op.alter_column('app_config', 'federation_enabled', nullable=False)

    op.create_table('domains',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_allowed', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table('actors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ap_id', sa.String(length=255), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('APPLICATION', 'GROUP', 'PERSON', name='actor_types'), server_default='PERSON', nullable=True),
        sa.Column('preferred_username', sa.String(length=255), nullable=False),
        sa.Column('public_key', sa.String(length=5000), nullable=True),
        sa.Column('private_key', sa.String(length=5000), nullable=True),
        sa.Column('inbox_url', sa.String(length=255), nullable=False),
        sa.Column('outbox_url', sa.String(length=255), nullable=False),
        sa.Column('followers_url', sa.String(length=255), nullable=False),
        sa.Column('following_url', sa.String(length=255), nullable=False),
        sa.Column('shared_inbox_url', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('manually_approves_followers', sa.Boolean(), nullable=False),
        sa.Column('last_fetch_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ap_id'),
        sa.UniqueConstraint('domain_id', 'preferred_username', name='domain_username_unique'),
    )

    op.add_column('users', sa.Column('actor_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('users_actor_id_key', 'users', ['actor_id'])
    op.create_foreign_key('users_actor_id_fkey', 'users', 'actors', ['actor_id'], ['id'])

    op.create_table('follow_requests',
        sa.Column('follower_actor_id', sa.Integer(), nullable=False),
        sa.Column('followed_actor_id', sa.Integer(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['followed_actor_id'], ['actors.id'], ),
        sa.ForeignKeyConstraint(['follower_actor_id'], ['actors.id'], ),
        sa.PrimaryKeyConstraint('follower_actor_id', 'followed_actor_id')
    )


def downgrade():
    op.drop_table('follow_requests')

    op.drop_constraint('users_actor_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('users_actor_id_key', 'users', type_='unique')
    op.drop_column('users', 'actor_id')

    op.drop_table('actors')
    op.execute('DROP TYPE actor_types')

    op.drop_table('domains')

    op.drop_column('app_config', 'federation_enabled')

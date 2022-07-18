"""update User and AppConfig tables

Revision ID: 5e3a3a31c432
Revises: e30007d681cb
Create Date: 2022-02-23 11:05:24.223304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e3a3a31c432'
down_revision = 'e30007d681cb'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'users', 'username', existing_type=sa.String(length=20),
        type_=sa.String(length=255), existing_nullable=False
    )
    op.alter_column(
        'users', 'email', existing_type=sa.String(length=120),
        type_=sa.String(length=255), existing_nullable=False
    )
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), default=False, nullable=True))
    op.execute("UPDATE users SET is_active = true")
    op.alter_column('users', 'is_active', nullable=False)
    op.add_column(
        'users',
        sa.Column('email_to_confirm', sa.String(length=255), nullable=True))
    op.add_column(
        'users',
        sa.Column('confirmation_token', sa.String(length=255), nullable=True))

    op.add_column(
        'app_config',
        sa.Column('admin_contact', sa.String(length=255), nullable=True)
    )


def downgrade():
    op.drop_column('app_config', 'admin_contact')

    op.drop_column('users', 'confirmation_token')
    op.drop_column('users', 'email_to_confirm')
    op.drop_column('users', 'is_active')
    op.alter_column(
        'users', 'email', existing_type=sa.String(length=255),
        type_=sa.String(length=120), existing_nullable=False
    )
    op.alter_column(
        'users', 'username', existing_type=sa.String(length=255),
        type_=sa.String(length=20), existing_nullable=False
    )

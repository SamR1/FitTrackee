"""update username length

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


def downgrade():
    op.alter_column(
        'users', 'username', existing_type=sa.String(length=255),
        type_=sa.String(length=20), existing_nullable=False
    )

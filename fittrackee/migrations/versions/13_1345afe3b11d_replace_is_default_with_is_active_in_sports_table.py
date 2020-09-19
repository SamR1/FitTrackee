"""replace 'is_default' with 'is_active' in 'Sports' table

Revision ID: 1345afe3b11d
Revises: f69f1e413bde
Create Date: 2019-09-22 17:57:00.595775

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1345afe3b11d'
down_revision = 'f69f1e413bde'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sports',
                  sa.Column('is_active',
                            sa.Boolean(create_constraint=50),
                            nullable=True))
    op.execute("UPDATE sports SET is_active = true")
    op.alter_column('sports', 'is_active', nullable=False)
    op.drop_column('sports', 'is_default')


def downgrade():
    op.add_column('sports',
                  sa.Column('is_default',
                            sa.Boolean(create_constraint=50),
                            nullable=True))
    op.execute("UPDATE sports SET is_default = true")
    op.alter_column('sports', 'is_default', nullable=False)
    op.drop_column('sports', 'is_active')

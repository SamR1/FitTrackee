"""add weather infos in 'Activity' table

Revision ID: 71093ac9ca44
Revises: e82e5e9447de
Create Date: 2018-06-13 15:29:11.715377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71093ac9ca44'
down_revision = 'e82e5e9447de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('activities', sa.Column('weather_end', sa.JSON(), nullable=True))
    op.add_column('activities', sa.Column('weather_start', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('activities', 'weather_start')
    op.drop_column('activities', 'weather_end')
    # ### end Alembic commands ###

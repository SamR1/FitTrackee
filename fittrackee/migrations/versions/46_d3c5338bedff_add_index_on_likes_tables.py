"""add index on likes tables

Revision ID: d3c5338bedff
Revises: d3e40c2bda80
Create Date: 2025-01-04 17:17:55.637816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3c5338bedff'
down_revision = 'd3e40c2bda80'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment_likes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_likes_comment_id'), ['comment_id'], unique=False)

    with op.batch_alter_table('workout_likes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_workout_likes_workout_id'), ['workout_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout_likes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workout_likes_workout_id'))

    with op.batch_alter_table('comment_likes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comment_likes_comment_id'))

    # ### end Alembic commands ###

"""add sport preferences

Revision ID: 080acc8ee956
Revises: 9842464bb885
Create Date: 2021-11-12 10:20:23.786727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '080acc8ee956'
down_revision = '9842464bb885'
branch_labels = None
depends_on = None


def upgrade():

    op.drop_constraint('sports_img_key', 'sports', type_='unique')
    op.drop_column('sports', 'img')

    op.create_table(
        'users_sports_preferences',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column(
            'stopped_speed_threshold',
            sa.Float(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['sport_id'],
            ['sports.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('user_id', 'sport_id'),
    )


def downgrade():
    op.drop_table('users_sports_preferences')

    op.add_column(
        'sports',
        sa.Column(
            'img', sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.create_unique_constraint('sports_img_key', 'sports', ['img'])
    op.execute(
        """
        UPDATE sports AS s
        SET img = si.img
        FROM (VALUES
            ('Cycling (Sport)','/img/sports/cycling-sport.png'),
            ('Cycling (Transport)','/img/sports/cycling-transport.png'),
            ('Hiking','/img/sports/hiking.png'),
            ('Mountain Biking','/img/sports/mountain-biking.png'),
            ('Running','/img/sports/running.png'),
            ('Walking','/img/sports/walking.png'),
            ('Mountain Biking (Electric)','/img/sports/electric-mountain-biking.png'),
            ('Trail','/img/sports/trail.png'),
            ('Skiing (Alpine)','/img/sports/alpine-skiing.png'),
            ('Skiing (Cross Country)','/img/sports/cross-country-skiing.png'),
            ('Rowing','/img/sports/rowing.png')
        ) AS si(label, img)
        WHERE si.label = s.label;
        """
    )

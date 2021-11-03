""" Add new sports

Revision ID: cee0830497f8
Revises: 4e8597c50064
Create Date: 2021-08-25 13:58:52.333603

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'cee0830497f8'
down_revision = '4e8597c50064'
branch_labels = None
depends_on = None


def upgrade():

    op.execute(
        """
        INSERT INTO sports (label, img, is_active)
        VALUES 
            ('Mountain Biking (Electric)', '/img/sports/electric-mountain-biking.png', True),
            ('Trail', '/img/sports/trail.png', True),
            ('Skiing (Alpine)', '/img/sports/alpine-skiing.png', True),
            ('Skiing (Cross Country)', '/img/sports/cross-country-skiing.png', True),
            ('Rowing', '/img/sports/rowing.png', True)
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM sports
        WHERE label = 'Mountain Biking (Electric)'
           OR label = 'Trail'
           OR label = 'Skiing (Alpine)'
           OR label = 'Skiing (Cross Country)'
           OR label = 'Rowing';
        """
    )

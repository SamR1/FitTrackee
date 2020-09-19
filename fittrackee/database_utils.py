from fittrackee import db
from fittrackee.activities.models import Sport
from fittrackee.application.utils import (
    init_config,
    update_app_config_from_database,
)
from fittrackee.users.models import User


def init_database(app):
    """Init the database."""
    admin = User(
        username='admin', email='admin@example.com', password='mpwoadmin'
    )
    admin.admin = True
    admin.timezone = 'Europe/Paris'
    db.session.add(admin)
    sport = Sport(label='Cycling (Sport)')
    sport.img = '/img/sports/cycling-sport.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Cycling (Transport)')
    sport.img = '/img/sports/cycling-transport.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Hiking')
    sport.img = '/img/sports/hiking.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Mountain Biking')
    sport.img = '/img/sports/mountain-biking.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Running')
    sport.img = '/img/sports/running.png'
    sport.is_default = True
    db.session.add(sport)
    sport = Sport(label='Walking')
    sport.img = '/img/sports/walking.png'
    sport.is_default = True
    db.session.add(sport)
    db.session.commit()
    _, db_app_config = init_config()
    update_app_config_from_database(app, db_app_config)

    print('Initial data stored in database.')

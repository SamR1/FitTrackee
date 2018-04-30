import datetime

from mpwo_api import db
from mpwo_api.activities.models import Activity, Sport
from mpwo_api.users.models import User


def add_admin():
    admin = User(
        username="admin",
        email="admin@example.com",
        password="12345678"
    )
    admin.admin = True
    db.session.add(admin)
    db.session.commit()
    return admin


def add_user(username, email, password):
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


def add_user_full(username, email, password):
    user = User(username=username, email=email, password=password)
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.bio = 'just a random guy'
    user.location = 'somewhere'
    user.birth_date = datetime.datetime.strptime('01/01/1980', '%d/%m/%Y')
    db.session.add(user)
    db.session.commit()
    return user


def add_sport(label):
    sport = Sport(label=label)
    db.session.add(sport)
    db.session.commit()
    return sport


def add_activity(user_id, sport_id, activity_date, duration):
    activity = Activity(
        user_id=user_id,
        sport_id=sport_id,
        activity_date=activity_date,
        duration=duration)
    db.session.add(activity)
    db.session.commit()
    return activity

import datetime

from mpwo_api import db
from mpwo_api.users.models import User


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

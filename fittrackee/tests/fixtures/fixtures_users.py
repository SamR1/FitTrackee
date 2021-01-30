import datetime

import pytest

from fittrackee import db
from fittrackee.users.models import User


@pytest.fixture()
def user_1() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_admin() -> User:
    admin = User(
        username='admin', email='admin@example.com', password='12345678'
    )
    admin.admin = True
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture()
def user_1_full() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.bio = 'just a random guy'
    user.location = 'somewhere'
    user.language = 'en'
    user.timezone = 'America/New_York'
    user.birth_date = datetime.datetime.strptime('01/01/1980', '%d/%m/%Y')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_paris() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.timezone = 'Europe/Paris'
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2() -> User:
    user = User(username='toto', email='toto@toto.com', password='87654321')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2_admin() -> User:
    user = User(username='toto', email='toto@toto.com', password='87654321')
    user.admin = True
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_3() -> User:
    user = User(username='sam', email='sam@test.com', password='12345678')
    user.weekm = True
    db.session.add(user)
    db.session.commit()
    return user

import datetime

import pytest

from fittrackee import db
from fittrackee.equipments.models import Equipment, EquipmentType
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Sport

from ..utils import random_string


@pytest.fixture()
def user_1() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.is_active = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_upper() -> User:
    user = User(username='TEST', email='TEST@TEST.COM', password='12345678')
    user.is_active = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_admin() -> User:
    admin = User(
        username='admin', email='admin@example.com', password='12345678'
    )
    admin.admin = True
    admin.is_active = True
    admin.accepted_policy = datetime.datetime.utcnow()
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
    user.is_active = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_raw_speed() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.bio = 'just a random guy'
    user.location = 'somewhere'
    user.language = 'en'
    user.timezone = 'America/New_York'
    user.birth_date = datetime.datetime.strptime('01/01/1980', '%d/%m/%Y')
    user.is_active = True
    user.use_raw_gpx_speed = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_paris() -> User:
    user = User(username='test', email='test@test.com', password='12345678')
    user.timezone = 'Europe/Paris'
    user.is_active = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2() -> User:
    user = User(username='toto', email='toto@toto.com', password='12345678')
    user.is_active = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2_admin() -> User:
    user = User(username='toto', email='toto@toto.com', password='12345678')
    user.is_active = True
    user.admin = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_3() -> User:
    user = User(username='sam', email='sam@test.com', password='12345678')
    user.is_active = True
    user.weekm = True
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def inactive_user() -> User:
    user = User(
        username='inactive', email='inactive@example.com', password='12345678'
    )
    user.confirmation_token = random_string()
    user.accepted_policy = datetime.datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_sport_1_preference(
    user_1: User,
    sport_1_cycling: Sport,
    equipment_type_1_shoe: EquipmentType,
    equipment_type_2_bike: EquipmentType,
    equipment_bike_user_1: Equipment,
) -> UserSportPreference:
    user_sport = UserSportPreference(
        user_id=user_1.id,
        sport_id=sport_1_cycling.id,
        stopped_speed_threshold=sport_1_cycling.stopped_speed_threshold,
    )
    db.session.add(user_sport)
    db.session.commit()
    return user_sport


@pytest.fixture()
def user_admin_sport_1_preference(
    user_1_admin: User,
    sport_1_cycling: Sport,
    equipment_type_1_shoe: EquipmentType,
    equipment_type_2_bike: EquipmentType,
    equipment_bike_user_1: Equipment,
) -> UserSportPreference:
    user_sport = UserSportPreference(
        user_id=user_1_admin.id,
        sport_id=sport_1_cycling.id,
        stopped_speed_threshold=sport_1_cycling.stopped_speed_threshold,
    )
    db.session.add(user_sport)
    db.session.commit()
    return user_sport

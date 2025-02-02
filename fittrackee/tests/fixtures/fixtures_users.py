from datetime import datetime, timezone

import pytest

from fittrackee import db
from fittrackee.users.models import FollowRequest, User, UserSportPreference
from fittrackee.users.roles import UserRole
from fittrackee.workouts.models import Sport

from ..utils import generate_follow_request, random_string


@pytest.fixture()
def user_1() -> User:
    user = User(username="test", email="test@test.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_upper() -> User:
    user = User(username="TEST", email="TEST@TEST.COM", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_admin() -> User:
    admin = User(
        username="admin", email="admin@example.com", password="12345678"
    )
    admin.role = UserRole.ADMIN.value
    admin.hide_profile_in_users_directory = False
    admin.is_active = True
    admin.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture()
def user_1_moderator() -> User:
    moderator = User(
        username="moderator",
        email="moderator@example.com",
        password="12345678",
    )
    moderator.role = UserRole.MODERATOR.value
    moderator.hide_profile_in_users_directory = False
    moderator.is_active = True
    moderator.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(moderator)
    db.session.commit()
    return moderator


@pytest.fixture()
def user_1_owner() -> User:
    owner = User(
        username="owner", email="owner@example.com", password="12345678"
    )
    owner.role = UserRole.OWNER.value
    owner.hide_profile_in_users_directory = False
    owner.is_active = True
    owner.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(owner)
    db.session.commit()
    return owner


@pytest.fixture()
def user_1_full() -> User:
    user = User(username="test", email="test@test.com", password="12345678")
    user.first_name = "John"
    user.last_name = "Doe"
    user.bio = "just a random guy"
    user.location = "somewhere"
    user.language = "en"
    user.timezone = "America/New_York"
    user.birth_date = datetime(1980, 1, 1, tzinfo=timezone.utc)
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_raw_speed() -> User:
    user = User(username="test", email="test@test.com", password="12345678")
    user.first_name = "John"
    user.last_name = "Doe"
    user.bio = "just a random guy"
    user.location = "somewhere"
    user.language = "en"
    user.timezone = "America/New_York"
    user.birth_date = datetime(1980, 1, 1, tzinfo=timezone.utc)
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.use_raw_gpx_speed = True
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_paris() -> User:
    user = User(username="test", email="test@test.com", password="12345678")
    user.timezone = "Europe/Paris"
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2() -> User:
    user = User(username="toto", email="toto@toto.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2_owner() -> User:
    user = User(username="toto", email="toto@toto.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.role = UserRole.OWNER.value
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2_admin() -> User:
    user = User(username="toto", email="toto@toto.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.role = UserRole.ADMIN.value
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_2_moderator() -> User:
    user = User(username="toto", email="toto@toto.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.role = UserRole.MODERATOR.value
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_3() -> User:
    user = User(username="sam", email="sam@test.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.weekm = True
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_3_admin() -> User:
    user = User(username="sam", email="sam@test.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.role = UserRole.ADMIN.value
    user.weekm = True
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_4() -> User:
    user = User(username="john", email="john@doe.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.weekm = True
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def inactive_user() -> User:
    user = User(
        username="inactive", email="inactive@example.com", password="12345678"
    )
    user.confirmation_token = random_string()
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def suspended_user() -> User:
    user = User(
        username="suspended_user",
        email="suspended_user@example.com",
        password="12345678",
    )
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    user.suspended_at = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def user_1_sport_1_preference(
    user_1: User,
    sport_1_cycling: Sport,
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
) -> UserSportPreference:
    user_sport = UserSportPreference(
        user_id=user_1_admin.id,
        sport_id=sport_1_cycling.id,
        stopped_speed_threshold=sport_1_cycling.stopped_speed_threshold,
    )
    db.session.add(user_sport)
    db.session.commit()
    return user_sport


@pytest.fixture()
def user_1_sport_2_preference(
    user_1: User,
    sport_2_running: Sport,
) -> UserSportPreference:
    user_sport = UserSportPreference(
        user_id=user_1.id,
        sport_id=sport_2_running.id,
        stopped_speed_threshold=sport_2_running.stopped_speed_threshold,
    )
    db.session.add(user_sport)
    db.session.commit()
    return user_sport


@pytest.fixture()
def user_2_sport_2_preference(
    user_1: User,
    user_2: User,
    sport_2_running: Sport,
) -> UserSportPreference:
    user_sport = UserSportPreference(
        user_id=user_2.id,
        sport_id=sport_2_running.id,
        stopped_speed_threshold=sport_2_running.stopped_speed_threshold,
    )
    db.session.add(user_sport)
    db.session.commit()
    return user_sport


@pytest.fixture()
def follow_request_from_user_1_to_user_2(
    user_1: User, user_2: User
) -> FollowRequest:
    return generate_follow_request(user_1, user_2)


@pytest.fixture()
def follow_request_from_user_2_to_user_1(
    user_1: User, user_2: User
) -> FollowRequest:
    return generate_follow_request(user_2, user_1)


@pytest.fixture()
def follow_request_from_user_3_to_user_1(
    user_1: User, user_3: User
) -> FollowRequest:
    return generate_follow_request(user_3, user_1)


@pytest.fixture()
def follow_request_from_user_3_to_user_2(
    user_2: User, user_3: User
) -> FollowRequest:
    return generate_follow_request(user_3, user_2)

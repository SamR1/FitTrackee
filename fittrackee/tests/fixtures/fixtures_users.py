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
    db.session.flush()
    user.create_actor()
    db.session.commit()
    return user


@pytest.fixture()
def user_1_upper() -> User:
    user = User(username="TEST", email="TEST@TEST.COM", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.flush()
    user.create_actor()
    db.session.commit()
    return user


@pytest.fixture()
def user_1_admin(user_1: User) -> User:
    user_1.username = "admin"
    user_1.email = "admin@example.com"
    user_1.role = UserRole.ADMIN.value
    db.session.commit()
    return user_1


@pytest.fixture()
def user_1_moderator(user_1: User) -> User:
    user_1.username = "moderator"
    user_1.email = "moderator@example.com"
    user_1.role = UserRole.MODERATOR.value
    db.session.commit()
    return user_1


@pytest.fixture()
def user_1_owner(user_1: User) -> User:
    user_1.username = "owner"
    user_1.email = "owner@example.com"
    user_1.role = UserRole.OWNER.value
    db.session.commit()
    return user_1


@pytest.fixture()
def user_1_full(user_1: User) -> User:
    user_1.first_name = "John"
    user_1.last_name = "Doe"
    user_1.bio = "just a random guy"
    user_1.location = "somewhere"
    user_1.language = "en"
    user_1.timezone = "America/New_York"
    user_1.birth_date = datetime(1980, 1, 1, tzinfo=timezone.utc)
    db.session.commit()
    return user_1


@pytest.fixture()
def user_1_raw_speed(user_1_full: User) -> User:
    user_1_full.use_raw_gpx_speed = True
    db.session.commit()
    return user_1_full


@pytest.fixture()
def user_1_paris(user_1: User) -> User:
    user_1.timezone = "Europe/Paris"
    db.session.commit()
    return user_1


@pytest.fixture()
def user_2() -> User:
    user = User(username="toto", email="toto@toto.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.flush()
    user.create_actor()
    db.session.commit()
    return user


@pytest.fixture()
def user_2_owner(user_2: User) -> User:
    user_2.role = UserRole.OWNER.value
    db.session.commit()
    return user_2


@pytest.fixture()
def user_2_admin(user_2: User) -> User:
    user_2.role = UserRole.ADMIN.value
    db.session.commit()
    return user_2


@pytest.fixture()
def user_2_moderator(user_2: User) -> User:
    user_2.role = UserRole.MODERATOR.value
    db.session.commit()
    return user_2


@pytest.fixture()
def user_3() -> User:
    user = User(username="sam", email="sam@test.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.weekm = True
    user.accepted_policy_date = datetime.now(timezone.utc)
    db.session.add(user)
    db.session.flush()
    user.create_actor()
    db.session.commit()
    return user


@pytest.fixture()
def user_3_admin(user_3: User) -> User:
    user_3.role = UserRole.ADMIN.value
    db.session.commit()
    return user_3


@pytest.fixture()
def user_4() -> User:
    user = User(username="john", email="john@doe.com", password="12345678")
    user.is_active = True
    user.hide_profile_in_users_directory = False
    user.weekm = True
    db.session.add(user)
    db.session.flush()
    user.create_actor()
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
    db.session.flush()
    user.create_actor()
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
    db.session.flush()
    user.create_actor()
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

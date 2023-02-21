import pytest

from fittrackee import db
from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import FollowRequest, User

from ..utils import (
    generate_follow_request,
    get_remote_user_object,
    random_string,
)


def generate_remote_user(
    remote_domain: Domain, without_profile_page: bool = False
) -> User:
    domain = f'https://{remote_domain.name}'
    user_name = random_string()[0:30]
    if without_profile_page:
        remote_user_object = get_remote_user_object(
            username=user_name.capitalize(),
            preferred_username=user_name,
            domain=domain,
        )
    else:
        remote_user_object = get_remote_user_object(
            username=user_name.capitalize(),
            preferred_username=user_name,
            domain=domain,
            profile_url=f'{domain}/{user_name}',
        )
    actor = Actor(
        preferred_username=user_name,
        domain_id=remote_domain.id,
        remote_user_data=remote_user_object,
    )
    db.session.add(actor)
    db.session.flush()
    user = User(username=user_name, email=None, password=None, is_remote=True)
    db.session.add(user)
    user.actor_id = actor.id
    user.is_active = True
    db.session.commit()
    return user


@pytest.fixture()
def remote_user(remote_domain: Domain) -> User:
    return generate_remote_user(remote_domain)


@pytest.fixture()
def remote_user_2(another_remote_domain: Domain) -> User:
    return generate_remote_user(another_remote_domain)


@pytest.fixture()
def remote_user_without_profile_page(remote_domain: Domain) -> User:
    return generate_remote_user(remote_domain, without_profile_page=True)


@pytest.fixture()
def follow_request_from_remote_user_to_user_1(
    user_1: User,
    remote_user: User,
) -> FollowRequest:
    return generate_follow_request(remote_user, user_1)


@pytest.fixture()
def follow_request_from_user_1_to_remote_user(
    user_1: User,
    remote_user: User,
) -> FollowRequest:
    return generate_follow_request(user_1, remote_user)

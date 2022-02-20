import pytest
from flask import Flask

from fittrackee import db
from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import User

from ..utils import RandomActor, get_remote_user_object, random_domain


@pytest.fixture()
def app_actor(app: Flask) -> Actor:
    domain = Domain.query.filter_by(name=app.config['AP_DOMAIN']).first()
    actor = Actor(preferred_username='test', domain_id=domain.id)
    db.session.add(actor)
    db.session.commit()
    return actor


@pytest.fixture()
def remote_domain(app_with_federation: Flask) -> Domain:
    remote_domain = Domain(name=random_domain())
    db.session.add(remote_domain)
    db.session.commit()
    return remote_domain


def generate_remote_user(
    remote_domain: Domain, without_profile_page: bool = False
) -> User:
    domain = f'https://{remote_domain.name}'
    user_name = 'test'
    if without_profile_page:
        remote_user_object = get_remote_user_object(
            username='Test',
            preferred_username=user_name,
            domain=domain,
        )
    else:
        remote_user_object = get_remote_user_object(
            username='Test',
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
    user = User(
        username=user_name,
        email=None,
        password=None,
    )
    db.session.add(user)
    user.actor_id = actor.id
    db.session.commit()
    return user


@pytest.fixture()
def remote_user(remote_domain: Domain) -> User:
    return generate_remote_user(remote_domain)


@pytest.fixture()
def remote_user_without_profile_page(remote_domain: Domain) -> User:
    return generate_remote_user(remote_domain, without_profile_page=True)


@pytest.fixture()
def random_actor() -> RandomActor:
    return RandomActor()


@pytest.fixture()
def random_actor_2() -> RandomActor:
    return RandomActor()

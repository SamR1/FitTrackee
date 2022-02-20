import pytest
from flask import Flask

from fittrackee import db
from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import User

from ..utils import get_remote_user_object, random_domain


@pytest.fixture()
def app_actor(app: Flask) -> Actor:
    domain = Domain.query.filter_by(name=app.config['AP_DOMAIN']).first()
    actor = Actor(preferred_username='test', domain_id=domain.id)
    db.session.add(actor)
    db.session.commit()
    return actor


@pytest.fixture()
def actor_1(user_1: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(preferred_username=user_1.username, domain_id=domain.id)
    db.session.add(actor)
    db.session.flush()
    user_1.actor_id = actor.id
    db.session.commit()
    return actor


@pytest.fixture()
def actor_2(user_2: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(preferred_username=user_2.username, domain_id=domain.id)
    db.session.add(actor)
    db.session.flush()
    user_2.actor_id = actor.id
    db.session.commit()
    return actor


@pytest.fixture()
def actor_3(user_3: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(preferred_username=user_3.username, domain_id=domain.id)
    db.session.add(actor)
    db.session.flush()
    user_3.actor_id = actor.id
    db.session.commit()
    return actor


@pytest.fixture()
def remote_domain(app_with_federation: Flask) -> Domain:
    remote_domain = Domain(name=random_domain())
    db.session.add(remote_domain)
    db.session.commit()
    return remote_domain


@pytest.fixture()
def remote_actor(
    user_2: User, app_with_federation: Flask, remote_domain: Domain
) -> Actor:
    domain = f'https://{remote_domain.name}'
    remote_user_object = get_remote_user_object(
        username=user_2.username, domain_with_scheme=domain
    )
    actor = Actor(
        preferred_username=user_2.username,
        domain_id=remote_domain.id,
        remote_user_data=remote_user_object,
    )
    db.session.add(actor)
    db.session.flush()
    user_2.name = user_2.username.capitalize()
    user_2.actor_id = actor.id
    db.session.commit()
    return actor

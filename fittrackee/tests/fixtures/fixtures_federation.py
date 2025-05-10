import pytest
from flask import Flask

from fittrackee import db
from fittrackee.federation.models import Actor, Domain

from ..utils import RandomActor, random_domain


@pytest.fixture()
def app_actor(app: Flask) -> Actor:
    domain = Domain.query.filter_by(name=app.config["AP_DOMAIN"]).one()
    actor = Actor(preferred_username="test", domain_id=domain.id)
    db.session.add(actor)
    db.session.commit()
    return actor


@pytest.fixture()
def remote_domain(app_with_federation: Flask) -> Domain:
    remote_domain = Domain(name=random_domain(), software_name="fittrackee")
    db.session.add(remote_domain)
    db.session.commit()
    return remote_domain


@pytest.fixture()
def another_remote_domain(app_with_federation: Flask) -> Domain:
    remote_domain = Domain(name=random_domain(), software_name="mastodon")
    db.session.add(remote_domain)
    db.session.commit()
    return remote_domain


@pytest.fixture()
def random_actor() -> RandomActor:
    return RandomActor()


@pytest.fixture()
def random_actor_2() -> RandomActor:
    return RandomActor()

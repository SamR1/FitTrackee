import pytest
from flask import Flask

from fittrackee import db
from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import User


@pytest.fixture()
def actor_1(user_1: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(username=user_1.username, domain_id=domain.id)
    db.session.add(actor)
    user_1.actor_id = actor.id
    db.session.commit()
    return actor


@pytest.fixture()
def app_actor(app: Flask) -> Actor:
    domain = Domain.query.filter_by(name=app.config['AP_DOMAIN']).first()
    actor = Actor(username='test', domain_id=domain.id)
    db.session.add(actor)
    db.session.commit()
    return actor

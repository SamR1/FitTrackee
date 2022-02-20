import pytest
from flask import Flask

from fittrackee import db
from fittrackee.federation.models import Actor, Domain, FollowRequest
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


@pytest.fixture()
def actor_2(user_2: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(username=user_2.username, domain_id=domain.id)
    db.session.add(actor)
    user_2.actor_id = actor.id
    db.session.commit()
    return actor


@pytest.fixture()
def actor_3(user_3: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(username=user_3.username, domain_id=domain.id)
    db.session.add(actor)
    user_3.actor_id = actor.id
    db.session.commit()
    return actor


@pytest.fixture()
def follow_request_from_actor_2_to_actor_1(
    actor_1: Actor, actor_2: Actor
) -> FollowRequest:
    follow_request = FollowRequest(
        followed_actor_id=actor_1.id, follower_actor_id=actor_2.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request


@pytest.fixture()
def follow_request_from_actor_3_to_actor_1(
    actor_1: Actor, actor_3: Actor
) -> FollowRequest:
    follow_request = FollowRequest(
        followed_actor_id=actor_1.id, follower_actor_id=actor_3.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.federation.models import Actor, Domain
from fittrackee.users.models import User

from ..utils import random_domain


@pytest.fixture()
def app_actor(app: Flask) -> Actor:
    domain = Domain.query.filter_by(name=app.config['AP_DOMAIN']).first()
    actor = Actor(username='test', domain_id=domain.id)
    db.session.add(actor)
    db.session.commit()
    return actor


@pytest.fixture()
def actor_1(user_1: User, app_with_federation: Flask) -> Actor:
    domain = Domain.query.filter_by(
        name=app_with_federation.config['AP_DOMAIN']
    ).first()
    actor = Actor(username=user_1.username, domain_id=domain.id)
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
    actor = Actor(username=user_2.username, domain_id=domain.id)
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
    actor = Actor(username=user_3.username, domain_id=domain.id)
    db.session.add(actor)
    user_3.actor_id = actor.id
    db.session.flush()
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
    user_name = user_2.username.capitalize()
    user_url = f'{remote_domain.name}/users/{user_2.username}'
    actor = Actor(
        username=user_2.username,
        domain_id=remote_domain.id,
        remote_user_data={
            '@context': [
                'https://www.w3.org/ns/activitystreams',
                'https://w3id.org/security/v1',
            ],
            'id': user_url,
            'type': 'Person',
            'following': f'{user_url}/following',
            'followers': f'{user_url}/followers',
            'inbox': f'{user_url}/inbox',
            'outbox': f'{user_url}/outbox',
            'name': user_name,
            'preferredUsername': user_2.username,
            'endpoints': {'sharedInbox': f'{remote_domain.name}/inbox'},
        },
    )
    db.session.add(actor)
    db.session.flush()
    user_2.name = user_name
    user_2.actor_id = actor.id
    db.session.commit()
    return actor

import re
from typing import Optional
from urllib.parse import urlparse

from fittrackee import db
from fittrackee.federation.exceptions import RemoteActorException
from fittrackee.federation.models import Actor, Domain
from fittrackee.federation.remote_actor import get_remote_actor
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User

from .exceptions import ActorNotFoundException, DomainNotFoundException


def get_username_and_domain(full_name: str) -> Optional[re.Match]:
    full_name_pattern = r'([\w_\-\.]+)@([\w_\-\.]+\.[a-z]{2,})'
    return re.match(full_name_pattern, full_name)


def get_user_from_username(user_name: str) -> User:
    user_name_and_domain = get_username_and_domain(user_name)
    if user_name_and_domain is None:  # local actor
        user = User.query.filter_by(username=user_name).first()
    else:  # remote actor
        name, domain_name = user_name_and_domain.groups()
        domain = Domain.query.filter_by(name=domain_name).first()
        if not domain:
            raise DomainNotFoundException(domain_name)
        actor = Actor.query.filter_by(
            preferred_username=name, domain_id=domain.id
        ).first()
        if not actor:
            raise ActorNotFoundException()
        user = actor.user
    if not user:
        raise UserNotFoundException()
    return user


def create_remote_user(remote_actor_url: Optional[str]) -> Actor:
    if not remote_actor_url:
        raise RemoteActorException('invalid remote actor url')

    # check if domain already exists
    remote_domain_name = urlparse(remote_actor_url).netloc
    remote_domain = Domain.query.filter_by(name=remote_domain_name).first()
    if not remote_domain:
        remote_domain = Domain(name=remote_domain_name)
        db.session.add(remote_domain)
        db.session.flush()

    if not remote_domain.is_remote:
        raise RemoteActorException(
            'the provided account is not a remote account'
        )

    try:
        remote_actor_object = get_remote_actor(remote_actor_url)
    except ActorNotFoundException:
        raise RemoteActorException('can not fetch remote actor')

    # check if actor already exists
    try:
        actor = Actor.query.filter_by(
            preferred_username=remote_actor_object['preferredUsername'],
            domain_id=remote_domain.id,
        ).first()
    except KeyError:
        raise RemoteActorException('invalid remote actor object')

    if not actor:
        try:
            actor = Actor(
                preferred_username=remote_actor_object['preferredUsername'],
                domain_id=remote_domain.id,
                remote_user_data=remote_actor_object,
            )
        except KeyError:
            raise RemoteActorException('invalid remote actor object')
        db.session.add(actor)
        db.session.flush()
        user = User(
            username=remote_actor_object['name'],
            email=None,
            password=None,
        )
        db.session.add(user)
        user.actor_id = actor.id
    else:
        actor.update_remote_data(remote_actor_object)
        actor.user.username = remote_actor_object['name']
    db.session.commit()
    return actor

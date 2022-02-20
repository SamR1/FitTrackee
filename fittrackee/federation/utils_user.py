import re
from typing import Optional

from fittrackee.federation.models import Actor, Domain
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

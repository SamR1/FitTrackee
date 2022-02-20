import pytest

from fittrackee import db
from fittrackee.federation.models import Actor
from fittrackee.users.models import User


@pytest.fixture()
def actor_1(user_1: User) -> Actor:
    actor = Actor(user=user_1)
    db.session.add(actor)
    db.session.commit()
    return actor

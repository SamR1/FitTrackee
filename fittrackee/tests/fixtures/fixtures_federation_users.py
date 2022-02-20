import pytest

from fittrackee import db
from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest


@pytest.fixture()
def follow_request_from_user_1_to_user_2_with_federation(
    actor_1: Actor,
    actor_2: Actor,
) -> FollowRequest:
    follow_request = FollowRequest(
        follower_user_id=actor_1.user.id, followed_user_id=actor_2.user.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request


@pytest.fixture()
def follow_request_from_user_2_to_user_1_with_federation(
    actor_1: Actor,
    actor_2: Actor,
) -> FollowRequest:
    follow_request = FollowRequest(
        follower_user_id=actor_2.user.id, followed_user_id=actor_1.user.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request


@pytest.fixture()
def follow_request_from_remote_user_to_user_1(
    actor_1: Actor,
    remote_actor: Actor,
) -> FollowRequest:
    follow_request = FollowRequest(
        follower_user_id=remote_actor.user.id, followed_user_id=actor_1.user.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request


@pytest.fixture()
def follow_request_from_user_1_to_remote_actor(
    actor_1: Actor,
    remote_actor: Actor,
) -> FollowRequest:
    follow_request = FollowRequest(
        follower_user_id=actor_1.user.id, followed_user_id=remote_actor.user.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request

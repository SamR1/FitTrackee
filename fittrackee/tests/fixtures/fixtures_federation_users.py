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

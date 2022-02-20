import pytest

from fittrackee.users.models import FollowRequest, User

from ..utils import generate_follow_request


@pytest.fixture()
def follow_request_from_remote_user_to_user_1(
    user_1: User,
    remote_user: User,
) -> FollowRequest:
    return generate_follow_request(remote_user, user_1)


@pytest.fixture()
def follow_request_from_user_1_to_remote_user(
    user_1: User,
    remote_user: User,
) -> FollowRequest:
    return generate_follow_request(user_1, remote_user)

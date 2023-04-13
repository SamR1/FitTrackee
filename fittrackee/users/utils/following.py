from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..models import User


def get_following(user: "User") -> List:
    following_ids = []
    for following in user.following:
        following_ids.append(following.id)
    return following_ids

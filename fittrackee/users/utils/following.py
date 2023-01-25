from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from ..models import User


def get_following(user: "User") -> Tuple[List, List]:
    local_following_ids = []
    remote_following_ids = []
    for following in user.following:
        if following.is_remote is True:
            remote_following_ids.append(following.id)
        else:
            local_following_ids.append(following.id)
    return local_following_ids, remote_following_ids

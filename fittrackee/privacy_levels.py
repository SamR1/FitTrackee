from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from fittrackee.comments.models import Comment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class PrivacyLevel(str, Enum):  # to make enum serializable
    PUBLIC = 'public'
    FOLLOWERS = 'followers_only'  # only local followers in federated instances
    PRIVATE = 'private'  # in case of comments, for mentioned users only


def get_map_visibility(
    map_visibility: PrivacyLevel, workout_visibility: PrivacyLevel
) -> PrivacyLevel:
    # workout privacy overrides map privacy, when stricter
    if workout_visibility == PrivacyLevel.PRIVATE or (
        workout_visibility == PrivacyLevel.FOLLOWERS
        and map_visibility == PrivacyLevel.PUBLIC
    ):
        return workout_visibility
    return map_visibility


def can_view(
    target_object: Union['Workout', 'Comment'],
    visibility: str,
    user: Optional['User'] = None,
) -> bool:
    if (
        target_object.__getattribute__(visibility) == PrivacyLevel.PUBLIC
        or user == target_object.user
    ):
        return True

    if not user:
        return False

    if (
        target_object.__class__.__name__ == "Comment"
        and user in target_object.mentioned_users.all()
    ):
        return True

    if (
        target_object.__getattribute__(visibility) == PrivacyLevel.FOLLOWERS
        and user in target_object.user.followers
    ):
        return True

    return False

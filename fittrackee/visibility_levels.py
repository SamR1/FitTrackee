from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from fittrackee.comments.models import Comment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class VisibilityLevel(str, Enum):  # to make enum serializable
    PUBLIC = 'public'
    FOLLOWERS = 'followers_only'  # only followers
    PRIVATE = 'private'  # in case of comments, for mentioned users only


def get_map_visibility(
    map_visibility: VisibilityLevel, workout_visibility: VisibilityLevel
) -> VisibilityLevel:
    # workout visibility overrides map visibility, when stricter
    if workout_visibility == VisibilityLevel.PRIVATE or (
        workout_visibility == VisibilityLevel.FOLLOWERS
        and map_visibility == VisibilityLevel.PUBLIC
    ):
        return workout_visibility
    return map_visibility


def can_view(
    target_object: Union['Workout', 'Comment'],
    visibility: str,
    user: Optional['User'] = None,
    for_report: bool = False,
) -> bool:
    owner = target_object.user
    if user and (
        user.id == owner.id or (user.has_moderator_rights and for_report)
    ):
        return True

    if (
        target_object.__class__.__name__ == "Workout"
        and target_object.suspended_at
    ):
        if not user:
            return False

        from fittrackee.comments.models import Comment

        user_comments_count = Comment.query.filter_by(
            workout_id=target_object.id, user_id=user.id
        ).count()
        if user_comments_count == 0:
            return False

    if target_object.__getattribute__(
        visibility
    ) == VisibilityLevel.PUBLIC and (
        not user or not user.is_blocked_by(owner)
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
        target_object.__getattribute__(visibility) == VisibilityLevel.FOLLOWERS
        and user in owner.followers.all()
    ):
        return True

    # visibility level is private
    return False

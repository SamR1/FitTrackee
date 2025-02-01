from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from fittrackee.comments.models import Comment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class VisibilityLevel(str, Enum):  # to make enum serializable
    PUBLIC = "public"
    FOLLOWERS_AND_REMOTE = "followers_and_remote_only"
    FOLLOWERS = "followers_only"  # only local followers in federated instances
    PRIVATE = "private"  # in case of comments, for mentioned users only


def get_calculated_visibility(
    *, visibility: VisibilityLevel, parent_visibility: VisibilityLevel
) -> VisibilityLevel:
    # - workout visibility overrides analysis visibility, when stricter,
    # - analysis visibility overrides map visibility, when stricter.
    if (
        parent_visibility == VisibilityLevel.PRIVATE
        or (
            parent_visibility == VisibilityLevel.FOLLOWERS
            and visibility
            in [VisibilityLevel.FOLLOWERS_AND_REMOTE, VisibilityLevel.PUBLIC]
        )
        or (
            parent_visibility == VisibilityLevel.FOLLOWERS_AND_REMOTE
            and visibility == VisibilityLevel.PUBLIC
        )
    ):
        return parent_visibility
    return visibility


def can_view(
    target_object: Union["Workout", "Comment"],
    visibility: str,
    user: Optional["User"] = None,
    for_report: bool = False,
) -> bool:
    from fittrackee.comments.models import Comment

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
        isinstance(target_object, Comment)
        and user in target_object.mentioned_users.all()
    ):
        return True

    if (
        target_object.__getattribute__(visibility) == VisibilityLevel.FOLLOWERS
        and user.is_remote is False
        and user in owner.followers.all()
        and target_object.user.is_remote is False
    ):
        return True

    if (
        target_object.__getattribute__(visibility)
        == VisibilityLevel.FOLLOWERS_AND_REMOTE
        and user in owner.followers.all()
    ):
        return True

    # visibility level is private
    return False

from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from fittrackee.comments.models import Comment
    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class VisibilityLevel(str, Enum):  # to make enum serializable
    PUBLIC = "public"
    FOLLOWERS = "followers_only"  # only followers
    PRIVATE = "private"  # in case of comments, for mentioned users only


def get_calculated_visibility(
    *, visibility: VisibilityLevel, parent_visibility: VisibilityLevel
) -> VisibilityLevel:
    # - workout visibility overrides analysis visibility, when stricter,
    # - analysis visibility overrides map visibility, when stricter.
    if parent_visibility == VisibilityLevel.PRIVATE or (
        parent_visibility == VisibilityLevel.FOLLOWERS
        and visibility == VisibilityLevel.PUBLIC
    ):
        return parent_visibility
    return visibility


def can_view(
    target_object: Union["Workout", "Comment", "Equipment"],
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
        and target_object.suspended_at  # type: ignore
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
        and user in owner.followers.all()
    ):
        return True

    # visibility level is private
    return False


def can_view_heart_rate(
    target_user: "User",
    user: Optional["User"] = None,
) -> bool:
    if user and (user.id == target_user.id):
        return True

    if target_user.hr_visibility == VisibilityLevel.PUBLIC and (
        not user or not user.is_blocked_by(target_user)
    ):
        return True

    if not user:
        return False

    if (
        target_user.hr_visibility == VisibilityLevel.FOLLOWERS
        and user in target_user.followers.all()
    ):
        return True

    # visibility level is private
    return False

from typing import TYPE_CHECKING, Optional

from fittrackee.privacy_levels import PrivacyLevel

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import WorkoutComment


def can_view_workout_comment(
    workout_comment: 'WorkoutComment',
    user: Optional['User'] = None,
) -> bool:
    # TODO: handle mentions
    if (
        workout_comment.text_visibility == PrivacyLevel.PUBLIC
        or user == workout_comment.user
    ):
        return True

    if not user:
        return False

    if (
        workout_comment.text_visibility == PrivacyLevel.FOLLOWERS
        and user in workout_comment.user.followers
        and user.is_remote is False
        and workout_comment.user.is_remote is False
    ):
        return True

    if (
        workout_comment.text_visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
        and user in workout_comment.user.followers
    ):
        return True

    return False

from typing import Optional, Tuple

from fittrackee.users.models import User
from fittrackee.users.privacy_levels import PrivacyLevel
from fittrackee.workouts.models import Workout


def can_view_workout(
    workout: Workout,
    visibility: str,
    user: Optional[User] = None,
) -> Tuple[bool, str]:
    """
    returns if user can view workout and status used by workout serializer

    status:
    - owner: provided user is workout owner
    - follower: provided user follows workout owner
    - other: other cases (user does not follow workout owner,
      unauthenticated user (no user provided)
    """
    status = 'other'
    if user is not None:
        status = (
            'owner'
            if workout.user_id == user.id
            else 'follower'
            if user in workout.user.followers
            else 'other'
        )
    visibility = getattr(workout, visibility)
    if (
        visibility == PrivacyLevel.PUBLIC
        or user is not None
        and (
            workout.user_id == user.id
            or (
                user in workout.user.followers
                and visibility == PrivacyLevel.FOLLOWERS
            )
        )
    ):
        return True, status
    return False, status

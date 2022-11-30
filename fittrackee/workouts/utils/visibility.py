from typing import Optional, Tuple

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
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
    - remote_follower: provided user follows workout owner from remote instance
    - other: other cases (user does not follow workout owner,
      unauthenticated user (no user provided))
    """
    status = 'other'
    if user is not None:
        if workout.user_id == user.id:
            status = 'owner'
        if user in workout.user.followers:
            status = (
                'remote_follower' if workout.user.is_remote else 'follower'
            )

    visibility = getattr(workout, visibility)
    if (
        visibility == PrivacyLevel.PUBLIC
        or user is not None
        and (
            workout.user_id == user.id
            or (
                user in workout.user.followers
                and visibility
                in [PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS_AND_REMOTE]
                and status == 'follower'
            )
            or (
                user in workout.user.followers
                and visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
                and status == 'remote_follower'
            )
        )
    ):
        return True, status
    return False, status


def get_workout_user_status(
    workout: Workout,
    user: Optional[User] = None,
) -> str:
    """
    returns user status depending on workout visibility and relationship

    status:
    - owner: provided user is workout owner
    - follower: provided user follows workout owner
    - other: other cases (user does not follow workout owner,
      unauthenticated user (no user provided))
    """
    _, user_status = can_view_workout(workout, 'workout_visibility', user)
    return user_status

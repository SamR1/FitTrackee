from typing import Optional

from fittrackee.responses import ForbiddenErrorResponse, HttpResponse


def can_view_workout(
    auth_user_id: int, workout_user_id: int
) -> Optional[HttpResponse]:
    """
    Return error response if user has no right to view workout
    """
    if auth_user_id != workout_user_id:
        return ForbiddenErrorResponse()
    return None

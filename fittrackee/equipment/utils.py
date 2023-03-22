from typing import Optional

from fittrackee.responses import ForbiddenErrorResponse, HttpResponse


def can_view_equipment(
    auth_user_id: int, equipment_user_id: int
) -> Optional[HttpResponse]:
    """
    Return error response if user has no right to view equipment
    """
    if auth_user_id != equipment_user_id:
        return ForbiddenErrorResponse("User not authorized for that equipment")
    return None

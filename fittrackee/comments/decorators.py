from functools import wraps
from typing import Any, Callable

from fittrackee.privacy_levels import can_view
from fittrackee.responses import ForbiddenErrorResponse, NotFoundErrorResponse
from fittrackee.utils import decode_short_id

from .models import Comment


def check_workout_comment(check_owner: bool = True) -> Callable:
    def decorator_check_workout_comment(f: Callable) -> Callable:
        @wraps(f)
        def wrapper_check_workout_comment(
            *args: Any, **kwargs: Any
        ) -> Callable:
            auth_user = args[0]
            comment_short_id = kwargs["comment_short_id"]

            workout_comment_uuid = decode_short_id(comment_short_id)
            comment = Comment.query.filter_by(
                uuid=workout_comment_uuid
            ).first()
            if not comment:
                return NotFoundErrorResponse(
                    f"workout comment not found (id: {comment_short_id})"
                )

            if not can_view(comment, "text_visibility", auth_user):
                return NotFoundErrorResponse(
                    f"workout comment not found (id: {comment_short_id})"
                )

            if check_owner and (
                not auth_user or auth_user.id != comment.user.id
            ):
                return ForbiddenErrorResponse()
            return f(auth_user, comment)

        return wrapper_check_workout_comment

    return decorator_check_workout_comment

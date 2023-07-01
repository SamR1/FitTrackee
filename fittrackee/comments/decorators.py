from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional

from fittrackee.privacy_levels import can_view
from fittrackee.responses import ForbiddenErrorResponse, NotFoundErrorResponse
from fittrackee.utils import decode_short_id

from .models import Comment

if TYPE_CHECKING:
    from fittrackee.users.models import User


def check_workout_comment(check_owner: bool = True) -> Callable:
    def decorator_check_workout_comment(f: Callable) -> Callable:
        @wraps(f)
        def wrapper_check_workout_comment(
            *args: Any, **kwargs: Any
        ) -> Callable:
            auth_user: Optional['User'] = args[0]
            comment_short_id = kwargs["comment_short_id"]

            workout_comment_uuid = decode_short_id(comment_short_id)
            comment = Comment.query.filter(
                Comment.uuid == workout_comment_uuid,
                Comment.user_id.not_in(auth_user.get_blocked_user_ids())
                if auth_user
                else True,
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

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional

from fittrackee.responses import ForbiddenErrorResponse, NotFoundErrorResponse

from .exceptions import CommentForbiddenException
from .utils import get_comment

if TYPE_CHECKING:
    from fittrackee.users.models import User


def check_workout_comment(only_owner: bool = True) -> Callable:
    def decorator_check_workout_comment(f: Callable) -> Callable:
        @wraps(f)
        def wrapper_check_workout_comment(
            *args: Any, **kwargs: Any
        ) -> Callable:
            auth_user: Optional["User"] = args[0]
            comment_short_id: str = kwargs["comment_short_id"]

            try:
                comment = get_comment(comment_short_id, auth_user)
            except CommentForbiddenException:
                return NotFoundErrorResponse(
                    f"workout comment not found (id: {comment_short_id})"
                )
            if only_owner and (
                not auth_user or auth_user.id != comment.user.id
            ):
                return ForbiddenErrorResponse()
            return f(auth_user, comment)

        return wrapper_check_workout_comment

    return decorator_check_workout_comment

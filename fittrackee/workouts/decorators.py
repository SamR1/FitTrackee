from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional

from fittrackee.responses import (
    DataNotFoundErrorResponse,
    ForbiddenErrorResponse,
    NotFoundErrorResponse,
)

from .exceptions import WorkoutForbiddenException
from .utils.workouts import get_workout

if TYPE_CHECKING:
    from fittrackee.users.models import User


def check_workout(only_owner: bool = True, as_data: bool = True) -> Callable:
    def decorator_check_workout(f: Callable) -> Callable:
        @wraps(f)
        def wrapper_check_workout(*args: Any, **kwargs: Any) -> Callable:
            auth_user: Optional["User"] = args[0]
            workout_short_id = kwargs["workout_short_id"]
            try:
                workout = get_workout(workout_short_id, auth_user)
            except WorkoutForbiddenException:
                return (
                    DataNotFoundErrorResponse("workouts")
                    if as_data
                    else NotFoundErrorResponse(
                        f"workout not found (id: {workout_short_id})"
                    )
                )

            if only_owner and (
                not auth_user or auth_user.id != workout.user.id
            ):
                return ForbiddenErrorResponse()

            return f(auth_user, workout, **kwargs)

        return wrapper_check_workout

    return decorator_check_workout

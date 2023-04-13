from functools import wraps
from typing import Any, Callable

from fittrackee.privacy_levels import can_view
from fittrackee.responses import (
    DataNotFoundErrorResponse,
    ForbiddenErrorResponse,
)
from fittrackee.utils import decode_short_id
from fittrackee.workouts.models import Workout


def check_workout(check_owner: bool = True) -> Callable:
    def decorator_check_workout(f: Callable) -> Callable:
        @wraps(f)
        def wrapper_check_workout(*args: Any, **kwargs: Any) -> Callable:
            auth_user = args[0]
            workout_short_id = kwargs["workout_short_id"]
            workout_uuid = decode_short_id(workout_short_id)
            workout = Workout.query.filter_by(uuid=workout_uuid).first()
            if not workout:
                return DataNotFoundErrorResponse('workouts')

            if not can_view(workout, 'workout_visibility', auth_user):
                return DataNotFoundErrorResponse('workouts')

            if check_owner and (
                not auth_user or auth_user.id != workout.user.id
            ):
                return ForbiddenErrorResponse()

            return f(auth_user, workout, **kwargs)

        return wrapper_check_workout

    return decorator_check_workout

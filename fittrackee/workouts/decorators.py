from functools import wraps
from typing import Any, Callable

from fittrackee.responses import ForbiddenErrorResponse, NotFoundErrorResponse
from fittrackee.utils import decode_short_id
from fittrackee.workouts.models import Workout, WorkoutComment

from .utils.comment_visibility import can_view_workout_comment


def check_workout_comment(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Callable:
        auth_user = args[0]
        workout_short_id = kwargs["workout_short_id"]
        comment_short_id = kwargs["comment_short_id"]
        workout_uuid = decode_short_id(workout_short_id)
        workout = Workout.query.filter_by(uuid=workout_uuid).first()
        if not workout:
            return NotFoundErrorResponse(
                f"workout not found (id: {workout_short_id})"
            )

        workout_comment_uuid = decode_short_id(comment_short_id)
        workout_comment = WorkoutComment.query.filter_by(
            uuid=workout_comment_uuid
        ).first()
        if not workout_comment:
            return NotFoundErrorResponse(
                f"workout comment not found (id: {comment_short_id})"
            )

        if not can_view_workout_comment(workout_comment, auth_user):
            return NotFoundErrorResponse(
                f"workout comment not found (id: {comment_short_id})"
            )

        if auth_user.id != workout_comment.user.id:
            return ForbiddenErrorResponse()
        return f(auth_user, workout_comment)

    return decorated_function

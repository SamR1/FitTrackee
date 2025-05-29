from typing import TYPE_CHECKING

from ..exceptions import WorkoutExceedingValueException
from ..models import PSQL_INTEGER_LIMIT, WORKOUT_VALUES_LIMIT

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


class CheckWorkoutMixin:
    @staticmethod
    def _check_workout(workout: "Workout") -> None:
        if workout.distance and workout.distance > 999.9:
            raise WorkoutExceedingValueException(
                "'distance' exceeds max value (999.9)"
            )
        if workout.duration.total_seconds() > PSQL_INTEGER_LIMIT:
            raise WorkoutExceedingValueException(
                f"'duration' exceeds max value ({PSQL_INTEGER_LIMIT})"
            )

        for key in ["ascent", "descent", "max_speed"]:
            workout_value = getattr(workout, key)
            max_value = WORKOUT_VALUES_LIMIT[key]
            if workout_value and workout_value > max_value:
                raise WorkoutExceedingValueException(
                    f"'{key}' exceeds max value ({max_value})"
                )

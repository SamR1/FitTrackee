from fittrackee import db
from fittrackee.workouts.models import Workout

from ..services import WorkoutUpdateService
from .abstract_workouts_refresh_service import AbstractWorkoutsRefreshService


class WorkoutsWithoutFileRefreshService(AbstractWorkoutsRefreshService):
    """
    Allow to refresh workouts without file created before v1.1.0 in order
    to calculate pace values.

    All checks on parameters are made by the CLI command.
    """

    def refresh(self) -> int:
        filters = [
            Workout.original_file == None,  # noqa
            Workout.ave_pace == None,  # noqa
            Workout.best_pace == None,  # noqa
            # all workouts have speeds calculated
            Workout.ave_speed != None,  # noqa
            Workout.max_speed != None,  # noqa
        ]
        workouts_to_refresh, total = self._get_workouts(filters)
        if not total:
            return 0

        updated_workouts = 0
        for index, workout in enumerate(workouts_to_refresh, start=1):
            self._log_if_verbose(f"Refreshing workout {index}/{total}...")

            try:
                if self.new_sport_id:
                    workout.sport_id = self.new_sport_id
                    db.session.flush()
                    db.session.refresh(workout)
                service = WorkoutUpdateService(workout.user, workout, {})
                service.update()
                db.session.commit()
                updated_workouts += 1
            except Exception as e:
                self.logger.error(
                    (
                        f"Error when refreshing workout '{workout.short_id}' "
                        f"(user: {workout.user.username}): {e}"
                    )
                )
                continue

        if total:
            self._log_if_verbose(
                "\nRefresh done:\n"
                f"- updated workouts: {updated_workouts}\n"
                f"- errored workouts: {total - updated_workouts}"
            )

        return updated_workouts

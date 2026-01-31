from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import asc, desc

from fittrackee import db
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout

from ..services import WorkoutUpdateService

if TYPE_CHECKING:
    from logging import Logger


class WorkoutsWithoutFileRefreshService:
    """
    Allow to refresh workouts without file created before v1.1.0 in order
    to calculate pace values.

    All checks on parameters are made by the CLI command.
    """

    def __init__(
        self,
        logger: "Logger",
        per_page: Optional[int] = 10,
        page: Optional[int] = 1,
        order: Optional[str] = "asc",
        user: Optional[str] = None,
        sport_id: Optional[int] = None,
        new_sport_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        verbose: bool = False,
    ) -> None:
        self.per_page: Optional[int] = per_page
        self.page: Optional[int] = page
        self.order: Optional[str] = order
        self.username: Optional[str] = user
        self.sport_id: Optional[int] = sport_id
        self.new_sport_id: Optional[int] = new_sport_id
        self.date_from: Optional["datetime"] = date_from
        self.date_to: Optional["datetime"] = date_to
        self.logger: "Logger" = logger
        self.verbose: bool = verbose

    def _log_if_verbose(self, message: str) -> None:
        if not self.verbose:
            return
        self.logger.info(message)

    def refresh(self) -> int:
        workouts_to_refresh_query = Workout.query
        filters = [
            Workout.original_file == None,  # noqa
            Workout.ave_pace == None,  # noqa
            Workout.best_pace == None,  # noqa
            # all workouts have speeds calculated
            Workout.ave_speed != None,  # noqa
            Workout.max_speed != None,  # noqa
        ]
        if self.username:
            workouts_to_refresh_query = workouts_to_refresh_query.join(
                User, User.id == Workout.user_id
            )
            filters.extend([User.username == self.username])
        if self.sport_id:
            filters.extend([Workout.sport_id == self.sport_id])
        if self.date_from:
            filters.extend([Workout.workout_date >= self.date_from])
        if self.date_to:
            filters.extend([Workout.workout_date <= self.date_to])

        updated_workouts = 0
        workouts_to_refresh = (
            workouts_to_refresh_query.filter(*filters)
            .order_by(
                asc(Workout.workout_date)
                if self.order == "asc"
                else desc(Workout.workout_date)
            )
            .paginate(page=self.page, per_page=self.per_page, error_out=False)
            .items
        )

        total = len(workouts_to_refresh)
        if not total:
            self.logger.info("No workouts to refresh.")
            return 0

        self.logger.info(f"Number of workouts to refresh: {total}")
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

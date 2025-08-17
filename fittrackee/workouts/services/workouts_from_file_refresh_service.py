from logging import Logger, getLogger
from typing import TYPE_CHECKING, Optional

from sqlalchemy import asc, desc

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Workout

from ..exceptions import (
    WorkoutExceedingValueException,
    WorkoutException,
    WorkoutFileException,
    WorkoutRefreshException,
)
from ..utils.workouts import get_workout_datetime
from .mixins import WorkoutFileMixin
from .workout_from_file.services import WORKOUT_FROM_FILE_SERVICES

if TYPE_CHECKING:
    from datetime import datetime

    from fittrackee.workouts.models import Sport


appLog = getLogger("fittrackee_workout_refresh")


class WorkoutFromFileRefreshService(WorkoutFileMixin):
    """
    recalculate values ang regenerate geometry and points
    """

    def __init__(self, workout: "Workout", update_weather: bool = False):
        if not workout.original_file:
            raise WorkoutRefreshException(
                "error", "workout without original file"
            )

        self.original_file: str = workout.original_file
        self.workout: "Workout" = workout
        self.user: "User" = workout.user
        self.sport: "Sport" = workout.sport
        self.sport_preferences = UserSportPreference.query.filter_by(
            user_id=self.user.id, sport_id=self.sport.id
        ).first()
        self.stopped_speed_threshold = (
            self.sport.stopped_speed_threshold
            if self.sport_preferences is None
            else self.sport_preferences.stopped_speed_threshold
        )
        self.update_weather = update_weather

    def get_file_content(self) -> bytes:
        try:
            with open(get_absolute_file_path(self.original_file), "rb") as f:
                file_content = f.read()
                return file_content
        except Exception:
            raise WorkoutFileException(
                "error", "error when opening original file"
            ) from None

    def refresh(self) -> "Workout":
        file_extension = self._get_extension(self.original_file)
        if not self._is_valid_workout_file_extension(file_extension):
            raise WorkoutRefreshException("error", "invalid file extension")

        file_content = self.get_file_content()
        workout_service = WORKOUT_FROM_FILE_SERVICES[file_extension](
            auth_user=self.user,
            workout_file=file_content,  # type: ignore[arg-type]
            workout=self.workout,
            sport_id=self.sport.id,
            stopped_speed_threshold=self.stopped_speed_threshold,
            get_weather=self.update_weather,
        )

        # extract and calculate data from provided file
        # note: workout date is not updated
        try:
            workout_service.process_workout()
        except (WorkoutExceedingValueException, WorkoutFileException) as e:
            appLog.exception(f"workout exception: {e!s}")
            db.session.rollback()
            raise e
        except Exception as e:
            appLog.exception(f"exception: {e!s}")
            db.session.rollback()
            raise WorkoutException(
                "error", "error when processing workout"
            ) from e

        db.session.flush()

        # if original file is not a gpx, store the newly generated gpx file
        if file_extension != "gpx":
            gpx_file = (
                self.workout.gpx
                if self.workout.gpx
                else self.original_file.replace(file_extension, "gpx")
            )
            with open(get_absolute_file_path(gpx_file), "w") as f:
                f.write(workout_service.gpx.to_xml())

        db.session.commit()
        db.session.refresh(self.workout)
        return self.workout


class WorkoutsFromFileRefreshService:
    def __init__(
        self,
        per_page: Optional[int] = 10,
        page: Optional[int] = 1,
        order: Optional[str] = "asc",
        user: Optional[str] = None,
        extension: Optional[str] = None,
        sport_id: Optional[int] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        with_weather: bool = False,
        logger: Optional["Logger"] = None,
    ) -> None:
        self.per_page: Optional[int] = per_page
        self.page: Optional[int] = page
        self.order: Optional[str] = order
        self.username: Optional[str] = user
        self.extension: Optional[str] = extension
        self.sport_id: Optional[int] = sport_id
        self.from_: Optional["datetime"] = (
            get_workout_datetime(
                workout_date=from_,
                user_timezone=None,
                date_str_format="%Y-%m-%d",
            )[0]
            if from_
            else None
        )
        self.to: Optional["datetime"] = (
            get_workout_datetime(
                workout_date=to,
                user_timezone=None,
                date_str_format="%Y-%m-%d",
            )[0]
            if to
            else None
        )
        self.with_weather: bool = with_weather
        self.logger: Optional["Logger"] = logger

    def _log_message(self, message: str, *, is_error: bool = False) -> None:
        if not self.logger:
            return

        if is_error:
            self.logger.error(message)
            return

        self.logger.info(message)

    def refresh(self) -> int:
        workouts_to_refresh_query = Workout.query
        filters = [Workout.gpx != None]  # noqa
        if self.username:
            workouts_to_refresh_query = workouts_to_refresh_query.join(
                User, User.id == Workout.user_id
            )
            filters.extend([User.username == self.username])
        if self.extension:
            filters.extend([Workout.original_file.like(f"%{self.extension}")])
        if self.sport_id:
            filters.extend([Workout.sport_id == self.sport_id])
        if self.from_:
            filters.extend([Workout.workout_date >= self.from_])
        if self.to:
            filters.extend([Workout.workout_date <= self.to])

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
            self._log_message("No workouts to refresh.")
            return 0

        self._log_message(f"Number of workouts to refresh: {total}")
        for index, workout in enumerate(workouts_to_refresh, start=1):
            self._log_message(f"Refreshing workout {index}/{total}...")

            try:
                service = WorkoutFromFileRefreshService(
                    workout, update_weather=self.with_weather
                )
                service.refresh()
                updated_workouts += 1
            except Exception as e:
                self._log_message(
                    (
                        f"Error when refreshing workout '{workout.short_id}' "
                        f"(user: {workout.user.username}): {e}"
                    ),
                    is_error=True,
                )
                continue

        if total and self.logger:
            self.logger.info("Refresh done:")
            self.logger.info(f"- updated workouts: {updated_workouts}")
            self.logger.info(f"- errored workouts: {total - updated_workouts}")

        return updated_workouts

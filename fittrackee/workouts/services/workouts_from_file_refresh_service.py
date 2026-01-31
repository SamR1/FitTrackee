import zipfile
from datetime import datetime
from typing import IO, TYPE_CHECKING, Optional, Union

from sqlalchemy import asc, desc

from fittrackee import appLog, db
from fittrackee.files import get_absolute_file_path
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Workout, WorkoutSegment

from ..exceptions import (
    WorkoutExceedingValueException,
    WorkoutException,
    WorkoutFileException,
    WorkoutRefreshException,
)
from .mixins import WorkoutFileMixin
from .workout_from_file.services import WORKOUT_FROM_FILE_SERVICES

if TYPE_CHECKING:
    from logging import Logger

    from fittrackee.constants import ElevationDataSource
    from fittrackee.workouts.models import Sport


class WorkoutFromFileRefreshService(WorkoutFileMixin):
    """
    recalculate values ang regenerate geometry and points
    """

    def __init__(
        self,
        workout: "Workout",
        update_weather: bool = False,
        get_elevation_on_refresh: bool = True,
        change_elevation_source: Optional["ElevationDataSource"] = None,
        on_file_error: Optional[str] = None,
        logger: Optional["Logger"] = None,
    ):
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
        self.get_elevation_on_refresh = get_elevation_on_refresh
        self.change_elevation_source = change_elevation_source
        self.on_file_error = on_file_error
        self.logger = logger

    def get_file_content(self, file_extension: str) -> Union[bytes, IO[bytes]]:
        try:
            file_path = get_absolute_file_path(self.original_file)

            if file_extension == "kmz":
                with zipfile.ZipFile(file_path, "r") as kmz_ref:
                    return kmz_ref.open("doc.kml")

            with open(file_path, "rb") as f:
                file_content = f.read()
                return file_content
        except Exception:
            raise WorkoutFileException(
                "error", "error when opening original file"
            ) from None

    def _log_message(self, message: str) -> None:
        if self.logger:
            self.logger.info(message)

    def refresh(self) -> Optional["Workout"]:
        file_extension = self._get_extension(self.original_file)
        if not self._is_valid_workout_file_extension(file_extension):
            raise WorkoutRefreshException("error", "invalid file extension")

        try:
            file_content = self.get_file_content(file_extension)
        except WorkoutFileException as e:
            if self.on_file_error == "delete-workout":
                workout_id = self.workout.short_id
                user_name = self.workout.user.username
                db.session.delete(self.workout)
                db.session.commit()
                self._log_message(
                    f"No file found for workout '{workout_id}' (user: "
                    f"{user_name}), workout deleted."
                )
                return None
            if self.on_file_error == "remove-references":
                WorkoutSegment.query.filter_by(
                    workout_id=self.workout.id
                ).delete()
                self.workout.original_file = None
                self.workout.map_id = None
                self.workout.map = None
                db.session.commit()
                self._log_message(
                    f"No file found for workout '{self.workout.short_id}' "
                    f"(user: {self.workout.user.username}), segments deleted "
                    "and files references removed."
                )
                return self.workout
            raise e

        workout_service = WORKOUT_FROM_FILE_SERVICES[file_extension](
            auth_user=self.user,
            workout_file=file_content,  # type: ignore[arg-type]
            workout=self.workout,
            sport=self.sport,
            stopped_speed_threshold=self.stopped_speed_threshold,
            get_weather=self.update_weather,
            get_elevation_on_refresh=self.get_elevation_on_refresh,
            change_elevation_source=self.change_elevation_source,
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

        db.session.commit()
        db.session.refresh(self.workout)
        return self.workout


class WorkoutsFromFileRefreshService:
    """
    All checks on parameters are made by the CLI command.
    """

    def __init__(
        self,
        logger: "Logger",
        per_page: Optional[int] = 10,
        page: Optional[int] = 1,
        order: Optional[str] = "asc",
        user: Optional[str] = None,
        extension: Optional[str] = None,
        sport_id: Optional[int] = None,
        new_sport_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        with_weather: bool = False,
        with_elevation: bool = False,
        on_file_error: Optional[str] = None,
        verbose: bool = False,
    ) -> None:
        self.per_page: Optional[int] = per_page
        self.page: Optional[int] = page
        self.order: Optional[str] = order
        self.username: Optional[str] = user
        self.extension: Optional[str] = extension if extension else None
        self.sport_id: Optional[int] = sport_id
        self.new_sport_id: Optional[int] = new_sport_id
        self.date_from: Optional["datetime"] = date_from
        self.date_to: Optional["datetime"] = date_to
        self.with_weather: bool = with_weather
        self.with_elevation: bool = with_elevation
        self.on_file_error: Optional[str] = on_file_error
        self.logger: "Logger" = logger
        self.verbose: bool = verbose

    def _log_if_verbose(self, message: str) -> None:
        if not self.verbose:
            return
        self.logger.info(message)

    def refresh(self) -> int:
        workouts_to_refresh_query = Workout.query
        filters = [Workout.original_file != None]  # noqa
        if self.username:
            workouts_to_refresh_query = workouts_to_refresh_query.join(
                User, User.id == Workout.user_id
            )
            filters.extend([User.username == self.username])
        if self.extension:
            filters.extend([Workout.original_file.like(f"%{self.extension}")])
        if self.sport_id:
            filters.extend([Workout.sport_id == self.sport_id])
        if self.date_from:
            filters.extend([Workout.workout_date >= self.date_from])
        if self.date_to:
            filters.extend([Workout.workout_date <= self.date_to])

        updated_workouts = 0
        deleted_workouts = 0
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
                service = WorkoutFromFileRefreshService(
                    workout,
                    update_weather=self.with_weather,
                    get_elevation_on_refresh=self.with_elevation,
                    on_file_error=self.on_file_error,
                    logger=self.logger,
                )
                workout = service.refresh()
                if workout:
                    updated_workouts += 1
                else:
                    deleted_workouts += 1
            except Exception as e:
                self.logger.error(
                    (
                        f"Error when refreshing workout '{workout.short_id}' "
                        f"(user: {workout.user.username}): {e}"
                    )
                )
                continue

        if total:
            deleted_workouts_count = (
                f"- deleted workouts: {deleted_workouts}\n"
                if deleted_workouts
                else ""
            )
            errored_workouts = total - (updated_workouts + deleted_workouts)
            self._log_if_verbose(
                "\nRefresh done:\n"
                f"- updated workouts: {updated_workouts}\n"
                f"{deleted_workouts_count}"
                f"- errored workouts: {errored_workouts}"
            )

        return updated_workouts

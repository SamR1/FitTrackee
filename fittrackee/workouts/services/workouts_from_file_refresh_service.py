import zipfile
from datetime import datetime
from logging import Logger, getLogger
from typing import IO, TYPE_CHECKING, Optional, Union

from sqlalchemy import asc, desc, or_

from fittrackee import db
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

    def refresh(self) -> "Workout":
        file_extension = self._get_extension(self.original_file)
        if not self._is_valid_workout_file_extension(file_extension):
            raise WorkoutRefreshException("error", "invalid file extension")

        file_content = self.get_file_content(file_extension)
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
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        with_weather: bool = False,
        add_geometry: bool = False,
        verbose: bool = False,
    ) -> None:
        self.per_page: Optional[int] = per_page
        self.page: Optional[int] = page
        self.order: Optional[str] = order
        self.username: Optional[str] = user
        self.extension: Optional[str] = extension if extension else None
        self.sport_id: Optional[int] = sport_id
        self.date_from: Optional["datetime"] = date_from
        self.date_to: Optional["datetime"] = date_to
        self.with_weather: bool = with_weather
        self.add_geometry: bool = add_geometry
        self.logger: "Logger" = logger
        self.verbose: bool = verbose

    def _log_if_verbose(self, message: str) -> None:
        if not self.verbose:
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
        if self.date_from:
            filters.extend([Workout.workout_date >= self.date_from])
        if self.date_to:
            filters.extend([Workout.workout_date <= self.date_to])
        if self.add_geometry:
            workouts_to_refresh_query = workouts_to_refresh_query.join(
                WorkoutSegment
            )
            filters.extend(
                [
                    or_(
                        Workout.start_point_geom == None,  # noqa
                        WorkoutSegment.geom == None,  # noqa
                    )
                ]
            )

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
                service = WorkoutFromFileRefreshService(
                    workout, update_weather=self.with_weather
                )
                service.refresh()
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

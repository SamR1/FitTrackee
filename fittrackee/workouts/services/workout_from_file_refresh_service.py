from logging import getLogger
from typing import TYPE_CHECKING

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.users.models import UserSportPreference

from ..exceptions import (
    WorkoutExceedingValueException,
    WorkoutException,
    WorkoutFileException,
    WorkoutRefreshException,
)
from .mixins import WorkoutFileMixin
from .workout_from_file.services import WORKOUT_FROM_FILE_SERVICES

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


appLog = getLogger("fittrackee_workout_refresh")


class WorkoutFromFileRefreshService(WorkoutFileMixin):
    """
    recalculate values ang regenerate geometry and points
    """

    def __init__(self, workout: "Workout", update_weather: bool = False):
        if not workout.original_file:
            # for workouts uploaded before FitTrackee v0.10.0
            if workout.gpx:
                workout.original_file = workout.gpx
            else:
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

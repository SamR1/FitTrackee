from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import pytz

from fittrackee import db
from fittrackee.visibility_levels import VisibilityLevel

from ..constants import WORKOUT_DATE_FORMAT
from ..exceptions import WorkoutException
from ..models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    Workout,
)
from .base_workout_service import BaseWorkoutService
from .mixins import CheckWorkoutMixin

if TYPE_CHECKING:
    from fittrackee.users.models import User


@dataclass
class WorkoutData:
    distance: float
    duration: int
    sport_id: int
    workout_date: str
    ascent: Optional[float] = None
    descent: Optional[float] = None
    description: Optional[str] = None
    equipment_ids: Optional[List[str]] = None
    notes: Optional[str] = None
    title: Optional[str] = None
    workout_visibility: Optional[VisibilityLevel] = None


class WorkoutCreationService(CheckWorkoutMixin, BaseWorkoutService):
    """
    Workout creation without file
    """

    def __init__(self, auth_user: "User", workout_data: Dict):
        super().__init__(
            auth_user,
            workout_data["sport_id"],
            workout_data.get("equipment_ids"),
        )
        self.workout_data = WorkoutData(**workout_data)

    def get_workout_date(self) -> "datetime":
        try:
            workout_date = datetime.strptime(  # noqa: DTZ007
                self.workout_data.workout_date, WORKOUT_DATE_FORMAT
            )
        except ValueError as e:
            raise WorkoutException(
                "error", "invalid format for workout date"
            ) from e
        if self.auth_user.timezone:
            workout_date = pytz.timezone(self.auth_user.timezone).localize(
                workout_date
            )
            return workout_date.astimezone(pytz.utc)

        # in case no timezone is set for authenticated user
        return workout_date.replace(tzinfo=timezone.utc)

    def _get_elevation(self) -> Tuple[Optional[float], Optional[float]]:
        ascent = self.workout_data.ascent
        descent = self.workout_data.descent
        try:
            if (
                (ascent is None and descent is not None)
                or (ascent is not None and descent is None)
                or (ascent is not None and float(ascent) < 0)
                or (descent is not None and float(descent) < 0)
            ):
                raise WorkoutException("invalid", "invalid ascent or descent")
        except ValueError as e:
            raise WorkoutException(
                "invalid", "invalid ascent or descent"
            ) from e
        return ascent, descent

    def _get_workout_title(self, workout_date: datetime) -> str:
        return self._get_title(workout_date, self.workout_data.title)

    def process(self) -> Tuple[List["Workout"], Dict]:
        ascent, descent = self._get_elevation()
        duration = timedelta(seconds=self.workout_data.duration)
        distance = self.workout_data.distance

        workout_date = self.get_workout_date()
        new_workout = Workout(
            distance=distance,
            duration=duration,
            sport_id=self.workout_data.sport_id,
            user_id=self.auth_user.id,
            workout_date=workout_date,
        )
        db.session.add(new_workout)
        new_workout.moving = duration
        new_workout.pauses = timedelta(seconds=0)
        new_workout.ave_speed = (
            None
            if duration.seconds == 0
            else float(distance) / (duration.seconds / 3600)
        )
        new_workout.max_speed = new_workout.ave_speed
        new_workout.ascent = ascent
        new_workout.descent = descent

        self._check_workout(new_workout)
        new_workout.title = self._get_workout_title(workout_date)
        new_workout.description = (
            self.workout_data.description[:DESCRIPTION_MAX_CHARACTERS]
            if self.workout_data.description
            else None
        )
        new_workout.notes = (
            None
            if self.workout_data.notes is None
            else self.workout_data.notes[:NOTES_MAX_CHARACTERS]
        )

        equipments = self.get_equipments()
        if equipments is not None:
            new_workout.equipments = equipments

        new_workout.workout_visibility = (
            self.workout_data.workout_visibility
            if self.workout_data.workout_visibility
            else self.auth_user.workouts_visibility
        )

        db.session.flush()
        return [new_workout], {}

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict, List, Optional

import pytz

from fittrackee import db
from fittrackee.visibility_levels import VisibilityLevel

from ..constants import WORKOUT_DATE_FORMAT
from ..exceptions import WorkoutException
from ..models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Workout,
)
from .base_workout_service import BaseWorkoutService

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


class WorkoutCreationService(BaseWorkoutService):
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

    def process(self) -> List["Workout"]:
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

        duration = timedelta(seconds=self.workout_data.duration)
        distance = self.workout_data.distance

        new_workout = Workout(
            distance=distance,
            duration=duration,
            sport_id=self.workout_data.sport_id,
            user_id=self.auth_user.id,
            workout_date=self.get_workout_date(),
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

        if self.workout_data.title:
            new_workout.title = self.workout_data.title[:TITLE_MAX_CHARACTERS]
        else:
            workout_datetime = (
                new_workout.workout_date.astimezone(
                    pytz.timezone(self.auth_user.timezone)
                )
                if self.auth_user.timezone
                else new_workout.workout_date
            ).strftime("%Y-%m-%d %H:%M:%S")
            new_workout.title = f"{self.sport.label} - {workout_datetime}"
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
        return [new_workout]

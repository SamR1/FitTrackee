from datetime import timedelta
from typing import TYPE_CHECKING, Dict, List, TypedDict, Union

from fittrackee.equipments.utils import (
    SPORT_EQUIPMENT_TYPES,
    handle_pieces_of_equipment,
)
from fittrackee.visibility_levels import (
    VisibilityLevel,
    get_calculated_visibility,
)
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Sport,
)

from ..constants import WORKOUT_DATE_FORMAT
from ..exceptions import WorkoutException
from ..utils.convert import convert_speed_into_pace_duration
from ..utils.workouts import get_workout_datetime
from .mixins import CheckWorkoutMixin

if TYPE_CHECKING:
    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User

    from ..models import Workout


class WorkoutUpdateData(TypedDict, total=False):
    analysis_visibility: VisibilityLevel
    ascent: float
    calories: int
    descent: float
    description: str
    distance: float
    duration: int
    equipment_ids: List[str]
    map_visibility: VisibilityLevel
    notes: str
    sport_id: int
    title: str
    workout_date: str
    workout_visibility: VisibilityLevel


WITH_FILE_KEYS = {"analysis_visibility", "map_visibility"}
WITHOUT_FILE_KEYS = {
    "ascent",
    "calories",
    "descent",
    "distance",
    "duration",
    "workout_date",
}


class WorkoutUpdateService(CheckWorkoutMixin):
    def __init__(self, user: "User", workout: "Workout", workout_data: Dict):
        self.with_file = workout.original_file is not None
        self.workout_data = WorkoutUpdateData(**workout_data)
        self._check_workout_data()
        self.sport = self._get_sport()
        self.user = user
        self.workout = workout
        self.equipments_list = self._get_equipments_list()

    def _check_elevation_data(self) -> None:
        if self.with_file:
            return

        # for workout without gpx file, both elevation values must be
        # provided.
        try:
            if (
                (
                    "ascent" in self.workout_data
                    and "descent" not in self.workout_data
                )
                or (
                    "ascent" not in self.workout_data
                    and "descent" in self.workout_data
                )
            ) or (
                not (
                    self.workout_data.get("ascent") is None
                    and self.workout_data.get("descent") is None
                )
                and (
                    float(self.workout_data.get("ascent")) < 0  # type: ignore
                    or float(self.workout_data.get("descent")) < 0  # type: ignore
                )
            ):
                raise WorkoutException(
                    status="invalid",
                    message="invalid ascent or descent",
                )
        except (TypeError, ValueError) as e:
            raise WorkoutException(
                status="invalid",
                message="invalid ascent or descent",
            ) from e

    def _check_workout_data(self) -> None:
        invalid_keys = set(self.workout_data.keys()).intersection(
            WITHOUT_FILE_KEYS if self.with_file else WITH_FILE_KEYS
        )
        if invalid_keys:
            invalid_keys_str = ", ".join(
                sorted([f"'{key}'" for key in invalid_keys])
            )
            raise WorkoutException(
                status="invalid",
                message=(
                    f"invalid key{'' if len(invalid_keys) == 1 else 's'} "
                    f"({invalid_keys_str}) for workout with"
                    f"{'' if self.with_file else 'out'} file"
                ),
            )

        self._check_elevation_data()

    def _get_sport(self) -> Union["Sport", None]:
        sport_id = self.workout_data.get("sport_id")
        if sport_id:
            try:
                sport = Sport.query.filter_by(id=sport_id).one()
            except Exception as e:
                raise WorkoutException(
                    "invalid",
                    f"sport id {sport_id} not found",
                ) from e
            return sport
        return None

    def _get_equipments_list(self) -> Union[List["Equipment"], None]:
        if "equipment_ids" in self.workout_data:
            sport_id = (
                self.workout_data["sport_id"]
                if self.workout_data.get("sport_id")
                else self.workout.sport_id
            )
            return handle_pieces_of_equipment(
                self.workout_data["equipment_ids"],
                self.user,
                sport_id,
                self.workout.equipments,
            )
        elif self.sport:
            # remove equipment if invalid for new sport
            # Note: only one piece of equipment per type can be provided
            equipment_list = []
            for equipment in self.workout.equipments:
                if self.sport.label in SPORT_EQUIPMENT_TYPES.get(
                    equipment.equipment_type.label, []
                ):
                    equipment_list.append(equipment)
            return equipment_list
        return None

    def _update_workout_without_file(self) -> None:
        if "ascent" in self.workout_data:
            self.workout.ascent = self.workout_data["ascent"]

        if "descent" in self.workout_data:
            self.workout.descent = self.workout_data["descent"]

        if self.workout_data.get("workout_date"):
            self.workout.workout_date, _ = get_workout_datetime(
                workout_date=self.workout_data["workout_date"],
                date_str_format=WORKOUT_DATE_FORMAT,
                user_timezone=self.user.timezone,
            )

        update_speeds = False
        if self.workout_data.get("duration"):
            self.workout.duration = timedelta(
                seconds=self.workout_data["duration"]
            )
            self.workout.moving = self.workout.duration
            update_speeds = True

        if self.workout_data.get("distance"):
            self.workout.distance = self.workout_data["distance"]
            update_speeds = True

        if (
            update_speeds
            and self.workout.distance is not None
            and self.workout.duration is not None
        ):
            self.workout.ave_speed = (
                None
                if self.workout.duration.seconds == 0
                else float(self.workout.distance)
                / (self.workout.duration.seconds / 3600)
            )
            self.workout.max_speed = self.workout.ave_speed

        if (
            self.workout.ave_speed is not None
            and self.workout.max_speed is not None
            and (
                # to recalculated workouts created before v1.1.0
                self.workout.ave_pace is None
                or self.workout.best_pace is None
                # to recalculated pace when speeds have been updated
                or update_speeds
            )
        ):
            self.workout.ave_pace = convert_speed_into_pace_duration(
                float(self.workout.ave_speed)
            )
            self.workout.best_pace = convert_speed_into_pace_duration(
                float(self.workout.max_speed)
            )

        if "calories" in self.workout_data:
            self.workout.calories = self.workout_data["calories"] or None

        self._check_workout(self.workout)

    def update(self) -> None:
        if "sport_id" in self.workout_data:
            self.workout.sport_id = self.workout_data["sport_id"]
        if self.equipments_list is not None:
            self.workout.equipments = self.equipments_list

        if self.workout_data.get("description") is not None:
            self.workout.description = self.workout_data["description"][
                :DESCRIPTION_MAX_CHARACTERS
            ]
        if self.workout_data.get("notes") is not None:
            self.workout.notes = self.workout_data["notes"][
                :NOTES_MAX_CHARACTERS
            ]
        if self.workout_data.get("title") is not None:
            self.workout.title = self.workout_data["title"][
                :TITLE_MAX_CHARACTERS
            ]

        if "workout_visibility" in self.workout_data:
            self.workout.workout_visibility = self.workout_data[
                "workout_visibility"
            ]

        if self.with_file:
            if self.workout_data.get("analysis_visibility"):
                analysis_visibility = VisibilityLevel(
                    self.workout_data.get("analysis_visibility")
                )
                self.workout.analysis_visibility = get_calculated_visibility(
                    visibility=analysis_visibility,
                    parent_visibility=self.workout.workout_visibility,
                )
            if self.workout_data.get("map_visibility") is not None:
                map_visibility = VisibilityLevel(
                    self.workout_data.get("map_visibility")
                )
                self.workout.map_visibility = get_calculated_visibility(
                    visibility=map_visibility,
                    parent_visibility=self.workout.analysis_visibility,
                )
            return

        self._update_workout_without_file()

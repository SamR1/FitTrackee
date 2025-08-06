from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import pytz

from fittrackee.equipments.utils import handle_equipments
from fittrackee.users.models import UserSportPreference
from fittrackee.workouts.models import Sport

from ..exceptions import WorkoutException
from ..models import TITLE_MAX_CHARACTERS

if TYPE_CHECKING:
    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class BaseWorkoutService(ABC):
    def __init__(
        self,
        auth_user: "User",
        sport_id: Optional[int],
        equipment_ids: Union[List[str], None],
    ):
        if not sport_id:
            raise WorkoutException("invalid", "no sport id provided")
        try:
            self.sport = Sport.query.filter_by(id=sport_id).one()
        except Exception as e:
            raise WorkoutException(
                "invalid",
                f"Sport id: {sport_id} does not exist",
            ) from e
        self.auth_user = auth_user
        self.sport_preferences = UserSportPreference.query.filter_by(
            user_id=self.auth_user.id, sport_id=self.sport.id
        ).first()
        self.stopped_speed_threshold = (
            self.sport.stopped_speed_threshold
            if self.sport_preferences is None
            else self.sport_preferences.stopped_speed_threshold
        )
        self.equipment_ids = equipment_ids

    def get_equipments(self) -> Union[List["Equipment"], None]:
        if self.equipment_ids is None and self.sport_preferences:
            return [
                equipment
                for equipment in self.sport_preferences.default_equipments.all()  # noqa
                if equipment.is_active is True
            ]
        return handle_equipments(
            self.equipment_ids,
            self.auth_user,
            self.sport.id,
        )

    def _get_title(self, workout_date: datetime, title: Optional[str]) -> str:
        if title:
            return title[:TITLE_MAX_CHARACTERS]

        workout_datetime = (
            workout_date.astimezone(pytz.timezone(self.auth_user.timezone))
            if self.auth_user.timezone
            else workout_date
        ).strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.sport.label} - {workout_datetime}"

    @abstractmethod
    def process(self) -> Tuple[List["Workout"], Dict]:
        """
        returns:
        - list of workouts created successfully
        - a dict with errored workouts and flag indicating asynchronous
          processing
        """
        pass

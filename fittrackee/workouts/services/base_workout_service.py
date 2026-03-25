from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import pytz
from sqlalchemy import bindparam, update

from fittrackee import db
from fittrackee.equipments.utils import handle_pieces_of_equipment
from fittrackee.media.models import Media
from fittrackee.users.models import UserSportPreference
from fittrackee.utils import decode_short_id
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
        return handle_pieces_of_equipment(
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

    def update_media_attachments_if_provided(
        self, media_attachment_ids: Union[list[str], None], workout_id: int
    ) -> None:
        if not media_attachment_ids:
            return

        update_data = []
        for media_short_id in media_attachment_ids:
            update_data.append(
                {
                    "m_uuid": decode_short_id(media_short_id),
                    "workout_id": workout_id,
                }
            )

        if update_data:
            db.session.connection().execute(
                update(Media).where(
                    Media.uuid == bindparam("m_uuid"),
                    Media.user_id == self.auth_user.id,
                ),
                update_data,
            )

    @abstractmethod
    def process(self) -> Tuple[List["Workout"], Dict]:
        """
        returns:
        - list of workouts created successfully
        - a dict with errored workouts and flag indicating asynchronous
          processing
        """
        pass

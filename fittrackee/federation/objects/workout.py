from typing import TYPE_CHECKING, Dict

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.constants import WORKOUT_DATE_FORMAT

from ..enums import ActivityType
from ..exceptions import InvalidWorkoutException
from .base_object import BaseObject
from .exceptions import InvalidObjectException
from .templates.workout_note import WORKOUT_NOTE

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


class WorkoutObject(BaseObject):
    workout: "Workout"

    def __init__(self, workout: "Workout", activity_type: str) -> None:
        self._check_visibility(workout.workout_visibility)
        self.workout = workout
        if not self.workout.ap_id or not self.workout.remote_url:
            raise InvalidObjectException(
                "Invalid workout, missing 'ap_id' or 'remote_url'"
            )
        self.visibility = workout.workout_visibility
        self.type = ActivityType(activity_type)
        self.actor = self.workout.user.actor
        self.activity_id = self.workout.ap_id
        self.published = self._get_published_date(self.workout.creation_date)
        self.object_url = self.workout.remote_url
        self.activity_dict = self._init_activity_dict()

    @staticmethod
    def _check_visibility(visibility: VisibilityLevel) -> None:
        if visibility in [
            VisibilityLevel.PRIVATE,
            VisibilityLevel.FOLLOWERS,
        ]:
            raise InvalidVisibilityException(
                f"object visibility is: '{visibility.value}'"
            )

    def _get_note_content(self) -> str:
        # TODO:
        # handle translation and imperial units depending on user preferences
        return WORKOUT_NOTE.format(
            sport_label=self.workout.sport.label,
            workout_title=self.workout.title,
            workout_distance=self.workout.distance,
            workout_duration=self.workout.duration,
            workout_url=self.object_url,
        )

    def get_activity(self, is_note: bool = False) -> Dict:
        activity = self.activity_dict.copy()
        # for non-FitTrackee instances (like Mastodon)
        if is_note:
            activity["id"] = (
                f"{self.activity_id}/note/{self.type.value.lower()}"
            )
            activity["object"]["type"] = "Note"
            activity["object"]["content"] = self._get_note_content()
        # for FitTrackee instances
        else:
            activity["object"] = {
                **activity["object"],
                **{
                    "type": "Workout",
                    "ave_speed": self.workout.ave_speed,
                    "distance": self.workout.distance,
                    "duration": str(self.workout.duration),
                    "max_speed": self.workout.max_speed,
                    "moving": str(self.workout.moving),
                    "sport_id": self.workout.sport_id,
                    "title": self.workout.title,
                    "workout_date": self.workout.workout_date.strftime(
                        WORKOUT_DATE_FORMAT
                    ),
                },
            }
        if self.type == ActivityType.UPDATE:
            activity["object"] = {
                **activity["object"],
                "updated": self._get_modification_date(self.workout),
            }
        return activity


def convert_duration_string_to_seconds(duration_str: str) -> int:
    try:
        hour, minutes, seconds = duration_str.split(":")
        duration = int(hour) * 3600 + int(minutes) * 60 + int(seconds)
    except Exception as e:
        raise InvalidWorkoutException(
            f"duration or moving format is invalid ({e})"
        ) from e
    return duration


def convert_workout_activity(workout_data: Dict) -> Dict:
    return {
        **workout_data,
        "duration": convert_duration_string_to_seconds(
            workout_data["duration"]
        ),
        "moving": convert_duration_string_to_seconds(workout_data["moving"]),
    }

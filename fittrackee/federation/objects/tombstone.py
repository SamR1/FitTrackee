from typing import TYPE_CHECKING, Dict, Union

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel

from ..constants import AP_CTX, PUBLIC_STREAM
from ..enums import ActivityType
from .base_object import BaseObject

if TYPE_CHECKING:
    from fittrackee.comments.models import WorkoutComment
    from fittrackee.workouts.models import Workout


class TombstoneObject(BaseObject):
    # WIP
    object_to_delete: Union['Workout', 'WorkoutComment']

    def __init__(
        self, object_to_delete: Union['Workout', 'WorkoutComment']
    ) -> None:
        self.object_to_delete = object_to_delete
        self.object_to_delete_type = object_to_delete.__class__.__name__
        self.type = ActivityType.DELETE
        self.actor = self.object_to_delete.user.actor
        self.visibility = self._get_object_visibility()
        # TODO: handle comments with mentions
        if self.visibility in [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]:
            raise InvalidVisibilityException(
                f"object visibility is: '{self.visibility.value}'"
            )

    def _get_object_visibility(self) -> PrivacyLevel:
        if self.object_to_delete_type == 'WorkoutComment':
            return self.object_to_delete.text_visibility
        return self.object_to_delete.workout_visibility

    def get_activity(self) -> Dict:
        delete_activity = {
            "@context": AP_CTX,
            "id": f'{self.object_to_delete.ap_id}/delete',
            "type": "Delete",
            "actor": self.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": self.object_to_delete.ap_id,
            },
        }
        # TODO: handle comments with mentions
        if self.visibility == PrivacyLevel.PUBLIC:
            delete_activity['to'] = [PUBLIC_STREAM]
            delete_activity['cc'] = [self.actor.followers_url]
        else:
            delete_activity['to'] = [self.actor.followers_url]
            delete_activity['cc'] = []
        return delete_activity

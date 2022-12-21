from typing import TYPE_CHECKING, Dict

from fittrackee.privacy_levels import PrivacyLevel

from ..constants import AP_CTX, PUBLIC_STREAM
from ..enums import ActivityType
from .base_object import BaseObject
from .exceptions import InvalidVisibilityException

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


class TombstoneObject(BaseObject):
    # WIP
    # for now only tombstone for workouts is implemented
    object_to_delete: 'Workout'

    def __init__(self, object_to_delete: 'Workout') -> None:
        self.object_to_delete = object_to_delete
        self.type = ActivityType.DELETE
        self.actor = self.object_to_delete.user.actor
        self.visibility = self._get_object_visibility()
        if self.visibility in [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]:
            raise InvalidVisibilityException(
                f"object visibility is: '{self.visibility.value}'"
            )

    def _get_object_id(self) -> str:
        return (
            f'{self.actor.activitypub_id}/workouts/'
            f'{self.object_to_delete.short_id}'
        )

    def _get_object_visibility(self) -> PrivacyLevel:
        return self.object_to_delete.workout_visibility

    def get_activity(self) -> Dict:
        object_id = self._get_object_id()
        delete_activity = {
            "@context": AP_CTX,
            "id": f'{object_id}/delete',
            "type": "Delete",
            "actor": self.actor.activitypub_id,
            "object": {
                "type": "Tombstone",
                "id": object_id,
            },
        }
        if self.visibility == PrivacyLevel.PUBLIC:
            delete_activity['to'] = [PUBLIC_STREAM]
            delete_activity['cc'] = [self.actor.followers_url]
        else:
            delete_activity['to'] = [self.actor.followers_url]
            delete_activity['cc'] = []
        return delete_activity

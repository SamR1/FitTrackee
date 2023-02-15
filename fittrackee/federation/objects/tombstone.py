from typing import TYPE_CHECKING, Dict, Union

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel

from ..constants import AP_CTX, PUBLIC_STREAM
from ..enums import ActivityType
from .base_object import BaseObject

if TYPE_CHECKING:
    from fittrackee.comments.models import Comment
    from fittrackee.workouts.models import Workout


class TombstoneObject(BaseObject):
    # WIP
    object_to_delete: Union['Workout', 'Comment']

    def __init__(self, object_to_delete: Union['Workout', 'Comment']) -> None:
        self.object_to_delete = object_to_delete
        self.object_to_delete_type = object_to_delete.__class__.__name__
        self.type = ActivityType.DELETE
        self.actor = self.object_to_delete.user.actor
        self.visibility = self._get_object_visibility()
        if self.visibility in [
            PrivacyLevel.PRIVATE,
            PrivacyLevel.FOLLOWERS,
        ] and (
            self.object_to_delete_type != 'Comment'
            or (
                self.object_to_delete_type == 'Comment'
                and not self.object_to_delete.has_remote_mentions
            )
        ):
            raise InvalidVisibilityException(
                f"object visibility is: '{self.visibility.value}'"
            )

    def _get_object_visibility(self) -> PrivacyLevel:
        if self.object_to_delete_type == 'Comment':
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
        elif self.visibility in [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]:
            # for comments w/ mentions
            _, mentioned_users = self.object_to_delete.handle_mentions()
            mentions = [
                user.actor.activitypub_id
                for user in mentioned_users["local"].union(
                    mentioned_users["remote"]
                )
            ]
            delete_activity['to'] = mentions
            delete_activity['cc'] = []
        else:
            delete_activity['to'] = [self.actor.followers_url]
            delete_activity['cc'] = []
        return delete_activity

from typing import TYPE_CHECKING, Dict, Tuple

from ..constants import AP_CTX
from ..enums import ActivityType
from .base_object import ActivityObject

if TYPE_CHECKING:
    from ..models import Actor


class FollowRequestObject(ActivityObject):
    from_actor: 'Actor'
    to_actor: 'Actor'

    def __init__(
        self,
        from_actor: 'Actor',
        to_actor: 'Actor',
        activity_type: ActivityType,
    ):
        self.from_actor = from_actor
        self.to_actor = to_actor
        self.type = activity_type
        self.actor, self.id = self._get_actor_and_id()

    def _get_actor_and_id(self) -> Tuple['Actor', str]:
        if self.type in [ActivityType.FOLLOW, ActivityType.UNDO]:
            return self.from_actor, (
                f'{self.from_actor.activitypub_id}#'
                f'{"follow" if self.type ==ActivityType.FOLLOW else "undoe"}s/'
                f'{self.to_actor.fullname}'
            )
        return self.to_actor, (
            f'{self.to_actor.activitypub_id}#'
            f'{"accept" if self.type == ActivityType.ACCEPT else "reject"}s/'
            f'follow/{self.from_actor.fullname}'
        )

    def _get_follow_activity(self) -> Dict:
        return {
            'id': (
                f'{self.from_actor.activitypub_id}#follows/'
                f'{self.to_actor.fullname}'
            ),
            'type': ActivityType.FOLLOW.value,
            'actor': self.from_actor.activitypub_id,
            'object': self.to_actor.activitypub_id,
        }

    def serialize(self) -> Dict:
        if self.type == ActivityType.FOLLOW:
            activity = self._get_follow_activity()
        else:
            activity = {
                'id': self.id,
                'type': self.type.value,
                'actor': self.actor.activitypub_id,
                'object': self._get_follow_activity(),
            }
        activity['@context'] = AP_CTX
        return activity

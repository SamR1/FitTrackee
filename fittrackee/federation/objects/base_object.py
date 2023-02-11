from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Union

from fittrackee.privacy_levels import PrivacyLevel

from ..constants import AP_CTX, DATE_FORMAT, PUBLIC_STREAM

if TYPE_CHECKING:
    from fittrackee.comments.models import WorkoutComment
    from fittrackee.workouts.models import Workout

    from ..enums import ActivityType
    from ..models import Actor


class BaseObject(ABC):
    id: str
    type: 'ActivityType'
    actor: 'Actor'
    visibility: 'PrivacyLevel'
    activity_id: str
    object_url: str
    published: str

    def _init_activity_dict(self) -> Dict:
        activity = {
            '@context': AP_CTX,
            'type': self.type.value,
            'id': f"{self.activity_id}/{self.type.value.lower()}",
            'actor': self.actor.activitypub_id,
            'published': self.published,
            'object': {
                'id': self.activity_id,
                'published': self.published,
                'url': self.object_url,
                'attributedTo': self.actor.activitypub_id,
            },
        }
        if self.visibility == PrivacyLevel.PUBLIC:
            activity['to'] = [PUBLIC_STREAM]
            activity['cc'] = [self.actor.followers_url]
            activity['object']['to'] = [PUBLIC_STREAM]
            activity['object']['cc'] = [self.actor.followers_url]
        else:
            activity['to'] = [self.actor.followers_url]
            activity['cc'] = [self.actor.activitypub_id]
            activity['object']['to'] = [self.actor.followers_url]
            activity['object']['cc'] = [self.actor.activitypub_id]
        return activity

    @staticmethod
    def _get_published_date(object_date: datetime) -> str:
        return object_date.strftime(DATE_FORMAT)

    @staticmethod
    def _get_modification_date(
        activity_object: Union['Workout', 'WorkoutComment']
    ) -> str:
        return activity_object.modification_date.strftime(DATE_FORMAT)

    @abstractmethod
    def get_activity(self) -> Dict:
        pass

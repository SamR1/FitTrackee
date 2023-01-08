from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Dict

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel

from ..constants import AP_CTX, DATE_FORMAT, PUBLIC_STREAM

if TYPE_CHECKING:
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

    @staticmethod
    def _check_visibility(visibility: PrivacyLevel) -> None:
        if visibility in [
            PrivacyLevel.PRIVATE,
            PrivacyLevel.FOLLOWERS,
        ]:
            raise InvalidVisibilityException(
                f"object visibility is: '{visibility}'"
            )

    def _init_activity_dict(self) -> Dict:
        activity = {
            '@context': AP_CTX,
            'type': self.type.value,
            'id': f"{self.activity_id}/activity",
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
            activity['cc'] = []
            activity['object']['to'] = [self.actor.followers_url]
            activity['object']['cc'] = []
        return activity

    @staticmethod
    def _get_published_date(object_date: datetime) -> str:
        return object_date.strftime(DATE_FORMAT)

    @abstractmethod
    def get_activity(self) -> Dict:
        pass

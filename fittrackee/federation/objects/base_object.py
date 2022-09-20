from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..enums import ActivityType
    from ..models import Actor


class BaseObject(ABC):
    id: str
    type: 'ActivityType'
    actor: 'Actor'

    @abstractmethod
    def serialize(self) -> Dict:
        pass

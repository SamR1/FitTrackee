from typing import Dict, List, Union

from ..constants import AP_CTX
from ..enums import ActivityType
from .base_object import BaseObject


class LikeObject(BaseObject):
    def __init__(
        self,
        target_object_ap_id: str,
        like_id: int,
        actor_ap_id: str,
        is_undo: bool = False,
    ) -> None:
        self.is_undo = is_undo
        self.target_object_ap_id = target_object_ap_id
        self.like_id = like_id
        self.actor_ap_id = actor_ap_id

    def get_activity(self) -> Dict:
        activity_id = f"{self.actor_ap_id}#likes/{self.like_id}"
        like_object: Dict[str, Union[str, List]] = {
            "id": activity_id,
            "type": ActivityType.LIKE.value,
            "actor": self.actor_ap_id,
            "object": self.target_object_ap_id,
        }
        if self.is_undo:
            return {
                "@context": AP_CTX,
                "id": f"{activity_id}/undo",
                "type": ActivityType.UNDO.value,
                "actor": self.actor_ap_id,
                "object": like_object,
            }
        like_object["@context"] = AP_CTX
        return like_object

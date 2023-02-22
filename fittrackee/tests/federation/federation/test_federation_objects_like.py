from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.objects.like import LikeObject
from fittrackee.users.models import User

from ...comments.utils import CommentMixin


class TestLikeObject(CommentMixin):
    def test_it_generates_like_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        target_object_ap_id = self.random_string()
        like_id = self.random_int()
        like_object = LikeObject(
            target_object_ap_id=target_object_ap_id,
            like_id=like_id,
            actor_ap_id=user_1.actor.activitypub_id,
        )

        serialized_like = like_object.get_activity()

        assert serialized_like == {
            "@context": AP_CTX,
            "id": f"{user_1.actor.activitypub_id}#likes/{like_id}",
            "type": "Like",
            "actor": user_1.actor.activitypub_id,
            "object": target_object_ap_id,
        }

    def test_it_generates_undo_activity(
        self,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        target_object_ap_id = self.random_string()
        like_id = self.random_int()
        like_object = LikeObject(
            target_object_ap_id=target_object_ap_id,
            like_id=like_id,
            actor_ap_id=user_1.actor.activitypub_id,
            is_undo=True,
        )

        serialized_like = like_object.get_activity()

        assert serialized_like == {
            "@context": AP_CTX,
            "id": f"{user_1.actor.activitypub_id}#likes/{like_id}/undo",
            "type": "Undo",
            "actor": user_1.actor.activitypub_id,
            "object": {
                "id": f"{user_1.actor.activitypub_id}#likes/{like_id}",
                "type": "Like",
                "actor": user_1.actor.activitypub_id,
                "object": target_object_ap_id,
            },
        }

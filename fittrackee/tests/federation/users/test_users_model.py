from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.models import Actor
from fittrackee.users.models import FollowRequest


class TestFollowRequestModelWithFederation:
    def test_follow_request_model(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_1_to_user_2_with_federation: FollowRequest,
    ) -> None:
        assert '<FollowRequest from user \'1\' to user \'2\'>' == str(
            follow_request_from_user_1_to_user_2_with_federation
        )

        serialized_follow_request = (
            follow_request_from_user_1_to_user_2_with_federation.serialize()
        )
        assert serialized_follow_request['from_user'] == actor_1.serialize()
        assert serialized_follow_request['to_user'] == actor_2.serialize()

    def test_it_returns_activity_object_when_federation_is_enabled(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        actor_2: Actor,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        activity_object = follow_request_from_user_1_to_user_2.get_activity()

        assert app_with_federation.config['UI_URL'] in activity_object['id']
        expected_object_subset = {
            '@context': AP_CTX,
            'type': 'Follow',
            'actor': actor_1.activitypub_id,
            'object': actor_2.activitypub_id,
        }
        assert {**activity_object, **expected_object_subset} == activity_object

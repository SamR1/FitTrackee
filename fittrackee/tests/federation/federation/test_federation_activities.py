from typing import Dict, Optional, Union

import pytest
from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.exceptions import (
    ActorNotFoundException,
    UnsupportedActivityException,
)
from fittrackee.federation.models import Actor
from fittrackee.federation.utils import get_activity_instance
from fittrackee.users.exceptions import FollowRequestAlreadyRejectedError
from fittrackee.users.models import FollowRequest

from ...utils import RandomActor, random_string

SUPPORTED_ACTIVITIES = [(f'{a.value} activity', a.value) for a in ActivityType]


class TestActivityInstantiation:
    @pytest.mark.parametrize(
        'input_description,input_type', SUPPORTED_ACTIVITIES
    )
    def test_it_instantiates_activity_from_activity_dict(
        self, input_description: str, input_type: str
    ) -> None:
        activity = get_activity_instance({'type': input_type})
        activity_instance = activity(activity_dict={})
        assert activity_instance.__class__.__name__ == f'{input_type}Activity'

    def test_it_raises_exception_if_activity_type_is_invalid(self) -> None:
        with pytest.raises(UnsupportedActivityException):
            get_activity_instance({'type': random_string()})


class TestFollowActivity:
    @staticmethod
    def generate_follow_activity(
        actor_id: Optional[str] = None,
        object_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        if object_actor is None:
            object_actor = RandomActor()
        return {
            '@context': AP_CTX,
            'id': f'{actor_id}#follow/{object_actor.fullname}',
            'type': ActivityType.FOLLOW.value,
            'actor': actor_id if actor_id else RandomActor().activitypub_id,
            'object': object_actor.activitypub_id,
        }

    def test_it_raises_error_if_target_actor_does_not_exists(
        self, app_with_federation: Flask, remote_actor: Actor
    ) -> None:
        follow_activity = self.generate_follow_activity(
            actor_id=remote_actor.activitypub_id
        )

        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='followed actor not found for Follow Activity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_remote_actor_does_not_exists(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        follow_activity = self.generate_follow_activity(object_actor=actor_1)

        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='followed actor not found for Follow Activity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        actor_1.user.refuses_follow_request_from(remote_actor.user)
        follow_activity = self.generate_follow_activity(
            actor_id=remote_actor.activitypub_id, object_actor=actor_1
        )

        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        with pytest.raises(FollowRequestAlreadyRejectedError):
            activity.process_activity()

    def test_it_creates_follow_request(
        self, app_with_federation: Flask, actor_1: Actor, remote_actor: Actor
    ) -> None:
        follow_activity = self.generate_follow_activity(
            actor_id=remote_actor.activitypub_id, object_actor=actor_1
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )
        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_actor.user.id,
            followed_user_id=actor_1.user.id,
        ).first()
        assert follow_request is not None

    def test_it_does_raise_error_if_pending_follow_request_already_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        follow_activity = self.generate_follow_activity(
            actor_id=remote_actor.activitypub_id, object_actor=actor_1
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )
        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_actor.user.id,
            followed_user_id=actor_1.user.id,
        ).first()
        assert follow_request.updated_at is None

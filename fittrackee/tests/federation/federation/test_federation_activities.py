from typing import Dict, Optional, Union
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.exceptions import (
    ActorNotFoundException,
    UnsupportedActivityException,
)
from fittrackee.federation.models import Actor
from fittrackee.federation.tasks.activity import get_activity_instance
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)
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


class FollowRequestActivitiesTestCase:
    @staticmethod
    def generate_follow_activity(
        follower_actor_id: Optional[str] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        if follower_actor_id is None:
            follower_actor_id = RandomActor().activitypub_id
        if followed_actor is None:
            followed_actor = RandomActor()
        return {
            '@context': AP_CTX,
            'id': f'{follower_actor_id}#follows/{followed_actor.fullname}',
            'type': ActivityType.FOLLOW.value,
            'actor': follower_actor_id,
            'object': followed_actor.activitypub_id,
        }

    @staticmethod
    def generate_accept_or_reject_activity(
        activity_type: ActivityType,
        follower_actor: Optional[Union[Actor, RandomActor]] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        if follower_actor is None:
            follower_actor = RandomActor()
        if followed_actor is None:
            followed_actor = RandomActor()
        return {
            '@context': AP_CTX,
            'id': (
                f'{followed_actor.activitypub_id}#'
                f'{activity_type.value.lower()}s/follow/'
                f'{follower_actor.fullname}'
            ),
            'type': activity_type.value,
            'actor': followed_actor.activitypub_id,
            'object': {
                'id': (
                    f'{follower_actor.activitypub_id}#follows/'
                    f'{followed_actor.fullname}'
                ),
                'type': ActivityType.FOLLOW.value,
                'actor': follower_actor.activitypub_id,
                'object': followed_actor.activitypub_id,
            },
        }

    def generate_accept_activity(
        self,
        follower_actor: Optional[Union[Actor, RandomActor]] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        return self.generate_accept_or_reject_activity(
            ActivityType.ACCEPT, follower_actor, followed_actor
        )

    def generate_reject_activity(
        self,
        follower_actor: Optional[Union[Actor, RandomActor]] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        return self.generate_accept_or_reject_activity(
            ActivityType.REJECT, follower_actor, followed_actor
        )


class TestFollowActivity(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_followed_actor_does_not_exist(
        self, app_with_federation: Flask, remote_actor: Actor
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=remote_actor.activitypub_id
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='object actor not found for FollowActivity',
        ):
            activity.process_activity()

    def test_it_creates_actor_if_remote_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        random_actor: RandomActor,
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=random_actor.activitypub_id,
            followed_actor=actor_1,
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )
        with patch(
            'fittrackee.federation.utils_user.get_remote_actor'
        ) as get_remote_user_mock:
            get_remote_user_mock.return_value = (
                random_actor.get_remote_user_object()
            )
            activity.process_activity()

        remote_actor = Actor.query.filter_by(
            activitypub_id=follow_activity['actor']
        )
        assert remote_actor is not None

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        actor_1.user.rejects_follow_request_from(remote_actor.user)
        follow_activity = self.generate_follow_activity(
            follower_actor_id=remote_actor.activitypub_id,
            followed_actor=actor_1,
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
            follower_actor_id=remote_actor.activitypub_id,
            followed_actor=actor_1,
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

    def test_it_does_not_raise_error_if_pending_follow_request_already_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=remote_actor.activitypub_id,
            followed_actor=actor_1,
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


class TestAcceptActivity(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_follower_actor_does_not_exist(
        self, app_with_federation: Flask, remote_actor: Actor
    ) -> None:
        accept_activity = self.generate_accept_activity(
            followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='object actor not found for AcceptActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_followed_actor_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        accept_activity = self.generate_accept_activity(follower_actor=actor_1)
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for AcceptActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
    ) -> None:
        accept_activity = self.generate_accept_activity(
            follower_actor=actor_1, followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(NotExistingFollowRequestError):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_1_to_remote_actor: FollowRequest,
    ) -> None:
        remote_actor.user.rejects_follow_request_from(actor_1.user)
        accept_activity = self.generate_accept_activity(
            follower_actor=actor_1, followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(FollowRequestAlreadyProcessedError):
            activity.process_activity()

    def test_it_accepts_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_1_to_remote_actor: FollowRequest,
    ) -> None:
        accept_activity = self.generate_accept_activity(
            follower_actor=actor_1, followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=actor_1.user.id,
            followed_user_id=remote_actor.user.id,
        ).first()

        assert follow_request.is_approved
        assert follow_request.updated_at is not None


class TestRejectActivity(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_follower_actor_does_not_exist(
        self, app_with_federation: Flask, remote_actor: Actor
    ) -> None:
        accept_activity = self.generate_reject_activity(
            followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='object actor not found for RejectActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_followed_actor_does_not_exist(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        accept_activity = self.generate_reject_activity(follower_actor=actor_1)
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for RejectActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
    ) -> None:
        accept_activity = self.generate_reject_activity(
            follower_actor=actor_1, followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(NotExistingFollowRequestError):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_1_to_remote_actor: FollowRequest,
    ) -> None:
        remote_actor.user.rejects_follow_request_from(actor_1.user)
        accept_activity = self.generate_reject_activity(
            follower_actor=actor_1, followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(FollowRequestAlreadyProcessedError):
            activity.process_activity()

    def test_it_rejects_follow_request(
        self,
        app_with_federation: Flask,
        actor_1: Actor,
        remote_actor: Actor,
        follow_request_from_user_1_to_remote_actor: FollowRequest,
    ) -> None:
        accept_activity = self.generate_reject_activity(
            follower_actor=actor_1, followed_actor=remote_actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=actor_1.user.id,
            followed_user_id=remote_actor.user.id,
        ).first()

        assert follow_request.is_approved is False
        assert follow_request.updated_at is not None

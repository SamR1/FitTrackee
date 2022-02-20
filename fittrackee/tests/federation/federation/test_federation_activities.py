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
from fittrackee.federation.tasks.activity import get_activity_instance
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)
from fittrackee.users.models import FollowRequest, User

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
    def generate_activity_from_type(
        activity_type: ActivityType,
        follower_actor: Optional[Union[Actor, RandomActor]] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        if follower_actor is None:
            follower_actor = RandomActor()
        if followed_actor is None:
            followed_actor = RandomActor()
        activity_action = (
            f'{activity_type.value.lower()}e'
            if activity_type == ActivityType.UNDO
            else activity_type.value.lower()
        )
        return {
            '@context': AP_CTX,
            'id': (
                f'{followed_actor.activitypub_id}#'
                f'{activity_action}s/follow/'
                f'{follower_actor.fullname}'
            ),
            'type': activity_type.value,
            'actor': follower_actor.activitypub_id
            if activity_type == ActivityType.UNDO
            else followed_actor.activitypub_id,
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
        return self.generate_activity_from_type(
            ActivityType.ACCEPT, follower_actor, followed_actor
        )

    def generate_reject_activity(
        self,
        follower_actor: Optional[Union[Actor, RandomActor]] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        return self.generate_activity_from_type(
            ActivityType.REJECT, follower_actor, followed_actor
        )

    def generate_undo_activity(
        self,
        follower_actor: Optional[Union[Actor, RandomActor]] = None,
        followed_actor: Optional[Union[Actor, RandomActor]] = None,
    ) -> Dict:
        return self.generate_activity_from_type(
            ActivityType.UNDO, follower_actor, followed_actor
        )


class TestFollowActivity(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_followed_actor_does_not_exist(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=user_1.actor.activitypub_id
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='object actor not found for FollowActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        user_1.rejects_follow_request_from(remote_user)
        follow_activity = self.generate_follow_activity(
            follower_actor_id=remote_user.actor.activitypub_id,
            followed_actor=user_1.actor,
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        with pytest.raises(FollowRequestAlreadyRejectedError):
            activity.process_activity()

    def test_it_creates_follow_request(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=remote_user.actor.activitypub_id,
            followed_actor=user_1.actor,
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_user.id,
            followed_user_id=user_1.id,
        ).first()
        assert follow_request is not None

    def test_it_does_not_raise_error_if_pending_follow_request_already_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_remote_user_to_user_1: FollowRequest,
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=remote_user.actor.activitypub_id,
            followed_actor=remote_user.actor,
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=remote_user.id,
            followed_user_id=user_1.id,
        ).first()
        assert follow_request.updated_at is None


class TestAcceptActivity(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_follower_actor_does_not_exist(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        accept_activity = self.generate_accept_activity(
            followed_actor=remote_user.actor
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
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        accept_activity = self.generate_accept_activity(
            follower_actor=user_1.actor
        )
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
        user_1: User,
        remote_user: User,
    ) -> None:
        accept_activity = self.generate_accept_activity(
            follower_actor=user_1.actor, followed_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(NotExistingFollowRequestError):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.rejects_follow_request_from(user_1)
        accept_activity = self.generate_accept_activity(
            followed_actor=remote_user.actor, follower_actor=user_1.actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(FollowRequestAlreadyProcessedError):
            activity.process_activity()

    def test_it_accepts_follow_request(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        accept_activity = self.generate_accept_activity(
            follower_actor=user_1.actor, followed_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user_1.id,
            followed_user_id=remote_user.id,
        ).first()

        assert follow_request.is_approved
        assert follow_request.updated_at is not None


class TestRejectActivity(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_follower_actor_does_not_exist(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        accept_activity = self.generate_reject_activity(
            followed_actor=remote_user.actor
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
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        accept_activity = self.generate_reject_activity(
            follower_actor=user_1.actor
        )
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
        user_1: User,
        remote_user: User,
    ) -> None:
        accept_activity = self.generate_reject_activity(
            follower_actor=user_1.actor, followed_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(NotExistingFollowRequestError):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_already_rejected(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.rejects_follow_request_from(user_1)
        accept_activity = self.generate_accept_activity(
            followed_actor=remote_user.actor, follower_actor=user_1.actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        with pytest.raises(FollowRequestAlreadyProcessedError):
            activity.process_activity()

    def test_it_rejects_follow_request(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        accept_activity = self.generate_reject_activity(
            follower_actor=user_1.actor, followed_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': accept_activity['type']})(
            activity_dict=accept_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user_1.id,
            followed_user_id=remote_user.id,
        ).first()

        assert follow_request.is_approved is False
        assert follow_request.updated_at is not None


class TestUndoActivityForFollowRequest(FollowRequestActivitiesTestCase):
    def test_it_raises_error_if_follower_actor_does_not_exist(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        undo_activity = self.generate_undo_activity(
            followed_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': undo_activity['type']})(
            activity_dict=undo_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for UndoActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_followed_actor_does_not_exist(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        undo_activity = self.generate_undo_activity(
            follower_actor=user_1.actor
        )
        activity = get_activity_instance({'type': undo_activity['type']})(
            activity_dict=undo_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for UndoActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_follow_request_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
    ) -> None:
        undo_activity = self.generate_undo_activity(
            follower_actor=user_1.actor,
            followed_actor=remote_user.actor,
        )
        activity = get_activity_instance({'type': undo_activity['type']})(
            activity_dict=undo_activity
        )

        with pytest.raises(NotExistingFollowRequestError):
            activity.process_activity()

    def test_it_undoes_follow_request_regardless_its_status(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        undo_activity = self.generate_undo_activity(
            follower_actor=user_1.actor, followed_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': undo_activity['type']})(
            activity_dict=undo_activity
        )

        activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            follower_user_id=user_1.id,
            followed_user_id=remote_user.id,
        ).first()

        assert follow_request is None

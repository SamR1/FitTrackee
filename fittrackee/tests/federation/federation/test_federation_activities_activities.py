from datetime import datetime, timedelta
from typing import Dict, Optional, Union
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee.comments.models import WorkoutComment
from fittrackee.federation.constants import AP_CTX, DATE_FORMAT, PUBLIC_STREAM
from fittrackee.federation.enums import ActivityType
from fittrackee.federation.exceptions import (
    ActivityException,
    ActorNotFoundException,
    ObjectNotFoundException,
    UnsupportedActivityException,
)
from fittrackee.federation.models import Actor
from fittrackee.federation.objects.workout import (
    convert_duration_string_to_seconds,
)
from fittrackee.federation.tasks.activity import get_activity_instance
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.workouts.utils import WorkoutCommentMixin
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.constants import WORKOUT_DATE_FORMAT
from fittrackee.workouts.exceptions import SportNotFoundException
from fittrackee.workouts.models import Sport, Workout

from ...mixins import RandomMixin
from ...utils import RandomActor

SUPPORTED_ACTIVITIES = [(f'{a.value} activity', a.value) for a in ActivityType]


class TestActivityInstantiation(RandomMixin):
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
            get_activity_instance({'type': self.random_string()})


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

    def test_it_creates_follow_request_with_existing_remote_user(
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

    def test_it_creates_remote_user_and_follow_request(
        self,
        app_with_federation: Flask,
        user_1: User,
        random_actor: RandomActor,
    ) -> None:
        follow_activity = self.generate_follow_activity(
            follower_actor_id=random_actor.activitypub_id,
            followed_actor=user_1.actor,
        )
        activity = get_activity_instance({'type': follow_activity['type']})(
            activity_dict=follow_activity
        )
        with patch(
            'fittrackee.federation.utils.user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ), patch(
            'fittrackee.federation.utils.user.store_or_delete_user_picture'
        ), patch(
            'fittrackee.federation.utils.user.update_remote_actor_stats'
        ):
            activity.process_activity()

        follow_request = FollowRequest.query.filter_by(
            followed_user_id=user_1.id,
        ).first()
        assert follow_request.from_user.actor.fullname == random_actor.fullname

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


class WorkoutActivitiesTestCase(RandomMixin):
    def generate_random_object(
        self,
        remote_actor: Union[RandomActor, Actor],
        sport_id: int,
        activity_type: str,
        visibility: PrivacyLevel,
    ) -> Dict:
        remote_domain = (
            remote_actor.domain
            if isinstance(remote_actor, RandomActor)
            else f'https://{remote_actor.domain.name}'
        )
        workout_date = datetime.utcnow().strftime(WORKOUT_DATE_FORMAT)
        workout_distance = self.random_int(max_value=999)
        workout_short_id = self.random_short_id()
        workout_url = f'{remote_domain}/workouts/{workout_short_id}'
        published = datetime.utcnow().strftime(DATE_FORMAT)
        activity: Dict = {
            "@context": AP_CTX,
            "id": (
                f"{remote_actor.activitypub_id}/workouts/"
                f"{workout_short_id}/activity"
            ),
            "type": activity_type,
            "actor": remote_actor.activitypub_id,
            "published": published,
            "to": [],
            "cc": [],
            "object": {
                "id": (
                    f"{remote_actor.activitypub_id}/workouts/"
                    f"{workout_short_id}"
                ),
                "type": "Workout",
                "published": published,
                "url": workout_url,
                "attributedTo": remote_actor.activitypub_id,
                "to": [],
                "cc": [],
                "ave_speed": workout_distance,
                "distance": workout_distance,
                "duration": "01:00:00",
                "max_speed": workout_distance,
                "moving": "01:00:00",
                "sport_id": sport_id,
                "title": self.random_string(),
                "workout_date": workout_date,
            },
        }
        if visibility == PrivacyLevel.PUBLIC:
            activity['to'] = [PUBLIC_STREAM]
            activity['cc'] = [remote_actor.followers_url]
            activity['object']['to'] = [PUBLIC_STREAM]
            activity['object']['cc'] = [remote_actor.followers_url]
        else:
            activity['to'] = [remote_actor.followers_url]
            activity['cc'] = []
            activity['object']['to'] = [remote_actor.followers_url]
            activity['object']['cc'] = []
        return activity

    def generate_workout_create_activity(
        self,
        remote_actor: Union[RandomActor, Actor],
        sport_id: int,
        visibility: PrivacyLevel = PrivacyLevel.PUBLIC,
    ) -> Dict:
        return self.generate_random_object(
            remote_actor, sport_id, 'Create', visibility
        )

    def generate_workout_update_activity(
        self,
        remote_actor: Union[RandomActor, Actor, None] = None,
        sport_id: Optional[int] = None,
        workout: Optional[Workout] = None,
        updates: Optional[Dict] = None,
    ) -> Dict:
        activity = {}
        if not updates:
            updates = {}
        if workout:
            actor: Actor = workout.user.actor
            remote_domain = f'https://{workout.user.actor.domain.name}'
            published = datetime.utcnow().strftime(DATE_FORMAT)
            activity = {
                "@context": AP_CTX,
                "id": (
                    f"{actor.activitypub_id}/workouts/"
                    f"{workout.short_id}/activity"
                ),
                "type": "Update",
                "actor": actor.activitypub_id,
                "published": published,
                "to": [],
                "cc": [],
                "object": {
                    "id": workout.ap_id,
                    "type": "Workout",
                    "published": published,
                    "url": f"{remote_domain}/workouts/{workout.short_id}",
                    "attributedTo": actor.activitypub_id,
                    "to": [],
                    "cc": [],
                    "ave_speed": workout.ave_speed,
                    "distance": workout.distance,
                    "duration": str(workout.duration),
                    "max_speed": workout.max_speed,
                    "moving": str(workout.moving),
                    "sport_id": workout.sport_id,
                    "title": workout.title,
                    "workout_date": datetime.utcnow().strftime(
                        WORKOUT_DATE_FORMAT
                    ),
                },
            }
            if "workout_visibility" in updates:
                workout_visibility = updates["workout_visibility"]
                del updates["workout_visibility"]
            else:
                workout_visibility = workout.workout_visibility
            if workout_visibility == PrivacyLevel.PUBLIC:
                activity['to'] = [PUBLIC_STREAM]
                activity['cc'] = [actor.followers_url]
                activity['object']['to'] = [PUBLIC_STREAM]
                activity['object']['cc'] = [actor.followers_url]
            else:
                activity['to'] = [actor.followers_url]
                activity['cc'] = []
                activity['object']['to'] = [actor.followers_url]
                activity['object']['cc'] = []
        elif remote_actor and remote_actor and sport_id:
            activity = self.generate_random_object(
                remote_actor, sport_id, 'Update', PrivacyLevel.PUBLIC
            )
        activity["object"] = {**activity["object"], **updates}
        return activity

    def generate_workout_delete_activity(
        self,
        remote_actor: Union[RandomActor, Actor],
        remote_workout: Optional[Workout] = None,
    ) -> Dict:
        remote_domain = (
            remote_actor.domain
            if isinstance(remote_actor, RandomActor)
            else f'https://{remote_actor.domain.name}'
        )
        workout_short_id = (
            remote_workout.ap_id
            if remote_workout
            else f'{remote_domain}/workouts/{self.random_short_id()}'
        )
        return {
            '@context': AP_CTX,
            'id': f'{workout_short_id}/delete',
            'type': 'Delete',
            'actor': remote_actor.activitypub_id,
            'to': [PUBLIC_STREAM],
            'cc': [],
            'object': {
                'id': workout_short_id,
                'type': 'Tombstone',
            },
        }


class TestCreateActivityForWorkout(WorkoutActivitiesTestCase):
    def test_it_raises_error_if_workout_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
        sport_1_cycling: Sport,
    ) -> None:

        workout_activity = self.generate_workout_create_activity(
            remote_actor=random_actor, sport_id=sport_1_cycling.id
        )
        activity = get_activity_instance({'type': workout_activity['type']})(
            activity_dict=workout_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for CreateActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_sport_does_not_exist(
        self,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        workout_activity = self.generate_workout_create_activity(
            remote_actor=remote_user.actor, sport_id=self.random_int()
        )
        activity = get_activity_instance({'type': workout_activity['type']})(
            activity_dict=workout_activity
        )

        with pytest.raises(SportNotFoundException):
            activity.process_activity()

    def test_it_creates_remote_workout_without_gpx_with_public_visibility(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_activity = self.generate_workout_create_activity(
            remote_actor=remote_user.actor,
            sport_id=sport_1_cycling.id,
            visibility=PrivacyLevel.PUBLIC,
        )
        activity = get_activity_instance({'type': workout_activity['type']})(
            activity_dict=workout_activity
        )

        activity.process_activity()

        remote_workout = Workout.query.filter_by(
            user_id=remote_user.id, sport_id=sport_1_cycling.id
        ).first()
        assert remote_workout.ap_id == workout_activity['object']['id']
        assert remote_workout.remote_url == workout_activity['object']['url']
        assert (
            remote_workout.distance == workout_activity['object']['distance']
        )
        assert remote_workout.workout_visibility == PrivacyLevel.PUBLIC

    def test_it_creates_remote_workout_without_gpx_with_followers_visibility(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_activity = self.generate_workout_create_activity(
            remote_actor=remote_user.actor,
            sport_id=sport_1_cycling.id,
            visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )
        activity = get_activity_instance({'type': workout_activity['type']})(
            activity_dict=workout_activity
        )

        activity.process_activity()

        remote_workout = Workout.query.filter_by(
            user_id=remote_user.id, sport_id=sport_1_cycling.id
        ).first()
        assert (
            remote_workout.workout_visibility
            == PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

    def test_serializer_returns_remote_url(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_activity = self.generate_workout_create_activity(
            remote_actor=remote_user.actor,
            sport_id=sport_1_cycling.id,
            visibility=PrivacyLevel.PUBLIC,
        )
        activity = get_activity_instance({'type': workout_activity['type']})(
            activity_dict=workout_activity
        )
        activity.process_activity()

        remote_workout = Workout.query.filter_by(
            user_id=remote_user.id, sport_id=sport_1_cycling.id
        ).first()
        assert (
            remote_workout.serialize(remote_user)['remote_url']
            == remote_workout.remote_url
        )

    def test_it_does_not_create_records_for_remote_workout(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
    ) -> None:
        workout_activity = self.generate_workout_create_activity(
            remote_actor=remote_user.actor, sport_id=sport_1_cycling.id
        )
        activity = get_activity_instance({'type': workout_activity['type']})(
            activity_dict=workout_activity
        )
        activity.process_activity()

        remote_workout = Workout.query.filter_by(
            user_id=remote_user.id, sport_id=sport_1_cycling.id
        ).first()
        assert remote_workout.records == []


class TestDeleteActivityForWorkout(WorkoutActivitiesTestCase):
    def test_it_raises_error_if_remote_workout_does_not_exist(
        self,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        delete_activity = self.generate_workout_delete_activity(
            remote_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )

        with pytest.raises(
            ObjectNotFoundException,
            match='object not found for DeleteActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_workout_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        random_actor: Actor,
    ) -> None:
        delete_activity = self.generate_workout_delete_activity(
            remote_actor=random_actor
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for DeleteActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_when_activity_actor_is_not_workout_actor(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        remote_user_2: User,
    ) -> None:
        delete_activity = self.generate_workout_delete_activity(
            remote_actor=remote_user_2.actor,
            remote_workout=remote_cycling_workout,
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )

        with pytest.raises(
            ActivityException,
            match=(
                'DeleteActivity: activity actor does not match workout actor.'
            ),
        ):
            activity.process_activity()
        assert (
            Workout.query.filter_by(id=remote_cycling_workout.id).first()
            is not None
        )

    def test_it_deletes_remote_workout(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        delete_activity = self.generate_workout_delete_activity(
            remote_actor=remote_user.actor,
            remote_workout=remote_cycling_workout,
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )
        workout_id = remote_cycling_workout.id

        activity.process_activity()

        assert Workout.query.filter_by(id=workout_id).first() is None


class TestUpdateActivityForWorkout(WorkoutActivitiesTestCase):
    def test_it_raises_error_if_remote_workout_does_not_exist(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
    ) -> None:
        update_activity = self.generate_workout_update_activity(
            remote_actor=remote_user.actor, sport_id=sport_1_cycling.id
        )
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )
        with pytest.raises(
            ObjectNotFoundException,
            match="workout not found for UpdateActivity",
        ):

            activity.process_activity()

    def test_it_raises_error_if_workout_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        random_actor: Actor,
        sport_1_cycling: Sport,
    ) -> None:
        update_activity = self.generate_workout_update_activity(
            remote_actor=random_actor, sport_id=sport_1_cycling.id
        )
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )
        with pytest.raises(
            ActorNotFoundException,
            match="actor not found for UpdateActivity",
        ):

            activity.process_activity()

    def test_it_raises_error_when_activity_actor_is_not_workout_actor(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        remote_user_2: User,
    ) -> None:
        update_activity = self.generate_workout_update_activity(
            workout=remote_cycling_workout,
            updates={'title': self.random_string()},
        )
        update_activity = {
            **update_activity,
            'actor': remote_user_2.actor.activitypub_id,
        }
        activity = get_activity_instance({'type': update_activity['type']})(
            activity_dict=update_activity
        )
        serialize_workout = remote_cycling_workout.serialize(remote_user)
        with pytest.raises(
            ActivityException,
            match=(
                "UpdateActivity: activity actor does not match workout actor."
            ),
        ):

            activity.process_activity()

        workout = Workout.query.filter_by(id=remote_cycling_workout.id).first()
        assert workout.serialize(remote_user) == serialize_workout

    @pytest.mark.parametrize(
        "input_key, input_new_value",
        [
            ("ave_speed", 9.0),
            ("distance", 12.0),
            ("max_speed", 13.0),
            ("sport_id", 2),
            ("title", "new_title"),
            ("workout_visibility", PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_updates_remote_workout(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        remote_cycling_workout: Workout,
        input_key: str,
        input_new_value: Union[str, int, float, PrivacyLevel],
    ) -> None:
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        update_activity = self.generate_workout_update_activity(
            workout=remote_cycling_workout,
            updates={input_key: input_new_value},
        )
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )

        activity.process_activity()

        workout = Workout.query.filter_by(id=remote_cycling_workout.id).first()
        assert workout.__getattribute__(input_key) == input_new_value

    @pytest.mark.parametrize(
        "input_key, input_new_value",
        [
            ("duration", "00:50:00"),
            ("moving", "01:20:10"),
        ],
    )
    def test_it_updates_remote_workout_durations(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        remote_cycling_workout: Workout,
        input_key: str,
        input_new_value: str,
    ) -> None:
        update_activity = self.generate_workout_update_activity(
            workout=remote_cycling_workout,
            updates={input_key: input_new_value},
        )
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )

        activity.process_activity()

        workout = Workout.query.filter_by(id=remote_cycling_workout.id).first()
        assert workout.__getattribute__(input_key) == timedelta(
            seconds=convert_duration_string_to_seconds(input_new_value)
        )

    def test_it_updates_remote_workout_date(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        new_workout_date = "2022-01-04 08:16"
        update_activity = self.generate_workout_update_activity(
            workout=remote_cycling_workout,
            updates={"workout_date": new_workout_date},
        )
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )

        activity.process_activity()

        workout = Workout.query.filter_by(id=remote_cycling_workout.id).first()
        assert workout.workout_date == datetime.strptime(
            new_workout_date, WORKOUT_DATE_FORMAT
        )

    def test_it_updates_remote_workout_modification_date(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        update_activity = self.generate_workout_update_activity(
            workout=remote_cycling_workout,
            updates={"title": self.random_string()},
        )
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )

        activity.process_activity()

        workout = Workout.query.filter_by(id=remote_cycling_workout.id).first()
        assert workout.modification_date is not None

    def test_it_raises_exception_when_activity_is_invalid(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        update_activity = self.generate_workout_update_activity(
            workout=remote_cycling_workout,
        )
        del update_activity["object"]["title"]
        activity = get_activity_instance({"type": update_activity["type"]})(
            activity_dict=update_activity
        )
        with pytest.raises(
            ActivityException,
            match=(
                "UpdateActivity: invalid Workout activity"
                " \\(KeyError: 'title'\\)."
            ),
        ):

            activity.process_activity()


class WorkoutCommentActivitiesTestCase(RandomMixin):
    def generate_random_object(
        self,
        activity_type: str,
        remote_actor: Union[RandomActor, Actor],
        workout: Optional[Workout] = None,
        visibility: Optional[PrivacyLevel] = PrivacyLevel.PUBLIC,
    ) -> Dict:
        remote_domain = (
            remote_actor.domain
            if isinstance(remote_actor, RandomActor)
            else f'https://{remote_actor.domain.name}'
        )
        workout_short_id = (
            workout.short_id if workout else self.random_short_id()
        )
        if not workout:
            workout_api_id = (
                f'{remote_domain}/federation/users/'
                f'{remote_actor.name}/'
                f'workouts/{workout_short_id}'
            )
        else:
            workout_api_id = workout.ap_id

        comment_short_id = self.random_short_id()
        comment_ap_id = (
            f"{remote_actor.activitypub_id}/workouts/{workout_short_id}"
            f"/comments/{comment_short_id}"
        )
        comment_url = (
            f'{remote_domain}/workouts/{workout_short_id}'
            f'/comment/{comment_short_id}'
        )
        published = datetime.utcnow().strftime(DATE_FORMAT)
        activity: Dict = {
            "@context": AP_CTX,
            "id": f"{comment_ap_id}/activity",
            "type": activity_type,
            "actor": remote_actor.activitypub_id,
            "published": published,
            "to": [remote_actor.followers_url],
            "cc": [],
            "object": {
                "id": comment_ap_id,
                "type": "Note",
                "published": published,
                "url": comment_url,
                "attributedTo": remote_actor.activitypub_id,
                "inReplyTo": workout_api_id,
                "content": self.random_string(),
                "to": [remote_actor.followers_url],
                "cc": [],
            },
        }
        if visibility == PrivacyLevel.PUBLIC:
            activity['to'] = [PUBLIC_STREAM]
            activity['cc'] = [remote_actor.followers_url]
            activity['object']['to'] = [PUBLIC_STREAM]
            activity['object']['cc'] = [remote_actor.followers_url]
        elif visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE:
            activity['to'] = [remote_actor.followers_url]
            activity['cc'] = []
            activity['object']['to'] = [remote_actor.followers_url]
            activity['object']['cc'] = []
        elif workout:
            activity['to'] = [workout.user.actor.followers_url]
            activity['cc'] = []
            activity['object']['to'] = [workout.user.actor.followers_url]
            activity['object']['cc'] = []
        return activity

    def generate_workout_comment_create_activity(
        self,
        remote_actor: Union[RandomActor, Actor],
        workout: Optional[Workout] = None,
        visibility: Optional[PrivacyLevel] = PrivacyLevel.PUBLIC,
    ) -> Dict:
        return self.generate_random_object(
            "Create", remote_actor, workout, visibility
        )

    def generate_workout_comment_update_activity(
        self,
        remote_actor: Union[RandomActor, Actor],
        workout: Optional[Workout] = None,
        visibility: Optional[PrivacyLevel] = PrivacyLevel.PUBLIC,
    ) -> Dict:
        return self.generate_random_object(
            "Update", remote_actor, workout, visibility
        )

    def generate_workout_comment_delete_activity(
        self,
        remote_actor: Union[RandomActor, Actor],
        remote_comment: Optional[WorkoutComment] = None,
    ) -> Dict:
        remote_domain = (
            remote_actor.domain
            if isinstance(remote_actor, RandomActor)
            else f'https://{remote_actor.domain.name}'
        )
        comment_ap_id = (
            remote_comment.ap_id
            if remote_comment
            else (
                f'{remote_domain}/workouts/{self.random_short_id()}'
                f'/comments/{self.random_short_id()}/'
            )
        )
        return {
            '@context': AP_CTX,
            'id': f'{comment_ap_id}/delete',
            'type': 'Delete',
            'actor': remote_actor.activitypub_id,
            'to': [PUBLIC_STREAM],
            'cc': [],
            'object': {
                'id': comment_ap_id,
                'type': 'Tombstone',
            },
        }


class TestCreateActivityForWorkoutComment(WorkoutCommentActivitiesTestCase):
    def test_it_raises_error_if_comment_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        random_actor: RandomActor,
    ) -> None:

        comment_activity = self.generate_workout_comment_create_activity(
            remote_actor=random_actor
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for CreateActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_if_comment_workout_does_not_exist(
        self,
        app_with_federation: Flask,
        remote_user: User,
    ) -> None:
        comment_activity = self.generate_workout_comment_create_activity(
            remote_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        with pytest.raises(
            ObjectNotFoundException,
            match='workout not found for CreateActivity',
        ):
            activity.process_activity()

    @pytest.mark.parametrize(
        'input_visibility',
        [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_creates_remote_workout_comment_with_expected_visibility(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_visibility
        workout_cycling_user_1.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts/'
            f'{workout_cycling_user_1.short_id}'
        )
        comment_activity = self.generate_workout_comment_create_activity(
            remote_actor=remote_user.actor,
            workout=workout_cycling_user_1,
            visibility=input_visibility,
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        activity.process_activity()

        remote_comment = WorkoutComment.query.filter_by(
            user_id=remote_user.id
        ).first()
        assert remote_comment.ap_id == comment_activity['object']['id']
        assert remote_comment.remote_url == comment_activity['object']['url']
        assert remote_comment.text == comment_activity['object']['content']
        assert remote_comment.text_visibility == input_visibility
        assert remote_comment.reply_to is None


class TestCreateActivityForWorkoutCommentReply(
    WorkoutCommentMixin, WorkoutCommentActivitiesTestCase
):
    def test_it_raises_error_if_parent_comment_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts/'
            f'{workout_cycling_user_1.short_id}'
        )
        comment_activity = self.generate_workout_comment_create_activity(
            remote_actor=remote_user.actor, workout=workout_cycling_user_1
        )
        comment_activity["object"]["inReplyTo"] = (
            comment_activity["object"]["inReplyTo"]
            + f"/comments/{self.random_short_id()}"
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        with pytest.raises(
            ObjectNotFoundException,
            match='parent workout_comment not found for CreateActivity',
        ):
            activity.process_activity()

    @pytest.mark.parametrize(
        'input_visibility',
        [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_creates_remote_workout_comment_with_expected_visibility(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts/'
            f'{workout_cycling_user_1.short_id}'
        )
        parent_comment = self.create_comment(
            user_1, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )
        parent_comment.ap_id = (
            f'{user_1.actor.activitypub_id}/workouts/'
            f'{workout_cycling_user_1.short_id}/comments/'
            + parent_comment.short_id
        )
        comment_activity = self.generate_workout_comment_create_activity(
            remote_actor=remote_user.actor,
            workout=workout_cycling_user_1,
            visibility=input_visibility,
        )
        comment_activity["object"]["inReplyTo"] = parent_comment.ap_id
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        activity.process_activity()

        remote_comment = WorkoutComment.query.filter_by(
            user_id=remote_user.id
        ).first()
        assert remote_comment.ap_id == comment_activity['object']['id']
        assert remote_comment.remote_url == comment_activity['object']['url']
        assert remote_comment.text == comment_activity['object']['content']
        assert remote_comment.text_visibility == input_visibility
        assert remote_comment.reply_to == parent_comment.id


class TestUpdateActivityForWorkoutComment(
    WorkoutCommentMixin, WorkoutCommentActivitiesTestCase
):
    def test_it_raises_error_if_remote_workout_comment_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment_activity = self.generate_workout_comment_update_activity(
            remote_user.actor
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )
        with pytest.raises(
            ObjectNotFoundException,
            match="comment not found for UpdateActivity",
        ):

            activity.process_activity()

    def test_it_raises_error_if_workout_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        random_actor: Actor,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment_activity = self.generate_workout_comment_update_activity(
            random_actor
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )
        with pytest.raises(
            ActorNotFoundException,
            match="actor not found for UpdateActivity",
        ):

            activity.process_activity()

    def test_it_raises_error_when_activity_actor_is_not_comment_actor(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
        remote_user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        remote_comment.modification_date = datetime.utcnow()
        comment_activity = {
            **remote_comment.get_activity("Update"),
            'actor': remote_user_2.actor.activitypub_id,
        }
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        with pytest.raises(
            ActivityException,
            match=(
                "UpdateActivity: activity actor does not match Note actor."
            ),
        ):

            activity.process_activity()

        assert remote_comment.user == remote_user

    def test_it_updates_remote_workout_comment_text(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        remote_comment.modification_date = datetime.utcnow()
        comment_activity = remote_comment.get_activity("Update")
        comment_activity["object"]["content"] = self.random_string()
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        activity.process_activity()

        assert remote_comment.text == comment_activity["object"]["content"]

    def test_it_updates_remote_workout_modification_date(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        remote_comment.modification_date = datetime.utcnow()
        comment_activity = remote_comment.get_activity("Update")
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        activity.process_activity()

        assert remote_comment.modification_date is not None

    def test_it_updates_remote_workout_visibility(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        remote_comment.modification_date = datetime.utcnow()
        comment_activity = remote_comment.get_activity("Update")
        comment_activity["to"] = [remote_user.actor.followers_url]
        comment_activity["cc"] = [remote_user.actor.activitypub_id]
        comment_activity["object"]["to"] = [remote_user.actor.followers_url]
        comment_activity["object"]["cc"] = [remote_user.actor.activitypub_id]
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )

        activity.process_activity()

        assert (
            remote_comment.text_visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
        )

    def test_it_raises_exception_when_activity_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        remote_comment.modification_date = datetime.utcnow()
        comment_activity = remote_comment.get_activity("Update")
        del comment_activity["object"]["content"]
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )
        with pytest.raises(
            ActivityException,
            match=(
                "UpdateActivity: invalid Note activity"
                " \\(KeyError: 'content'\\)."
            ),
        ):

            activity.process_activity()


class TestDeleteActivityForWorkoutComment(
    WorkoutCommentMixin, WorkoutCommentActivitiesTestCase
):
    def test_it_raises_error_if_remote_workout_does_not_exist(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment_activity = self.generate_workout_comment_delete_activity(
            remote_actor=remote_user.actor
        )
        activity = get_activity_instance({'type': comment_activity['type']})(
            activity_dict=comment_activity
        )
        with pytest.raises(
            ObjectNotFoundException,
            match="object not found for DeleteActivity",
        ):

            activity.process_activity()

    def test_it_raises_error_if_workout_actor_does_not_exist(
        self,
        app_with_federation: Flask,
        random_actor: Actor,
    ) -> None:
        delete_activity = self.generate_workout_comment_delete_activity(
            remote_actor=random_actor
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )

        with pytest.raises(
            ActorNotFoundException,
            match='actor not found for DeleteActivity',
        ):
            activity.process_activity()

    def test_it_raises_error_when_activity_actor_is_not_comment_actor(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        remote_user_2: User,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            remote_cycling_workout,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        delete_activity = self.generate_workout_comment_delete_activity(
            remote_actor=remote_user_2.actor,
            remote_comment=remote_comment,
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )

        with pytest.raises(
            ActivityException,
            match=(
                'DeleteActivity: activity actor does not match workout actor.'
            ),
        ):
            activity.process_activity()
        assert (
            WorkoutComment.query.filter_by(id=remote_comment.id).first()
            is not None
        )

    def test_it_deletes_remote_workout(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            remote_cycling_workout,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        delete_activity = self.generate_workout_comment_delete_activity(
            remote_actor=remote_user.actor,
            remote_comment=remote_comment,
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )
        comment_id = remote_comment.id

        activity.process_activity()

        assert WorkoutComment.query.filter_by(id=comment_id).first() is None

    def test_it_deletes_remote_workout_with_reply(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        remote_comment = self.create_comment(
            remote_user,
            remote_cycling_workout,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        reply = self.create_comment(
            user_1,
            remote_cycling_workout,
            text_visibility=PrivacyLevel.PUBLIC,
            parent_comment=remote_comment,
        )
        delete_activity = self.generate_workout_comment_delete_activity(
            remote_actor=remote_user.actor,
            remote_comment=remote_comment,
        )
        activity = get_activity_instance({'type': delete_activity['type']})(
            activity_dict=delete_activity
        )
        comment_id = remote_comment.id

        activity.process_activity()

        assert WorkoutComment.query.filter_by(id=comment_id).first() is None
        assert reply.reply_to is None

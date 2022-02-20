from abc import ABC, abstractmethod
from importlib import import_module
from typing import Callable, Dict, Tuple

from fittrackee import appLog
from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)

from .exceptions import UnsupportedActivityException


def get_activity_instance(activity_dict: Dict) -> Callable:
    activity_type = activity_dict['type']
    try:
        Activity = getattr(
            import_module('fittrackee.federation.activities'),
            f'{activity_type}Activity',
        )
    except AttributeError:
        raise UnsupportedActivityException(activity_type)
    return Activity


class AbstractActivity(ABC):
    def __init__(self, activity_dict: Dict) -> None:
        self.activity = activity_dict

    def activity_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def process_activity(self) -> None:
        pass


class FollowBaseActivity(AbstractActivity):
    def get_actors(self) -> Tuple[Actor, Actor]:
        """
        return actors from activity 'actor' and 'object'
        """
        actor = Actor.query.filter_by(
            activitypub_id=self.activity['actor']
        ).first()
        if not actor:
            raise ActorNotFoundException(
                message=f'actor not found for {self.activity_name()}'
            )

        object_actor_activitypub_id = (
            self.activity['object']
            if isinstance(self.activity['object'], str)
            else self.activity['object']['actor']
        )
        object_actor = Actor.query.filter_by(
            activitypub_id=object_actor_activitypub_id
        ).first()
        if not object_actor:
            raise ActorNotFoundException(
                message=f'object actor not found for {self.activity_name()}'
            )
        return actor, object_actor

    @abstractmethod
    def process_activity(self) -> None:
        pass


class FollowActivity(FollowBaseActivity):
    def process_activity(self) -> None:
        follower_actor, followed_actor = self.get_actors()
        try:
            follower_actor.user.send_follow_request_to(followed_actor.user)
        except FollowRequestAlreadyRejectedError as e:
            appLog.error('Follow activity: follow request already rejected.')
            raise e


class AcceptActivity(FollowBaseActivity):
    def process_activity(self) -> None:
        followed_actor, follower_actor = self.get_actors()
        try:
            followed_actor.user.approves_follow_request_from(
                follower_actor.user
            )
        except NotExistingFollowRequestError as e:
            appLog.error(
                f'{self.activity_name()}: follow request does not exist.'
            )
            raise e
        except FollowRequestAlreadyProcessedError as e:
            appLog.error(
                f'{self.activity_name()}: follow request already processed.'
            )
            raise e


class RejectActivity(FollowBaseActivity):
    def process_activity(self) -> None:
        followed_actor, follower_actor = self.get_actors()
        try:
            followed_actor.user.rejects_follow_request_from(
                follower_actor.user
            )
        except NotExistingFollowRequestError as e:
            appLog.error(
                f'{self.activity_name()}: follow request does not exist.'
            )
            raise e
        except FollowRequestAlreadyProcessedError as e:
            appLog.error(
                f'{self.activity_name()}: follow request already processed.'
            )
            raise e

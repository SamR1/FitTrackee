from abc import ABC, abstractmethod
from typing import Dict, Tuple

from fittrackee import appLog
from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.federation.utils_user import create_remote_user
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)


class AbstractActivity(ABC):
    def __init__(self, activity_dict: Dict) -> None:
        self.activity = activity_dict

    def activity_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def process_activity(self) -> None:
        pass

    def get_actors(
        self, create_remote_actor: bool = False
    ) -> Tuple[Actor, Actor]:
        """
        return actors from activity 'actor' and 'object'
        """
        actor = Actor.query.filter_by(
            activitypub_id=self.activity['actor']
        ).first()
        if not actor:
            if create_remote_actor:
                actor = create_remote_user(self.activity['actor'])
            else:
                raise ActorNotFoundException(
                    f'actor not found for {self.activity_name()}'
                )

        if isinstance(self.activity['object'], str):
            object_actor_activitypub_id = self.activity['object']
        else:
            object_actor_activitypub_id = (
                self.activity['object']['object']
                if self.activity['type'] == 'Undo'
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


class FollowBaseActivity(AbstractActivity):
    @abstractmethod
    def process_activity(self) -> None:
        pass


class FollowActivity(FollowBaseActivity):
    def process_activity(self) -> None:
        follower_actor, followed_actor = self.get_actors(
            create_remote_actor=True
        )
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


class UndoActivity(AbstractActivity):
    def process_activity(self) -> None:
        if self.activity['object']['type'] == 'Follow':
            self.undoes_follow()

    def undoes_follow(self) -> None:
        follower_actor, followed_actor = self.get_actors()
        try:
            followed_actor.user.undoes_follow(follower_actor.user)
        except NotExistingFollowRequestError as e:
            appLog.error(
                f'{self.activity_name()}: follow request does not exist.'
            )
            raise e

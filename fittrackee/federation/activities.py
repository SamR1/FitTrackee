from abc import ABC, abstractmethod
from typing import Dict

from fittrackee import appLog
from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.users.exceptions import FollowRequestAlreadyRejectedError
from fittrackee.users.utils.follow import create_follow_request


class AbstractActivity(ABC):
    def __init__(self, activity_dict: Dict) -> None:
        self.activity = activity_dict

    @abstractmethod
    def process_activity(self) -> None:
        pass


class FollowActivity(AbstractActivity):
    def process_activity(self) -> None:
        followed_actor = Actor.query.filter_by(
            activitypub_id=self.activity['object']
        ).first()
        if not followed_actor:
            raise ActorNotFoundException(
                message='followed actor not found for Follow Activity'
            )

        follower_actor = Actor.query.filter_by(
            activitypub_id=self.activity['actor']
        ).first()
        if not follower_actor:
            raise ActorNotFoundException(
                message='followed actor not found for Follow Activity'
            )

        try:
            create_follow_request(
                follower_user_id=follower_actor.user.id,
                followed_user=followed_actor.user,
            )
        except FollowRequestAlreadyRejectedError as e:
            appLog.error('Follow activity: follow request already rejected.')
            raise e

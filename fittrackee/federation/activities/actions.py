from abc import ABC, abstractmethod
from typing import Dict, Tuple

from fittrackee import appLog, db
from fittrackee.federation.exceptions import ActorNotFoundException
from fittrackee.federation.models import Actor
from fittrackee.federation.utils.user import (
    create_remote_user,
    get_or_create_remote_domain_from_url,
)
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)
from fittrackee.workouts.exceptions import SportNotFoundException
from fittrackee.workouts.models import Sport
from fittrackee.workouts.utils.workouts import create_workout


class AbstractActivity(ABC):
    def __init__(self, activity_dict: Dict) -> None:
        self.activity = activity_dict

    def activity_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def process_activity(self) -> None:
        pass

    def get_actor(self, create_remote_actor: bool = False) -> Actor:
        """
        return actor from activity
        """
        actor = Actor.query.filter_by(
            activitypub_id=self.activity['actor']
        ).first()
        if not actor:
            if create_remote_actor:
                remote_domain = get_or_create_remote_domain_from_url(
                    self.activity['actor']
                )
                user = create_remote_user(
                    remote_domain, self.activity['actor']
                )
                actor = user.actor
            else:
                raise ActorNotFoundException(
                    f'actor not found for {self.activity_name()}'
                )
        return actor

    def get_actors(
        self, create_remote_actor: bool = False
    ) -> Tuple[Actor, Actor]:
        """
        return actors from activity 'actor' and 'object'
        """
        actor = self.get_actor(create_remote_actor)

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


class CreateActivity(AbstractActivity):
    def create_remote_workout(self, actor: Actor) -> None:
        workout_data = self.activity['object']
        sport_id = workout_data['sport_id']
        if not sport_id:
            raise SportNotFoundException()
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            raise SportNotFoundException()
        new_workout = create_workout(actor.user, workout_data)
        db.session.add(new_workout)
        db.session.commit()

    def process_activity(self) -> None:
        actor = self.get_actor()
        if self.activity['object']['type'] == 'Workout':
            self.create_remote_workout(actor=actor)

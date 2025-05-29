from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Union

from fittrackee import appLog, db
from fittrackee.comments.models import Comment, CommentLike
from fittrackee.federation.constants import PUBLIC_STREAM
from fittrackee.federation.exceptions import (
    ActivityException,
    ActorNotFoundException,
    ObjectNotFoundException,
)
from fittrackee.federation.models import Actor
from fittrackee.federation.objects.workout import (
    convert_duration_string_to_seconds,
)
from fittrackee.federation.utils.user import (
    create_remote_user,
    get_or_create_remote_domain_from_url,
)
from fittrackee.users.exceptions import (
    FollowRequestAlreadyProcessedError,
    FollowRequestAlreadyRejectedError,
    NotExistingFollowRequestError,
)
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.constants import WORKOUT_DATE_FORMAT
from fittrackee.workouts.exceptions import SportNotFoundException
from fittrackee.workouts.models import Sport, Workout, WorkoutLike
from fittrackee.workouts.services.workout_creation_service import (
    WorkoutCreationService,
)

from ..objects.workout import convert_workout_activity


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
            activitypub_id=self.activity["actor"]
        ).first()
        if not actor:
            if create_remote_actor:
                remote_domain = get_or_create_remote_domain_from_url(
                    self.activity["actor"]
                )
                user = create_remote_user(
                    remote_domain, self.activity["actor"]
                )
                actor = user.actor
            else:
                raise ActorNotFoundException(
                    f"actor not found for {self.activity_name()}"
                )
        return actor

    def get_actors(
        self, create_remote_actor: bool = False
    ) -> Tuple[Actor, Actor]:
        """
        return actors from activity 'actor' and 'object'
        """
        actor = self.get_actor(create_remote_actor)

        if isinstance(self.activity["object"], str):
            object_actor_activitypub_id = self.activity["object"]
        else:
            object_actor_activitypub_id = (
                self.activity["object"]["object"]
                if self.activity["type"] == "Undo"
                else self.activity["object"]["actor"]
            )
        object_actor = Actor.query.filter_by(
            activitypub_id=object_actor_activitypub_id
        ).first()
        if not object_actor:
            raise ActorNotFoundException(
                message=f"object actor not found for {self.activity_name()}"
            )
        return actor, object_actor

    @staticmethod
    def _get_visibility(
        activity_object: Dict, actor: Actor
    ) -> VisibilityLevel:
        recipients = activity_object.get("cc", []) + activity_object.get(
            "to", []
        )
        if PUBLIC_STREAM in recipients:
            return VisibilityLevel.PUBLIC
        elif actor.followers_url in recipients:
            return VisibilityLevel.FOLLOWERS_AND_REMOTE
        # TODO:
        # For comments only (only visible to mentioned users)
        return VisibilityLevel.PRIVATE


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
            appLog.error("Follow activity: follow request already rejected.")
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
                f"{self.activity_name()}: follow request does not exist."
            )
            raise e
        except FollowRequestAlreadyProcessedError as e:
            appLog.error(
                f"{self.activity_name()}: follow request already processed."
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
                f"{self.activity_name()}: follow request does not exist."
            )
            raise e
        except FollowRequestAlreadyProcessedError as e:
            appLog.error(
                f"{self.activity_name()}: follow request already processed."
            )
            raise e


class UndoActivity(AbstractActivity):
    def process_activity(self) -> None:
        if self.activity["object"]["type"] == "Follow":
            self.undoes_follow()
        if self.activity["object"]["type"] == "Like":
            self.undoes_like()

    def undoes_follow(self) -> None:
        follower_actor, followed_actor = self.get_actors()
        try:
            followed_actor.user.undoes_follow(follower_actor.user)
        except NotExistingFollowRequestError as e:
            appLog.error(
                f"{self.activity_name()}: follow request does not exist."
            )
            raise e

    def undoes_like(self) -> None:
        like = None
        actor = self.get_actor(create_remote_actor=True)
        object_ap_id = self.activity["object"]["object"]

        # check if like is related to a workout
        target_object = Workout.query.filter_by(ap_id=object_ap_id).first()
        if target_object:
            like = WorkoutLike.query.filter_by(
                user_id=actor.user.id,
                workout_id=target_object.id,
            ).first()

        # check if like is related to a comment
        if not target_object:
            target_object = Comment.query.filter_by(ap_id=object_ap_id).first()
            if not target_object:
                raise ObjectNotFoundException("object", self.activity_name())

            like = CommentLike.query.filter_by(
                user_id=actor.user.id,
                comment_id=target_object.id,
            ).first()

        if like:
            db.session.delete(like)
            db.session.commit()


def create_comment(
    note_data: Dict, actor: Actor, visibility: VisibilityLevel
) -> Comment:
    reply_to_object_api_id = note_data.get("inReplyTo")
    workout = None
    parent_comment = None
    if reply_to_object_api_id:
        # comment to a workout
        workout = Workout.query.filter_by(ap_id=reply_to_object_api_id).first()
        if not workout:
            # reply to a comment
            parent_comment = Comment.query.filter_by(
                ap_id=reply_to_object_api_id
            ).first()
            if parent_comment:
                # get workout from parent comment
                workout = parent_comment.workout if parent_comment else None

    new_comment = Comment(
        user_id=actor.user.id,
        workout_id=workout.id if workout else None,
        text=note_data["content"],
        text_visibility=visibility,
        reply_to=parent_comment.id if parent_comment else None,
    )
    new_comment.ap_id = note_data["id"]
    new_comment.remote_url = note_data["url"]
    db.session.add(new_comment)
    db.session.flush()
    return new_comment


class CreateActivity(AbstractActivity):
    def create_remote_workout(self, actor: Actor) -> None:
        workout_data = self.activity["object"]
        sport_id = workout_data["sport_id"]
        if not sport_id:
            raise SportNotFoundException()
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            raise SportNotFoundException()
        workout_data["workout_visibility"] = self._get_visibility(
            workout_data, actor
        )
        service = WorkoutCreationService(
            actor.user, convert_workout_activity(workout_data)
        )
        new_workout, _ = service.process()
        db.session.commit()

    def create_remote_note(self, actor: Actor) -> None:
        note_data = self.activity["object"]
        new_comment = create_comment(
            note_data, actor, self._get_visibility(note_data, actor)
        )
        new_comment.create_mentions()
        db.session.commit()

    def process_activity(self) -> None:
        object_type = self.activity["object"]["type"]
        actor = self.get_actor(create_remote_actor=object_type == "Note")
        if object_type == "Workout":
            self.create_remote_workout(actor=actor)
        if object_type == "Note":
            self.create_remote_note(actor=actor)


class DeleteActivity(AbstractActivity):
    def process_activity(self) -> None:
        actor = self.get_actor()
        object_ap_id = self.activity["object"]["id"]

        # check if related object is a comment
        object_to_delete = Comment.query.filter_by(ap_id=object_ap_id).first()

        # if not, check if related object is a workout
        if not object_to_delete:
            object_to_delete = Workout.query.filter_by(
                ap_id=object_ap_id
            ).first()

        if not object_to_delete:
            raise ObjectNotFoundException("object", self.activity_name())

        if object_to_delete.user.actor.id != actor.id:
            raise ActivityException(
                f"{self.activity_name()}: activity actor does not "
                f"match workout actor."
            )

        db.session.delete(object_to_delete)
        db.session.commit()


class UpdateActivity(AbstractActivity):
    @staticmethod
    def convert_duration_string_to_timedelta(
        duration_string: str,
    ) -> timedelta:
        return timedelta(
            seconds=convert_duration_string_to_seconds(duration_string)
        )

    def update_remote_workout(self, actor: Actor) -> None:
        workout_data = self.activity["object"]
        workout_to_update = Workout.query.filter_by(
            ap_id=workout_data["id"]
        ).first()
        if not workout_to_update:
            raise ObjectNotFoundException("workout", self.activity_name())

        if workout_to_update.user.actor.id != actor.id:
            raise ActivityException(
                f"{self.activity_name()}: activity actor does not "
                f"match workout actor."
            )

        try:
            workout_to_update.ave_speed = workout_data["ave_speed"]
            workout_to_update.distance = workout_data["distance"]
            workout_to_update.duration = (
                self.convert_duration_string_to_timedelta(
                    workout_data["duration"]
                )
            )
            workout_to_update.max_speed = workout_data["max_speed"]
            workout_to_update.moving = (
                self.convert_duration_string_to_timedelta(
                    workout_data["moving"]
                )
            )
            workout_to_update.sport_id = workout_data["sport_id"]
            workout_to_update.title = workout_data["title"]
            # workout date must be in GMT+00:00
            workout_to_update.workout_date = datetime.strptime(
                workout_data["workout_date"], WORKOUT_DATE_FORMAT
            ).replace(tzinfo=timezone.utc)
            workout_to_update.workout_visibility = self._get_visibility(
                workout_data, actor
            )
            db.session.commit()
        except Exception as e:
            raise ActivityException(
                f"{self.activity_name()}: invalid Workout activity "
                f"({e.__class__.__name__}: {e})."
            ) from e

    def update_remote_workout_comment(self, actor: Actor) -> None:
        note_data = self.activity["object"]
        comment_to_update = Comment.query.filter_by(
            ap_id=note_data["id"]
        ).first()
        if not comment_to_update:
            comment_to_update = create_comment(
                note_data, actor, self._get_visibility(note_data, actor)
            )

        if comment_to_update.user.actor.id != actor.id:
            raise ActivityException(
                f"{self.activity_name()}: activity actor does not "
                f"match Note actor."
            )

        try:
            comment_to_update.text = note_data["content"]
            comment_to_update.text_visibility = self._get_visibility(
                note_data, actor
            )
            comment_to_update.modification_date = datetime.now(timezone.utc)
            comment_to_update.update_mentions()
            db.session.commit()
        except Exception as e:
            raise ActivityException(
                f"{self.activity_name()}: invalid Note activity "
                f"({e.__class__.__name__}: {e})."
            ) from e

    def process_activity(self) -> None:
        object_type = self.activity["object"]["type"]
        actor = self.get_actor(create_remote_actor=object_type == "Note")
        if object_type == "Workout":
            self.update_remote_workout(actor)
        if object_type == "Note":
            self.update_remote_workout_comment(actor)


class LikeActivity(AbstractActivity):
    def process_activity(self) -> None:
        like: Union[None, WorkoutLike, CommentLike] = None
        actor = self.get_actor(create_remote_actor=True)
        object_ap_id = self.activity["object"]

        # check if like is related to a workout
        target_object = Workout.query.filter_by(ap_id=object_ap_id).first()
        if target_object:
            like = WorkoutLike(
                user_id=actor.user.id, workout_id=target_object.id
            )

        # check if like is related to a comment
        else:
            target_object = Comment.query.filter_by(ap_id=object_ap_id).first()
            if not target_object:
                raise ObjectNotFoundException("object", self.activity_name())

            like = CommentLike(
                user_id=actor.user.id, comment_id=target_object.id
            )

        if like:
            db.session.add(like)
            db.session.commit()

from typing import TYPE_CHECKING, Dict

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel

from ..enums import ActivityType
from .base_object import BaseObject

if TYPE_CHECKING:
    from fittrackee.comments.models import WorkoutComment
    from fittrackee.workouts.models import Workout


class WorkoutCommentObject(BaseObject):

    workout: 'Workout'
    workout_comment: 'WorkoutComment'

    def __init__(
        self, workout_comment: 'WorkoutComment', activity_type: str
    ) -> None:
        """
        Note: No visibility check on instantiation if activity is not a
        creation.
        It should be possible, for instance, to send an Update activity for a
        comment with remote mentions removed.
        """
        self._check_visibility(workout_comment, activity_type)
        self.workout_comment = workout_comment
        self.visibility = workout_comment.text_visibility
        self.workout = workout_comment.workout
        self.type = ActivityType(activity_type)
        self.actor = self.workout_comment.user.actor
        self.activity_id = self.workout_comment.ap_id
        self.published = self._get_published_date(
            self.workout_comment.created_at
        )
        self.object_url = self.workout_comment.remote_url
        self.activity_dict = self._init_activity_dict()

    @staticmethod
    def _check_visibility(
        comment: 'WorkoutComment', activity_type: str
    ) -> None:
        if (
            activity_type == 'Create'
            and comment.text_visibility
            in [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
            and not comment.mentions.all()
        ):
            raise InvalidVisibilityException(
                f"object visibility is: '{comment.text_visibility.value}'"
            )

    def get_activity(self) -> Dict:
        (
            text_with_mention,
            mentioned_users,
        ) = self.workout_comment.handle_mentions()
        self.activity_dict['object']['type'] = 'Note'
        self.activity_dict['object']['content'] = text_with_mention
        self.activity_dict['object']['inReplyTo'] = (
            self.workout_comment.parent_comment.ap_id
            if self.workout_comment.reply_to
            else self.workout.ap_id
        )
        if self.type == ActivityType.UPDATE:
            self.activity_dict['object'] = {
                **self.activity_dict['object'],
                'updated': self._get_modification_date(self.workout_comment),
            }
        # existing mentions (local and remote)
        mentions = [
            user.actor.activitypub_id
            for user in mentioned_users["local"].union(
                mentioned_users["remote"]
            )
        ]
        if self.visibility in [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]:
            self.activity_dict['to'] = mentions
            self.activity_dict['cc'] = []
            self.activity_dict['object']['to'] = mentions
            self.activity_dict['object']['cc'] = []
        else:
            self.activity_dict['cc'].extend(mentions)
            self.activity_dict['object']['cc'].extend(mentions)
        return self.activity_dict

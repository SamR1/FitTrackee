from typing import TYPE_CHECKING, Dict

from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.visibility_levels import VisibilityLevel

from ..enums import ActivityType
from .base_object import BaseObject
from .exceptions import InvalidObjectException

if TYPE_CHECKING:
    from fittrackee.comments.models import Comment
    from fittrackee.workouts.models import Workout


class CommentObject(BaseObject):
    workout: "Workout"
    comment: "Comment"

    def __init__(self, comment: "Comment", activity_type: str) -> None:
        """
        Note: No visibility check on instantiation if activity is not a
        creation.
        It should be possible, for instance, to send an Update activity for a
        comment with remote mentions removed.
        """
        self._check_visibility(comment, activity_type)
        self.comment = comment
        if not self.comment.ap_id or not self.comment.remote_url:
            raise InvalidObjectException(
                "Invalid comment, missing 'ap_id' or 'remote_url'"
            )

        self.visibility = comment.text_visibility
        self.workout = comment.workout
        self.type = ActivityType(activity_type)
        self.actor = self.comment.user.actor
        self.activity_id = self.comment.ap_id
        self.published = self._get_published_date(self.comment.created_at)
        self.object_url = self.comment.remote_url
        self.activity_dict = self._init_activity_dict()

    @staticmethod
    def _check_visibility(comment: "Comment", activity_type: str) -> None:
        if (
            activity_type == "Create"
            and comment.text_visibility
            in [VisibilityLevel.PRIVATE, VisibilityLevel.FOLLOWERS]
            and not comment.mentioned_users.all()
        ):
            raise InvalidVisibilityException(
                f"object visibility is: '{comment.text_visibility.value}'"
            )

    def get_activity(self) -> Dict:
        (
            text_with_mention,
            mentioned_users,
        ) = self.comment.handle_mentions()
        self.activity_dict["object"]["type"] = "Note"
        self.activity_dict["object"]["content"] = text_with_mention
        self.activity_dict["object"]["inReplyTo"] = (
            self.comment.parent_comment.ap_id
            if self.comment.reply_to
            else self.workout.ap_id
        )
        if self.type == ActivityType.UPDATE:
            self.activity_dict["object"] = {
                **self.activity_dict["object"],
                "updated": self._get_modification_date(self.comment),
            }
        # existing mentions (local and remote)
        mentions = [
            user.actor.activitypub_id
            for user in mentioned_users["local"].union(
                mentioned_users["remote"]
            )
        ]
        if self.visibility in [
            VisibilityLevel.PRIVATE,
            VisibilityLevel.FOLLOWERS,
        ]:
            self.activity_dict["to"] = mentions
            self.activity_dict["cc"] = []
            self.activity_dict["object"]["to"] = mentions
            self.activity_dict["object"]["cc"] = []
        else:
            self.activity_dict["cc"].extend(mentions)
            self.activity_dict["object"]["cc"].extend(mentions)
        return self.activity_dict

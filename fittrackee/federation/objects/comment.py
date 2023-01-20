from typing import TYPE_CHECKING, Dict

from ..enums import ActivityType
from .base_object import BaseObject

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout, WorkoutComment


class WorkoutCommentObject(BaseObject):

    workout: 'Workout'
    workout_comment: 'WorkoutComment'

    def __init__(
        self, workout_comment: 'WorkoutComment', activity_type: str
    ) -> None:
        self._check_visibility(workout_comment.text_visibility)
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

    def get_activity(self) -> Dict:
        self.activity_dict['object']['type'] = 'Note'
        self.activity_dict['object']['content'] = self.workout_comment.text
        self.activity_dict['object']['inReplyTo'] = self.workout.ap_id
        if self.type == ActivityType.UPDATE:
            self.activity_dict['object'] = {
                **self.activity_dict['object'],
                'updated': self._get_modification_date(self.workout_comment),
            }
        return self.activity_dict

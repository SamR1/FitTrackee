from typing import TYPE_CHECKING, Dict

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.workouts.exceptions import PrivateWorkoutException

from ..constants import AP_CTX, DATE_FORMAT, PUBLIC_STREAM
from ..enums import ActivityType
from .base_object import ActivityObject

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


class WorkoutObject(ActivityObject):
    workout: 'Workout'

    def __init__(self, workout: 'Workout') -> None:
        if workout.workout_visibility == PrivacyLevel.PRIVATE:
            raise PrivateWorkoutException()
        self.workout = workout
        self.type = ActivityType.CREATE
        self.actor = self.workout.user.actor
        self.activity_id = (
            f'https://{self.actor.activitypub_id}/'
            f'workouts/{self.workout.short_id}'
        )
        self.published = self.workout.creation_date.strftime(DATE_FORMAT)
        self.workout_url = (
            f'https://{self.actor.domain.name}/'
            f'workouts/{self.workout.short_id}'
        )
        self.activity_dict = self._init_activity_dict()

    def _init_activity_dict(self) -> Dict:
        return {
            '@context': AP_CTX,
            'type': self.type.value,
            'actor': self.actor.activitypub_id,
            'published': self.published,
            'object': {
                'id': self.activity_id,
                'published': self.published,
                'url': self.workout_url,
                'attributedTo': self.actor.activitypub_id,
            },
        }

    def _get_note_content(self) -> str:
        # TODO: handle translation and imperial units depending on user
        # preferences
        return f"""New workout "{self.workout.title}"'

Distance: {self.workout.distance}km
Duration: {self.workout.duration}

#fittrackee

link: {self.workout_url}
"""

    def _update_activity_recipients(self, activity: Dict) -> Dict:
        if self.workout.workout_visibility == PrivacyLevel.PUBLIC:
            activity['to'] = [PUBLIC_STREAM]
            activity['cc'] = [self.actor.followers_url]
            activity['object']['to'] = [PUBLIC_STREAM]
            activity['object']['cc'] = [self.actor.followers_url]
        else:
            activity['to'] = [self.actor.followers_url]
            activity['cc'] = []
            activity['object']['to'] = [self.actor.followers_url]
            activity['object']['cc'] = []
        return activity

    def serialize(self, is_note: bool = False) -> Dict:
        activity = self.activity_dict.copy()
        if is_note:
            activity['id'] = f'{self.activity_id}/note/activity'
            activity['object']['type'] = 'Note'
            activity['object']['content'] = self._get_note_content()
        else:
            activity['id'] = f'{self.activity_id}/activity'
            activity['object'] = {
                **activity['object'],
                **{
                    'type': 'Workout',
                    'ascent': self.workout.ascent,
                    'descent': self.workout.descent,
                    'distance': self.workout.distance,
                    'duration': self.workout.duration,
                    'max_alt': self.workout.max_alt,
                    'min_alt': self.workout.min_alt,
                    'moving': self.workout.moving,
                    'sport_id': self.workout.sport_id,
                    'title': self.workout.title,
                    'workout_date': self.workout.workout_date.strftime(
                        DATE_FORMAT
                    ),
                },
            }
        return self._update_activity_recipients(activity)

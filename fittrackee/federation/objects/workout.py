from typing import TYPE_CHECKING, Dict

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.workouts.constants import WORKOUT_DATE_FORMAT

from ..constants import AP_CTX, DATE_FORMAT, PUBLIC_STREAM
from ..enums import ActivityType
from ..exceptions import InvalidWorkoutException
from .base_object import BaseObject
from .exceptions import InvalidVisibilityException
from .templates.workout_note import WORKOUT_NOTE

if TYPE_CHECKING:
    from fittrackee.workouts.models import Workout


class WorkoutObject(BaseObject):
    workout: 'Workout'

    def __init__(self, workout: 'Workout', activity_type: str) -> None:
        if workout.workout_visibility in [
            PrivacyLevel.PRIVATE,
            PrivacyLevel.FOLLOWERS,
        ]:
            raise InvalidVisibilityException(
                f"object visibility is: '{workout.workout_visibility.value}'"
            )
        self.workout = workout
        self.type = ActivityType(activity_type)
        self.actor = self.workout.user.actor
        self.activity_id = (
            f'{self.actor.activitypub_id}/workouts/{self.workout.short_id}'
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
        # TODO:
        # handle translation and imperial units depending on user preferences
        return WORKOUT_NOTE.format(
            sport_label=self.workout.sport.label,
            workout_title=self.workout.title,
            workout_distance=self.workout.distance,
            workout_duration=self.workout.duration,
            workout_url=self.workout_url,
        )

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

    def get_activity(self, is_note: bool = False) -> Dict:
        activity = self.activity_dict.copy()
        # for non-FitTrackee instances (like Mastodon)
        if is_note:
            activity['id'] = f'{self.activity_id}/note/activity'
            activity['object']['type'] = 'Note'
            activity['object']['content'] = self._get_note_content()
        # for FitTrackee instances
        else:
            activity['id'] = f'{self.activity_id}/activity'
            activity['object'] = {
                **activity['object'],
                **{
                    'type': 'Workout',
                    'ave_speed': float(self.workout.ave_speed),
                    'distance': float(self.workout.distance),
                    'duration': str(self.workout.duration),
                    'max_speed': float(self.workout.max_speed),
                    'moving': str(self.workout.moving),
                    'sport_id': self.workout.sport_id,
                    'title': self.workout.title,
                    'workout_date': self.workout.workout_date.strftime(
                        WORKOUT_DATE_FORMAT
                    ),
                    'workout_visibility': self.workout.workout_visibility,
                },
            }
        return self._update_activity_recipients(activity)


def convert_duration_string_to_seconds(duration_str: str) -> int:
    try:
        hour, minutes, seconds = duration_str.split(':')
        duration = int(hour) * 3600 + int(minutes) * 60 + int(seconds)
    except Exception as e:
        raise InvalidWorkoutException(
            f'duration or moving format is invalid ({e})'
        )
    return duration


def convert_workout_activity(workout_data: Dict) -> Dict:
    return {
        **workout_data,
        'duration': convert_duration_string_to_seconds(
            workout_data['duration']
        ),
        'moving': convert_duration_string_to_seconds(workout_data['moving']),
    }

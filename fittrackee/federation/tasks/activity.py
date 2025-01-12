from importlib import import_module
from typing import Callable, Dict

from fittrackee import dramatiq

from ..exceptions import UnsupportedActivityException


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


@dramatiq.actor(queue_name='fittrackee_activities')
def handle_activity(activity: Dict) -> None:
    activity = get_activity_instance({'type': activity['type']})(
        activity_dict=activity
    )
    activity.process_activity()  # type: ignore

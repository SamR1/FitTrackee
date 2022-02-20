from typing import Dict

from fittrackee import dramatiq
from fittrackee.federation.utils import get_activity_instance


@dramatiq.actor(queue_name='fittrackee_activities')
def handle_activity(activity: Dict) -> None:
    activity = get_activity_instance({'type': activity['type']})(
        activity_dict=activity
    )
    activity.process_activity()  # type: ignore

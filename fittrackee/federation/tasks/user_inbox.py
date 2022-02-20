from typing import Dict, List

from fittrackee import appLog, dramatiq
from fittrackee.federation.exceptions import SenderNotFoundException
from fittrackee.federation.inbox import send_to_remote_user_inbox
from fittrackee.federation.models import Actor


@dramatiq.actor(queue_name='fittrackee_users_inbox')
def send_to_users_inbox(
    sender_id: int, activity: Dict, recipients: List
) -> None:
    sender = Actor.query.filter_by(id=sender_id).first()
    if not sender:
        appLog.error('Sender not found when sending to users inbox.')
        raise SenderNotFoundException()
    for recipient_inbox_url in recipients:
        send_to_remote_user_inbox(
            sender=sender,
            activity=activity,
            recipient_inbox_url=recipient_inbox_url,
        )

from typing import Dict, List

from fittrackee import appLog, dramatiq
from fittrackee.federation.exceptions import SenderNotFoundException
from fittrackee.federation.inbox import send_to_inbox
from fittrackee.federation.models import Actor


@dramatiq.actor(queue_name='fittrackee_send_to_remote_inbox')
def send_to_remote_inbox(
    sender_id: int, activity: Dict, recipients: List
) -> None:
    sender = Actor.query.filter_by(id=sender_id).first()
    if not sender:
        appLog.error('Sender not found when sending to inbox.')
        raise SenderNotFoundException()
    for inbox_url in recipients:
        send_to_inbox(sender=sender, activity=activity, inbox_url=inbox_url)

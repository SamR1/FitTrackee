from typing import Dict

from fittrackee import dramatiq, email_service


@dramatiq.actor(queue_name="fittrackee_emails")
def send_email(user_data: Dict, email_data: Dict, *, template: str) -> None:
    email_service.send(
        template=template,
        lang=user_data["language"],
        recipient=user_data["email"],
        data=email_data,
    )

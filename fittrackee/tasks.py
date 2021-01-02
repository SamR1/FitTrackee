from typing import Dict

from fittrackee import dramatiq, email_service


@dramatiq.actor(queue_name='fittrackee_emails')
def reset_password_email(user: Dict, email_data: Dict) -> None:
    email_service.send(
        template='password_reset_request',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )

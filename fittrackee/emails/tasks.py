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


@dramatiq.actor(queue_name='fittrackee_emails')
def email_updated_to_current_address(user: Dict, email_data: Dict) -> None:
    email_service.send(
        template='email_update_to_current_email',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )


@dramatiq.actor(queue_name='fittrackee_emails')
def email_updated_to_new_address(user: Dict, email_data: Dict) -> None:
    email_service.send(
        template='email_update_to_new_email',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )


@dramatiq.actor(queue_name='fittrackee_emails')
def password_change_email(user: Dict, email_data: Dict) -> None:
    email_service.send(
        template='password_change',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )


@dramatiq.actor(queue_name='fittrackee_emails')
def account_confirmation_email(user: Dict, email_data: Dict) -> None:
    email_service.send(
        template='account_confirmation',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )


@dramatiq.actor(queue_name='fittrackee_emails')
def data_export_email(user: Dict, email_data: Dict) -> None:
    email_service.send(
        template='data_export_ready',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )

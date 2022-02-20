from datetime import datetime
from json import dumps
from typing import Dict
from urllib.parse import urlparse

import requests

from fittrackee import appLog

from .models import Actor
from .signature import VALID_DATE_FORMAT, signature_header


def send_to_remote_user_inbox(
    sender: Actor, activity: Dict, recipient: Actor
) -> None:
    now_str = datetime.utcnow().strftime(VALID_DATE_FORMAT)
    parsed_inbox_url = urlparse(recipient.inbox_url)
    signed_header = signature_header(
        host=parsed_inbox_url.netloc,
        path=parsed_inbox_url.path,
        date_str=now_str,
        actor=sender,
    )
    response = requests.post(
        recipient.inbox_url,
        data=dumps(activity),
        headers={
            "Host": parsed_inbox_url.netloc,
            "Date": now_str,
            "Signature": signed_header,
            "Content-Type": "application/ld+json",
        },
    )
    if response.status_code >= 400:
        appLog.error(
            f"Error when send to user inbox '{recipient.inbox_url}', "
            f"status code: {response.status_code}, "
            f"content: {response.content.decode()}"
        )

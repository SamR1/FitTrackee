from datetime import datetime
from json import dumps
from typing import Dict, Union
from urllib.parse import urlparse

import requests
from flask import Request

from fittrackee import appLog
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    UnauthorizedErrorResponse,
)

from .exceptions import InvalidSignatureException
from .models import Actor
from .signature import (
    VALID_DATE_FORMAT,
    SignatureVerification,
    generate_digest,
    generate_signature_header,
)
from .tasks.activity import handle_activity
from .utils import is_invalid_activity_data


def inbox(request: Request) -> Union[Dict, HttpResponse]:
    activity_data = request.get_json()
    if not activity_data or is_invalid_activity_data(activity_data):
        return InvalidPayloadErrorResponse()

    try:
        signature_verification = SignatureVerification.get_signature(request)
        signature_verification.verify()
    except InvalidSignatureException:
        return UnauthorizedErrorResponse(message='Invalid signature.')

    handle_activity.send(activity=activity_data)

    return {'status': 'success'}


def send_to_inbox(sender: Actor, activity: Dict, inbox_url: str) -> None:
    now_str = datetime.utcnow().strftime(VALID_DATE_FORMAT)
    parsed_inbox_url = urlparse(inbox_url)
    digest = generate_digest(activity)
    signed_header = generate_signature_header(
        host=parsed_inbox_url.netloc,
        path=parsed_inbox_url.path,
        date_str=now_str,
        actor=sender,
        digest=digest,
    )
    response = requests.post(
        inbox_url,
        data=dumps(activity),
        headers={
            'Host': parsed_inbox_url.netloc,
            'Date': now_str,
            'Signature': signed_header,
            'Digest': digest,
            'Content-Type': 'application/ld+json',
        },
    )
    if response.status_code >= 400:
        appLog.error(
            f"Error when send to inbox '{inbox_url}', "
            f"status code: {response.status_code}, "
            f"content: {response.content.decode()}"
        )

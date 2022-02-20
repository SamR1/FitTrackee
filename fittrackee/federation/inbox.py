from datetime import datetime
from json import dumps
from typing import Dict, Optional, Union
from urllib.parse import urlparse

import requests
from flask import Request

from fittrackee import appLog
from fittrackee.responses import (
    HttpResponse,
    InvalidPayloadErrorResponse,
    UnauthorizedErrorResponse,
    UserNotFoundErrorResponse,
)

from .exceptions import InvalidSignatureException
from .models import Actor, Domain
from .signature import (
    VALID_DATE_FORMAT,
    SignatureVerification,
    signature_header,
)
from .utils import is_invalid_activity_data


def inbox(
    request: Request, app_domain: Domain, username: Optional[str]
) -> Union[Dict, HttpResponse]:
    # if user inbox
    if username:
        recipient = Actor.query.filter_by(
            preferred_username=username,
            domain_id=app_domain.id,
        ).first()
        if not recipient:
            return UserNotFoundErrorResponse()

    activity_data = request.get_json()
    if not activity_data or is_invalid_activity_data(activity_data):
        return InvalidPayloadErrorResponse()

    try:
        signature_verification = SignatureVerification.get_signature(request)
        signature_verification.verify()
    except InvalidSignatureException:
        return UnauthorizedErrorResponse(message='Invalid signature.')

    # TODO handle activity

    return {'status': 'success'}


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

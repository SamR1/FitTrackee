import time
from datetime import timedelta
from typing import Optional
from uuid import UUID

import humanize
import shortuuid
from sqlalchemy.sql import text

from fittrackee import db


def get_readable_duration(duration: int, locale: Optional[str] = None) -> str:
    """
    Return readable and localized duration from duration in seconds
    """
    if locale is None:
        locale = 'en'
    if locale != 'en':
        try:
            _t = humanize.i18n.activate(locale)  # noqa
        except FileNotFoundError:
            locale = 'en'
    readable_duration = humanize.naturaldelta(timedelta(seconds=duration))
    if locale != 'en':
        humanize.i18n.deactivate()
    return readable_duration


def clean(sql: str, days: int) -> int:
    limit = int(time.time()) - (days * 86400)
    result = db.session.execute(text(sql), {'limit': limit})
    db.session.commit()
    return result.rowcount


def encode_uuid(uuid_value: UUID) -> str:
    """
    Return short id string from a UUID
    """
    return shortuuid.encode(uuid_value)


def decode_short_id(short_id: str) -> UUID:
    """
    Return UUID from a short id string
    """
    return shortuuid.decode(short_id)

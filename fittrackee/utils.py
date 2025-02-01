import time
from uuid import UUID

import nh3
import shortuuid
from sqlalchemy.sql import text

from fittrackee import db


def clean(sql: str, days: int) -> int:
    limit = int(time.time()) - (days * 86400)
    result = db.session.execute(text(sql), {'limit': limit})
    db.session.commit()
    return result.rowcount  # type: ignore


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


def clean_input(input_text: str) -> str:
    # HTML sanitization
    return nh3.clean(
        input_text,
        tags={"a", "br", "p", "span"},
        attributes={"a": {"href", "target"}},
    )

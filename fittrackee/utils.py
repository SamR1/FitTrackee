import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache, wraps
from typing import Callable, Hashable, Tuple
from uuid import UUID

import nh3
import shortuuid
from sqlalchemy.sql import text

from fittrackee import db


def clean(sql: str, days: int) -> int:
    limit = int(time.time()) - (days * 86400)
    result = db.session.execute(text(sql), {"limit": limit})
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


def clean_input(input_text: str, for_markdown_renderer: bool = False) -> str:
    # HTML sanitization
    tags = {"a", "br", "p", "span"}
    attributes = {"a": {"href", "target"}}
    if for_markdown_renderer:
        tags.update({"img", "strong", "em"})
        attributes["img"] = {"src", "alt"}
    return nh3.clean(
        input_text,
        tags=tags,
        attributes=attributes,
    )


class TimedLRUCache:
    def __init__(self, seconds: int, maxsize: int = 128) -> None:
        self.lifetime = timedelta(seconds=seconds)
        self.maxsize = maxsize

    def __call__(self, f: Callable) -> Callable:
        cached_func = lru_cache(maxsize=self.maxsize)(f)
        cached_func.expiration = (  # type: ignore[attr-defined]
            datetime.now(timezone.utc) + self.lifetime
        )

        @wraps(f)
        def wrapper(*args: Tuple, **kwargs: Hashable) -> Callable:
            if datetime.now(timezone.utc) >= cached_func.expiration:  # type: ignore[attr-defined]
                cached_func.cache_clear()
                cached_func.expiration = (  # type: ignore[attr-defined]
                    datetime.now(timezone.utc) + self.lifetime
                )
            return cached_func(*args, **kwargs)

        return wrapper

import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import humanize
import nh3
import pytz
import shortuuid
from babel.dates import format_datetime
from sqlalchemy import DateTime
from sqlalchemy.sql import text
from sqlalchemy.types import TypeDecorator

from fittrackee import db
from fittrackee.languages import LANGUAGES_DATE_STRING
from fittrackee.users.constants import USER_DATE_FORMAT, USER_TIMEZONE
from fittrackee.users.utils.language import get_language

if TYPE_CHECKING:
    from sqlalchemy.engine.interfaces import Dialect

    from fittrackee.users.models import User


# Store Timezone Aware Timestamps as Timezone Naive UTC
# source: https://docs.sqlalchemy.org/en/14/core/custom_types.html#store-timezone-aware-timestamps-as-timezone-naive-utc  # noqa
class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: Optional[datetime], dialect: 'Dialect'
    ) -> Optional[datetime]:
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(
        self, value: Optional[datetime], dialect: 'Dialect'
    ) -> Optional[datetime]:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value


def get_date_string_for_user(date_to_format: datetime, user: "User") -> str:
    """
    Note: date_to_format is a timezone-aware datetime in UTC
    """
    user_language = get_language(user.language)
    user_timezone = user.timezone if user.timezone else USER_TIMEZONE
    user_date_format = (
        user.date_format if user.date_format else USER_DATE_FORMAT
    )

    date_format = (
        LANGUAGES_DATE_STRING[user_language]
        if user_date_format == "date_string"
        else user_date_format
    )
    return format_datetime(
        date_to_format.astimezone(pytz.timezone(user_timezone)),
        format=f"{date_format} - HH:mm:ss",
        locale=user_language,
    )


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


def aware_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_datetime_in_utc(
    date_string: str, date_format: str = '%Y-%m-%d'
) -> datetime:
    return datetime.strptime(date_string, date_format).replace(
        tzinfo=timezone.utc
    )


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


def clean_input(text: str) -> str:
    # HTML sanitization
    return nh3.clean(
        text,
        tags={"a", "br", "p", "span"},
        attributes={"a": {"href", "target"}},
    )

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

import humanize
import pytz
from babel.dates import format_datetime

from fittrackee.languages import LANGUAGES_DATE_STRING
from fittrackee.users.constants import USER_DATE_FORMAT, USER_TIMEZONE
from fittrackee.users.utils.language import get_language

if TYPE_CHECKING:
    from fittrackee.users.models import User


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
        locale = "en"
    if locale != "en":
        try:
            _t = humanize.i18n.activate(locale)
        except FileNotFoundError:
            locale = "en"
    readable_duration = humanize.naturaldelta(timedelta(seconds=duration))
    if locale != "en":
        humanize.i18n.deactivate()
    return readable_duration


def aware_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_datetime_in_utc(
    date_string: str, date_format: str = "%Y-%m-%d"
) -> datetime:
    return datetime.strptime(date_string, date_format).replace(
        tzinfo=timezone.utc
    )

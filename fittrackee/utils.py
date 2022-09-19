import time
from datetime import timedelta
from typing import Optional

import humanize

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
    result = db.engine.execute(sql, {'limit': limit})
    return result.rowcount

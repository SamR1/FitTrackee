from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, TypeDecorator

if TYPE_CHECKING:
    from sqlalchemy.engine import Dialect


PSQL_INTEGER_LIMIT = 2147483647


# Store Timezone Aware Timestamps as Timezone Naive UTC
# source: https://docs.sqlalchemy.org/en/14/core/custom_types.html#store-timezone-aware-timestamps-as-timezone-naive-utc  # noqa
class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(
        self, value: Optional[datetime], dialect: "Dialect"
    ) -> Optional[datetime]:
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(
        self, value: Optional[datetime], dialect: "Dialect"
    ) -> Optional[datetime]:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value

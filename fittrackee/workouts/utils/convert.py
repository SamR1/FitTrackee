import re
from datetime import timedelta
from typing import Optional, Union

from ..exceptions import InvalidDurationException


def convert_in_duration(value: str) -> timedelta:
    if not re.match(r"^([0-1]?\d|2[0-3]):[0-5]\d(:[0-5]\d)?$", value):
        raise InvalidDurationException()
    hours = int(value.split(":")[0])
    minutes = int(value.split(":")[1])
    return timedelta(seconds=(hours * 3600 + minutes * 60))


def convert_value_to_integer(
    record_type: str, val: Union[timedelta, float, None]
) -> Optional[int]:
    if val is None or record_type not in ["AS", "FD", "HA", "LD", "MS"]:
        return None

    if isinstance(val, timedelta):  # record_type == "LD"
        return int(val.total_seconds())

    multiplier = (
        100 if record_type in ["AS", "MS"] else 1000  # 'FD' and 'HA
    )
    return round(val * multiplier)

from datetime import timedelta
from typing import Optional, Union

from .duration import _remove_microseconds


def convert_in_duration(value: str) -> timedelta:
    hours = int(value.split(":")[0])
    minutes = int(value.split(":")[1])
    return timedelta(seconds=(hours * 3600 + minutes * 60))


def convert_timedelta_to_integer(value: str) -> int:
    hours, minutes, seconds = str(value).split(":")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def convert_value_to_integer(
    record_type: str, val: Union[float, timedelta]
) -> Optional[int]:
    if val is None or record_type not in ["AS", "FD", "HA", "LD", "MS"]:
        return None

    if isinstance(val, timedelta):  # "LD"
        return convert_timedelta_to_integer(str(_remove_microseconds(val)))

    multiplier = (
        100 if record_type in ["AS", "MS"] else 1000  # 'FD' and 'HA
    )
    return round(val * multiplier)

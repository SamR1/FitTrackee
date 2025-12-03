import re
from datetime import timedelta
from typing import Optional, Union

import pandas as pd

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
    from ..models import RECORD_TYPES

    if val is None or record_type not in RECORD_TYPES:
        return None

    if isinstance(val, timedelta):  # self.record_type in ["LD", "AP", "MP"]
        return int(val.total_seconds())

    multiplier = (
        100 if record_type in ["AS", "MS"] else 1000  # 'FD' and 'HA
    )
    return round(val * multiplier)


def convert_speed_into_pace_duration(
    speed: Optional[float],
) -> Optional[timedelta]:
    # return pace as duration for 1km
    #
    # note: speed unit is 'km/h'
    if speed is None:
        return None
    if not speed:
        return timedelta(seconds=0)
    return (
        pd.Timedelta(timedelta(minutes=60 / speed)).round("s").to_pytimedelta()
    )


def convert_speed_into_pace_in_sec_per_meter(
    speed: Optional[float],
) -> Optional[float]:
    # return pace in s/m
    #
    # note: speed unit is 'km/h'
    if speed is None:
        return None
    if not speed:
        return 0.0
    return round(1 / (speed / 3.6), 10)

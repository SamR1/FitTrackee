import re
from datetime import timedelta
from typing import Optional, Union

from ..constants import POWER_SPORTS, RPM_CADENCE_SPORTS, SPM_CADENCE_SPORTS
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


def get_cadence(sport_label: str, cadence: Optional[int]) -> Optional[int]:
    if cadence is None:
        return None

    if sport_label in RPM_CADENCE_SPORTS:
        return cadence

    if sport_label in SPM_CADENCE_SPORTS:
        return cadence * 2

    return None


def get_power(sport_label: str, power: Optional[int]) -> Optional[int]:
    if power is None:
        return None

    if sport_label in POWER_SPORTS:
        return power

    return None

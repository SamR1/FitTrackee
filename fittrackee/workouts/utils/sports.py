from datetime import timedelta
from typing import Optional

from fittrackee.workouts.constants import (
    PACE_SPORTS,
    POWER_SPORTS,
    RPM_CADENCE_SPORTS,
    SPM_CADENCE_SPORTS,
)


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


def get_pace(sport_label: str, pace: Optional[timedelta]) -> Optional[str]:
    if pace is None:
        return None

    if sport_label in PACE_SPORTS:
        return str(pace)

    return None

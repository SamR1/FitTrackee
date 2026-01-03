from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from fittrackee.constants import PaceSpeedDisplay
from fittrackee.workouts.constants import (
    CADENCE_SPORTS,
    POWER_SPORTS,
    RPM_CADENCE_SPORTS,
    SPM_CADENCE_SPORTS,
    SPORTS_WITHOUT_ELEVATION_DATA,
)

if TYPE_CHECKING:
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


@dataclass
class SportDisplayedData:
    display_elevation: bool
    display_pace: bool
    display_power: bool
    display_speed: bool
    display_cadence: bool
    display_spm_cadence: bool
    display_rpm_cadence: bool


def get_sports_displayed_data(
    sports: List["Sport"],
    user: Optional["User"],
    force_display_speed: bool = False,
) -> Dict:
    """
    Get sports display config from:
    - 'user_sports_preferences' if user is provided and a preference exists
    - otherwise from 'sports'

    'force_display_speed' allows to display speed in Workout list regardless
    sport preferences
    """
    from fittrackee.users.models import UserSportPreference

    sports_data_visibility = {}
    for sport in sports:
        sport_preferences = (
            UserSportPreference.query.filter_by(
                sport_id=sport.id, user_id=user.id
            ).first()
            if user
            else None
        )
        pace_speed_display = (
            sport_preferences.pace_speed_display
            if sport_preferences
            else sport.pace_speed_display
        )
        sports_data_visibility[sport.id] = SportDisplayedData(
            display_elevation=sport.label not in SPORTS_WITHOUT_ELEVATION_DATA,
            display_pace=pace_speed_display != PaceSpeedDisplay.SPEED,
            display_speed=force_display_speed
            or pace_speed_display != PaceSpeedDisplay.PACE,
            display_power=sport.label in POWER_SPORTS,
            display_cadence=sport.label in CADENCE_SPORTS,
            display_spm_cadence=sport.label in SPM_CADENCE_SPORTS,
            display_rpm_cadence=sport.label in RPM_CADENCE_SPORTS,
        )
    return sports_data_visibility


def get_sport_displayed_data(
    sport: "Sport", user: Optional["User"], force_display_speed: bool = False
) -> "SportDisplayedData":
    return get_sports_displayed_data([sport], user, force_display_speed)[
        sport.id
    ]


def get_pace(
    pace: Optional[timedelta], sport_data_visibility: "SportDisplayedData"
) -> Optional[str]:
    if pace is None or not sport_data_visibility.display_pace:
        return None

    return str(pace)


def get_speed(
    value: Union[float, Decimal, None],
    sport_data_visibility: "SportDisplayedData",
    pace: Optional[timedelta] = None,
) -> Optional[float]:
    if value is None:
        return None

    if (
        # in case pace is not yet calculated for workouts created
        # before 1.1.0
        sport_data_visibility.display_pace and pace is None
    ) or sport_data_visibility.display_speed:
        return float(value)

    return None


def get_elevation_data(
    value: Optional[float],
    can_see_analysis_data: bool,
    sport_data_visibility: "SportDisplayedData",
) -> Optional[float]:
    if (
        value is None
        or not can_see_analysis_data
        or not sport_data_visibility.display_elevation
    ):
        return None

    return float(value)


def get_cadence(
    cadence: Optional[int], sport_data_visibility: "SportDisplayedData"
) -> Optional[int]:
    if cadence is None:
        return None

    if sport_data_visibility.display_rpm_cadence:
        return cadence

    if sport_data_visibility.display_spm_cadence:
        return cadence * 2

    return None


def get_power(
    power: Optional[int], sport_data_visibility: "SportDisplayedData"
) -> Optional[int]:
    if power is None or not sport_data_visibility.display_power:
        return None

    return power

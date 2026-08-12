from datetime import timedelta
from typing import TYPE_CHECKING, Dict, List, Optional

import numpy as np
import pandas as pd

from ..utils.duration import remove_microseconds
from .sports import (
    get_cadence,
    get_elevation_data,
    get_pace,
    get_power,
    get_speed,
    get_sports_displayed_data,
)

if TYPE_CHECKING:
    from fittrackee.users.models import User

    from .sports import SportDisplayedData


def _agg_segments(serie: "pd.Series") -> "pd.Series":
    cols = {
        "duration": serie["duration"].sum(),
        "pauses": serie["pauses"].sum(),
        "moving": serie["moving"].sum(),
        "distance": serie["distance"].sum(),
        "min_alt": serie["min_alt"].min(),
        "max_alt": serie["max_alt"].max(),
        "descent": serie["descent"].sum(),
        "ascent": serie["ascent"].sum(),
        "max_speed": serie["max_speed"].max(),
        "ave_speed": serie["ave_speed"].mean(),
        "ave_cadence": serie["ave_cadence"].mean(),
        "max_cadence": serie["max_cadence"].max(),
        "ave_hr": serie["ave_hr"].mean(),
        "max_hr": serie["max_hr"].max(),
        "ave_power": serie["ave_power"].mean(),
        "max_power": serie["max_power"].max(),
        "ave_pace": serie["ave_pace"].mean(),
        "best_pace": serie["best_pace"].max(),
        "calories": serie["calories"].sum(),
    }
    return pd.Series(
        cols,
        index=list(cols.keys()),
    )


def convert_duration_to_string(value: Optional["timedelta"]) -> Optional[str]:
    if value is None:
        return None
    return str(remove_microseconds(timedelta(seconds=value.total_seconds())))


def convert_pace_duration_to_string(
    value: Optional["timedelta"], sport_data_visibility: "SportDisplayedData"
) -> Optional[str]:

    if value is None:
        return None

    return get_pace(
        remove_microseconds(timedelta(seconds=value.total_seconds())),
        sport_data_visibility,
    )


def get_segments_stats(
    totals: List[Dict],
    *,
    user: Optional["User"],
    can_see_analysis_data: bool,
    can_see_heart_rate: bool,
    can_see_calories: bool,
) -> Dict:
    if not totals:
        return {}

    from ..models import Sport

    sports_ids = [total["sport_id"] for total in totals]
    sports: List["Sport"] = Sport.query.filter(Sport.id.in_(sports_ids)).all()
    sports_displayed_data = get_sports_displayed_data(sports, user)

    df = pd.DataFrame(totals)
    df = df.groupby("sport_id").apply(_agg_segments)
    df["sport_id"] = df.index

    for key in ["duration", "pauses", "moving"]:
        df[key] = df[key].apply(convert_duration_to_string)
    for key in ["ave_speed", "max_speed"]:
        df[key] = df.apply(
            lambda x: get_speed(
                x[key],  # noqa:B023
                sport_data_visibility=sports_displayed_data[x["sport_id"]],
                pace=x["ave_pace" if key == "ave_speed" else "best_pace"],  # noqa:B023
            ),
            axis=1,
        )
    for key in ["min_alt", "max_alt"]:
        df[key] = df.apply(
            lambda x: get_elevation_data(
                x[key],  # noqa:B023
                can_see_analysis_data=can_see_analysis_data,
                sport_data_visibility=sports_displayed_data[x["sport_id"]],
            ),
            axis=1,
        )
    for key in ["ave_pace", "best_pace"]:
        df[key] = df.apply(
            lambda x: convert_pace_duration_to_string(
                x[key],  # noqa:B023
                sport_data_visibility=sports_displayed_data[x["sport_id"]],
            ),
            axis=1,
        )
    for key in ["ave_cadence", "max_cadence"]:
        df[key] = df.apply(
            lambda x: get_cadence(
                x[key],  # noqa:B023
                sport_data_visibility=sports_displayed_data[x["sport_id"]],
            ),
            axis=1,
        )
    for key in ["ave_power", "max_power"]:
        df[key] = df.apply(
            lambda x: get_power(
                x[key],  # noqa:B023
                sport_data_visibility=sports_displayed_data[x["sport_id"]],
            ),
            axis=1,
        )
    for key in ["ave_hr", "max_hr"]:
        df[key] = df[key].apply(
            lambda x: x if can_see_heart_rate else None,
        )
    if key == "calories":
        df[key] = df[key].apply(
            lambda x: x if can_see_calories else None,
        )

    df = df.replace({np.nan: None})
    for key in ["ave_hr", "ave_power", "ave_cadence"]:
        df[key] = df[key].apply(lambda x: None if x is None else round(x))

    return df.to_dict(orient="index")

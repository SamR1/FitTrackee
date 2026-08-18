from datetime import timedelta
from typing import TYPE_CHECKING, Dict, List

import pytest

from fittrackee.constants import PaceSpeedDisplay
from fittrackee.workouts.utils.segments import (
    convert_duration_to_string,
    get_segments_stats,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User, UserSportPreference
    from fittrackee.workouts.models import Sport


class TestConvertDurationToString:
    def test_it_returns_none_when_value_is_none(self) -> None:
        result = convert_duration_to_string(None)

        assert result is None

    @pytest.mark.parametrize(
        "input_seconds,input_ms,expected_result",
        [
            (0, 0, "0:00:00"),
            (3754, 1, "1:02:34"),
        ],
    )
    def test_it_converts_duration_into_string(
        self, input_seconds: int, input_ms: int, expected_result: str
    ) -> None:
        result = convert_duration_to_string(
            timedelta(seconds=input_seconds, microseconds=input_ms)
        )

        assert result == expected_result


class TestGetSegmentsStats:
    def test_it_returns_empty_dict_when_no_totals(self, app: "Flask") -> None:
        stats = get_segments_stats(
            totals=[],
            user=None,
            can_see_analysis_data=False,
            can_see_heart_rate=False,
            can_see_calories=False,
        )

        assert stats == {}

    def test_it_returns_stats_when_user_is_none_and_all_flags_are_none(
        self,
        app: "Flask",
        sport_8_trail: "Sport",
        sport_9_open_water_swimming: "Sport",
        multi_sports_totals: List[Dict],
    ) -> None:
        stats = get_segments_stats(
            totals=multi_sports_totals,
            user=None,
            can_see_analysis_data=False,
            can_see_heart_rate=False,
            can_see_calories=False,
        )
        assert stats == {
            sport_8_trail.id: {
                "duration": "0:33:19",
                "pauses": "0:00:48",
                "moving": "0:32:30",
                "distance": 5.134,
                "min_alt": None,
                "max_alt": None,
                "descent": 25.0,
                "ascent": 30.0,
                "max_speed": None,
                "ave_speed": None,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": None,
                "max_hr": None,
                "ave_power": None,
                "max_power": None,
                "ave_pace": "0:06:19",
                "best_pace": "0:05:39",
                "calories": 299,
                "sport_id": sport_8_trail.id,
            },
            sport_9_open_water_swimming.id: {
                "duration": "0:09:09",
                "pauses": "0:00:00",
                "moving": "0:09:09",
                "distance": 0.451,
                "min_alt": None,
                "max_alt": None,
                "descent": 0.0,
                "ascent": 0.0,
                "max_speed": 4.86,
                "ave_speed": 2.96,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": None,
                "max_hr": None,
                "ave_power": None,
                "max_power": None,
                "ave_pace": None,
                "best_pace": None,
                "calories": 125,
                "sport_id": sport_9_open_water_swimming.id,
            },
        }

    def test_it_returns_stats_when_user_is_provided_and_all_flags_are_true(
        self,
        app: "Flask",
        sport_8_trail: "Sport",
        sport_9_open_water_swimming: "Sport",
        user_1: "User",
        multi_sports_totals: List[Dict],
    ) -> None:
        stats = get_segments_stats(
            totals=multi_sports_totals,
            user=user_1,
            can_see_analysis_data=True,
            can_see_heart_rate=True,
            can_see_calories=True,
        )
        assert stats == {
            sport_8_trail.id: {
                "duration": "0:33:19",
                "pauses": "0:00:48",
                "moving": "0:32:30",
                "distance": 5.134,
                "min_alt": 6.8,
                "max_alt": 19.0,
                "descent": 25.0,
                "ascent": 30.0,
                "max_speed": None,
                "ave_speed": None,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": 162,
                "max_hr": 173,
                "ave_power": None,
                "max_power": None,
                "ave_pace": "0:06:19",
                "best_pace": "0:05:39",
                "calories": 299,
                "sport_id": sport_8_trail.id,
            },
            sport_9_open_water_swimming.id: {
                "duration": "0:09:09",
                "pauses": "0:00:00",
                "moving": "0:09:09",
                "distance": 0.451,
                "min_alt": None,
                "max_alt": None,
                "descent": 0.0,
                "ascent": 0.0,
                "max_speed": 4.86,
                "ave_speed": 2.96,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": 136,
                "max_hr": 160,
                "ave_power": None,
                "max_power": None,
                "ave_pace": None,
                "best_pace": None,
                "calories": 125,
                "sport_id": sport_9_open_water_swimming.id,
            },
        }

    def test_it_returns_stats_when_sport_preferences_allows_returns_pace_and_speed(  # noqa
        self,
        app: "Flask",
        sport_8_trail: "Sport",
        sport_9_open_water_swimming: "Sport",
        user_1_sport_8_preference: "UserSportPreference",
        user_1: "User",
        multi_sports_totals: List[Dict],
    ) -> None:
        user_1_sport_8_preference.pace_speed_display = (
            PaceSpeedDisplay.PACE_AND_SPEED
        )
        stats = get_segments_stats(
            totals=multi_sports_totals,
            user=user_1,
            can_see_analysis_data=True,
            can_see_heart_rate=True,
            can_see_calories=True,
        )
        assert stats == {
            sport_8_trail.id: {
                "duration": "0:33:19",
                "pauses": "0:00:48",
                "moving": "0:32:30",
                "distance": 5.134,
                "min_alt": 6.8,
                "max_alt": 19.0,
                "descent": 25.0,
                "ascent": 30.0,
                "max_speed": 11.59,
                "ave_speed": 9.504999999999999,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": 162,
                "max_hr": 173,
                "ave_power": None,
                "max_power": None,
                "ave_pace": "0:06:19",
                "best_pace": "0:05:39",
                "calories": 299,
                "sport_id": sport_8_trail.id,
            },
            sport_9_open_water_swimming.id: {
                "duration": "0:09:09",
                "pauses": "0:00:00",
                "moving": "0:09:09",
                "distance": 0.451,
                "min_alt": None,
                "max_alt": None,
                "descent": 0.0,
                "ascent": 0.0,
                "max_speed": 4.86,
                "ave_speed": 2.96,
                "ave_cadence": None,
                "max_cadence": None,
                "ave_hr": 136,
                "max_hr": 160,
                "ave_power": None,
                "max_power": None,
                "ave_pace": None,
                "best_pace": None,
                "calories": 125,
                "sport_id": sport_9_open_water_swimming.id,
            },
        }

from datetime import timedelta
from typing import Optional

import pytest

from fittrackee.workouts.exceptions import InvalidDurationException
from fittrackee.workouts.utils.convert import (
    convert_in_duration,
    convert_pace_in_duration,
    convert_speed_into_pace_duration,
    convert_speed_into_pace_in_sec_per_meter,
    convert_value_to_integer,
)


class TestConvertInDuration:
    def test_it_raises_exception_format_is_invalid(self) -> None:
        with pytest.raises(InvalidDurationException, match="invalid duration"):
            convert_in_duration("00h01m")

    @pytest.mark.parametrize(
        "input_value,expected_seconds",
        [
            ("00:01", 60),
            ("00:01:00", 60),
            ("01:00", 3600),
            ("00:00", 0),
        ],
    )
    def test_it_converts_str_into_time_delta(
        self, input_value: str, expected_seconds: int
    ) -> None:
        assert convert_in_duration(input_value) == timedelta(
            seconds=expected_seconds
        )


class TestConvertValueToInteger:
    @pytest.mark.parametrize("input_record", ["AS", "FD", "LD", "MS"])
    def test_it_returns_none_when_value_is_none(
        self, input_record: str
    ) -> None:
        assert convert_value_to_integer("LD", None) is None

    def test_it_returns_none_when_input_record_in_invalid(self) -> None:
        assert convert_value_to_integer("invalid", 100) is None

    @pytest.mark.parametrize(
        "input_value,expected_value",
        [
            (timedelta(minutes=2), 120),
            (timedelta(days=2), 172800),
        ],
    )
    def test_it_returns_seconds_for_longest_duration(
        self, input_value: "timedelta", expected_value: "timedelta"
    ) -> None:
        assert convert_value_to_integer("LD", input_value) == expected_value

    @pytest.mark.parametrize(
        "input_record,input_value,expected_value",
        [
            ("AS", 3.5, 350),
            ("MS", 20.0, 2000),
            ("FD", 3.456, 3456),
        ],
    )
    def test_it_returns_integer_for_record_different_than_longest_duration(
        self,
        input_record: str,
        input_value: "timedelta",
        expected_value: "timedelta",
    ) -> None:
        assert (
            convert_value_to_integer(input_record, input_value)
            == expected_value
        )


class TestConvertSpeedIntoPaceDuration:
    @pytest.mark.parametrize(
        "input_speed,expected_pace",
        [
            (None, None),
            (0.0, timedelta()),
            (3.6, timedelta(minutes=16, seconds=40)),
            (5.0, timedelta(minutes=12)),
            (11.3, timedelta(minutes=5, seconds=19)),
        ],
    )
    def test_it_converts_speed_in_pace(
        self, input_speed: Optional[float], expected_pace: Optional[timedelta]
    ) -> None:
        assert convert_speed_into_pace_duration(input_speed) == expected_pace


class TestConvertSpeedIntoPaceSeconds:
    def test_it_returns_none_when_speed_is_none(self) -> None:
        assert convert_speed_into_pace_in_sec_per_meter(speed=None) is None

    @pytest.mark.parametrize(
        "input_speed,expected_pace",
        [
            (0.0, 0.0),
            (3.6, 1.0),
            (5.0, 0.72),
            (11.3, 0.3185840708),
        ],
    )
    def test_it_converts_speed_in_pace(
        self, input_speed: float, expected_pace: float
    ) -> None:
        assert (
            convert_speed_into_pace_in_sec_per_meter(input_speed)  # type: ignore[arg-type]
            == expected_pace
        )


class TestConvertPaceInDuration:
    @pytest.mark.parametrize(
        "input_pace",
        [
            "",
            "01:12:00",
            "09:60",
        ],
    )
    def test_it_raises_exception_when_pace_format_is_invalid(
        self, input_pace: str
    ) -> None:
        with pytest.raises(InvalidDurationException):
            convert_pace_in_duration(input_pace)

    @pytest.mark.parametrize(
        "input_pace, expected_duration_in_seconds",
        [
            ("00:00", 0),
            ("01:00", 60),
            ("90:10", 5410),
        ],
    )
    def test_it_returns_pace_in_duration(
        self, input_pace: str, expected_duration_in_seconds: int
    ) -> None:
        assert convert_pace_in_duration(input_pace) == timedelta(
            seconds=expected_duration_in_seconds
        )

from datetime import timedelta

import pytest

from fittrackee.workouts.exceptions import InvalidDurationException
from fittrackee.workouts.utils.convert import (
    convert_in_duration,
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

from datetime import timedelta

import pytest

from fittrackee.workouts.utils.convert import convert_value_to_integer


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

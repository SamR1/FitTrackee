from datetime import datetime, timezone
from typing import Dict
from unittest.mock import Mock, patch, sentinel

import pytest
import pytz
import requests

from fittrackee.dates import get_datetime_in_utc
from fittrackee.tests.mixins import BaseTestMixin
from fittrackee.tests.utils import random_string
from fittrackee.workouts.services.weather.visual_crossing import VisualCrossing
from fittrackee.workouts.services.weather.weather_service import WeatherService
from fittrackee.workouts.services.workout_from_file.workout_point import (
    WorkoutPoint,
)

from ...mixins import ResponseMockMixin

VISUAL_CROSSING_RESPONSE = {
    "queryCost": 1,
    "latitude": 48.866667,
    "longitude": 2.333333,
    "resolvedAddress": "48.866667,2.333333",
    "address": "48.866667,2.333333",
    "timezone": "Europe/Paris",
    "tzoffset": 1.0,
    "days": [
        {
            "datetime": "2022-11-15",
            "datetimeEpoch": 1668466800,
            "temp": 10.4,
            "humidity": 93.3,
            "windspeed": 18.9,
            "winddir": 179.4,
            "conditions": "Rain, Partially cloudy",
            "description": "Partly cloudy throughout the day with rain.",
            "icon": "rain",
        }
    ],
    "currentConditions": {
        "datetime": "13:00:00",
        "datetimeEpoch": 1668513600,
        "temp": 11.3,
        "humidity": 93.1,
        "windspeed": 14.0,
        "winddir": 161.9,
        "conditions": "Rain, Overcast",
        "icon": "rain",
    },
}


class WeatherTestCase(BaseTestMixin):
    api_key = random_string()

    @staticmethod
    def get_gpx_point(time: datetime) -> WorkoutPoint:
        return WorkoutPoint(latitude=48.866667, longitude=2.333333, time=time)


class TestVisualCrossingGetTimestamp(WeatherTestCase):
    def test_it_returns_expected_timestamp_as_integer(self) -> None:
        time = datetime.now(timezone.utc)
        visual_crossing = VisualCrossing(api_key=self.api_key)

        timestamp = visual_crossing._get_timestamp(time)

        assert isinstance(timestamp, int)

    @pytest.mark.parametrize(
        "input_datetime,expected_datetime",
        [
            ("2020-12-15T13:00:00", "2020-12-15T13:00:00"),
            ("2020-12-15T13:29:59", "2020-12-15T13:00:00"),
            ("2020-12-15T13:30:00", "2020-12-15T14:00:00"),
            ("2020-12-15T13:59:59", "2020-12-15T14:00:00"),
        ],
    )
    def test_it_returns_rounded_time(
        self, input_datetime: str, expected_datetime: str
    ) -> None:
        date_format = "%Y-%m-%dT%H:%M:%S"
        time = get_datetime_in_utc(input_datetime, date_format)
        visual_crossing = VisualCrossing(api_key=self.api_key)

        timestamp = visual_crossing._get_timestamp(time)

        assert (
            timestamp
            == get_datetime_in_utc(expected_datetime, date_format).timestamp()
        )


class TestVisualCrossingGetWeather(WeatherTestCase, ResponseMockMixin):
    def test_it_calls_api_with_time_and_point_location(self) -> None:
        time = datetime(
            year=2022,
            month=11,
            day=15,
            hour=12,
            minute=00,
            second=00,
            tzinfo=pytz.utc,
        )
        point = self.get_gpx_point(time)
        visual_crossing = VisualCrossing(api_key=self.api_key)
        with patch.object(requests, "get") as get_mock:
            visual_crossing.get_weather(point)

        args = self.get_args(get_mock.call_args)
        assert args[0] == (
            "https://weather.visualcrossing.com/VisualCrossingWebServices/"
            f"rest/services/timeline/{point.latitude},{point.longitude}/"
            f"{int(point.time.timestamp())}"  # type: ignore
        )

    def test_it_calls_api_with_expected_params(self) -> None:
        visual_crossing = VisualCrossing(api_key=self.api_key)
        with patch.object(requests, "get") as get_mock:
            visual_crossing.get_weather(
                self.get_gpx_point(datetime.now(timezone.utc))
            )

        kwargs = self.get_kwargs(get_mock.call_args)
        assert kwargs.get("params") == {
            "key": self.api_key,
            "iconSet": "icons1",
            "unitGroup": "metric",
            "contentType": "json",
            "elements": (
                "datetime,datetimeEpoch,temp,humidity,windspeed,"
                "winddir,conditions,description,icon"
            ),
            "include": "current",
        }

    def test_it_returns_data_from_current_conditions(self) -> None:
        point = self.get_gpx_point(
            datetime(
                year=2022,
                month=11,
                day=15,
                hour=13,
                minute=00,
                second=00,
                tzinfo=pytz.utc,
            ).astimezone(pytz.timezone("Europe/Paris"))
        )
        visual_crossing = VisualCrossing(api_key=self.api_key)
        with patch.object(
            requests,
            "get",
            return_value=self.get_response(VISUAL_CROSSING_RESPONSE),
        ):
            weather_data = visual_crossing.get_weather(point)

        current_conditions: Dict = VISUAL_CROSSING_RESPONSE[  # type: ignore
            "currentConditions"
        ]
        assert weather_data == {
            "icon": current_conditions["icon"],
            "temperature": current_conditions["temp"],
            "humidity": current_conditions["humidity"] / 100,
            "wind": (current_conditions["windspeed"] * 1000) / 3600,
            "windBearing": current_conditions["winddir"],
        }


class TestWeatherService(WeatherTestCase):
    @pytest.mark.parametrize(
        "input_api_key,input_provider",
        [
            ("", "visualcrossing"),
            ("valid_api_key", ""),
            ("valid_api_key", "invalid_provider"),
            ("valid_api_key", "darksky"),  # removed provider
        ],
    )
    def test_weather_api_is_none_when_configuration_is_invalid(
        self,
        monkeypatch: pytest.MonkeyPatch,
        input_api_key: str,
        input_provider: str,
    ) -> None:
        monkeypatch.setenv("WEATHER_API_KEY", input_api_key)
        monkeypatch.setenv("WEATHER_API_PROVIDER", input_provider)

        weather_service = WeatherService()

        assert weather_service.weather_api is None

    @pytest.mark.parametrize(
        "input_provider",
        ["visualcrossing", "VisualCrossing"],
    )
    def test_weather_api_is_visualcrossing_when_configured(
        self,
        monkeypatch: pytest.MonkeyPatch,
        input_provider: str,
    ) -> None:
        monkeypatch.setenv("WEATHER_API_KEY", "valid_api_key")
        monkeypatch.setenv("WEATHER_API_PROVIDER", input_provider)

        weather_service = WeatherService()

        assert isinstance(weather_service.weather_api, VisualCrossing)

    def test_it_returns_none_when_no_weather_api(self) -> None:
        weather_service = WeatherService()
        weather_service.weather_api = None
        point = self.get_gpx_point(datetime.now(timezone.utc))

        weather_data = weather_service.get_weather(point)

        assert weather_data is None

    def test_it_returns_none_when_weather_api_raises_exception(self) -> None:
        weather_api = Mock()
        weather_api.get_weather = Mock()
        weather_api.get_weather.side_effect = Exception()
        weather_service = WeatherService()
        weather_service.weather_api = weather_api
        point = self.get_gpx_point(datetime.now(timezone.utc))

        weather_data = weather_service.get_weather(point)

        assert weather_data is None

    def test_it_returns_weather_data(self) -> None:
        weather_api = Mock()
        weather_api.get_weather = Mock()
        weather_api.get_weather.return_value = sentinel
        weather_service = WeatherService()
        weather_service.weather_api = weather_api
        point = self.get_gpx_point(datetime.now(timezone.utc))

        weather_data = weather_service.get_weather(point)

        assert weather_data == sentinel

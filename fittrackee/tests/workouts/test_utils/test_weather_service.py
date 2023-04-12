from datetime import datetime
from typing import Dict, Optional
from unittest.mock import Mock, patch, sentinel

import pytest
import pytz
import requests
from gpxpy.gpx import GPXTrackPoint

from fittrackee.tests.mixins import CallArgsMixin
from fittrackee.tests.utils import random_string
from fittrackee.workouts.utils.weather.visual_crossing import VisualCrossing
from fittrackee.workouts.utils.weather.weather_service import WeatherService

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


class WeatherTestCase:
    api_key = random_string()

    @staticmethod
    def get_gpx_point(time: Optional[datetime] = None) -> GPXTrackPoint:
        return GPXTrackPoint(latitude=48.866667, longitude=2.333333, time=time)


class TestVisualCrossingGetTimestamp(WeatherTestCase):
    def test_it_returns_expected_timestamp_as_integer(self) -> None:
        time = datetime.utcnow()
        visual_crossing = VisualCrossing(api_key=self.api_key)

        timestamp = visual_crossing._get_timestamp(time)

        assert isinstance(timestamp, int)

    @pytest.mark.parametrize(
        'input_datetime,expected_datetime',
        [
            ('2020-12-15T13:00:00', '2020-12-15T13:00:00'),
            ('2020-12-15T13:29:59', '2020-12-15T13:00:00'),
            ('2020-12-15T13:30:00', '2020-12-15T14:00:00'),
            ('2020-12-15T13:59:59', '2020-12-15T14:00:00'),
        ],
    )
    def test_it_returns_rounded_time(
        self, input_datetime: str, expected_datetime: str
    ) -> None:
        time = datetime.strptime(input_datetime, '%Y-%m-%dT%H:%M:%S')
        visual_crossing = VisualCrossing(api_key=self.api_key)

        timestamp = visual_crossing._get_timestamp(time)

        assert (
            timestamp
            == datetime.strptime(
                expected_datetime, '%Y-%m-%dT%H:%M:%S'
            ).timestamp()
        )


class TestVisualCrossingGetWeather(WeatherTestCase, CallArgsMixin):
    @staticmethod
    def get_response() -> Mock:
        response_mock = Mock()
        response_mock.raise_for_status = Mock()
        response_mock.json = Mock()
        response_mock.json.return_value = VISUAL_CROSSING_RESPONSE
        return response_mock

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
        with patch.object(requests, 'get') as get_mock:
            visual_crossing.get_weather(point)

        args = self.get_args(get_mock.call_args)
        assert args[0] == (
            'https://weather.visualcrossing.com/VisualCrossingWebServices/'
            f'rest/services/timeline/{point.latitude},{point.longitude}/'
            f'{int(point.time.timestamp())}'  # type: ignore
        )

    def test_it_calls_api_with_expected_params(self) -> None:
        visual_crossing = VisualCrossing(api_key=self.api_key)
        with patch.object(requests, 'get') as get_mock:
            visual_crossing.get_weather(self.get_gpx_point(datetime.utcnow()))

        kwargs = self.get_kwargs(get_mock.call_args)
        assert kwargs.get('params') == {
            'key': self.api_key,
            'iconSet': 'icons1',
            'unitGroup': 'metric',
            'contentType': 'json',
            'elements': (
                'datetime,datetimeEpoch,temp,humidity,windspeed,'
                'winddir,conditions,description,icon'
            ),
            'include': 'current',
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
            ).astimezone(pytz.timezone('Europe/Paris'))
        )
        visual_crossing = VisualCrossing(api_key=self.api_key)
        with patch.object(requests, 'get', return_value=self.get_response()):
            weather_data = visual_crossing.get_weather(point)

        current_conditions: Dict = VISUAL_CROSSING_RESPONSE[  # type: ignore
            'currentConditions'
        ]
        assert weather_data == {
            'icon': current_conditions['icon'],
            'temperature': current_conditions['temp'],
            'humidity': current_conditions['humidity'] / 100,
            'wind': (current_conditions['windspeed'] * 1000) / 3600,
            'windBearing': current_conditions['winddir'],
        }


class TestWeatherService(WeatherTestCase):
    @pytest.mark.parametrize(
        'input_api_key,input_provider',
        [
            ('', 'visualcrossing'),
            ('valid_api_key', ''),
            ('valid_api_key', 'invalid_provider'),
            ('valid_api_key', 'darksky'),  # removed provider
        ],
    )
    def test_weather_api_is_none_when_configuration_is_invalid(
        self,
        monkeypatch: pytest.MonkeyPatch,
        input_api_key: str,
        input_provider: str,
    ) -> None:
        monkeypatch.setenv('WEATHER_API_KEY', input_api_key)
        monkeypatch.setenv('WEATHER_API_PROVIDER', input_provider)

        weather_service = WeatherService()

        assert weather_service.weather_api is None

    @pytest.mark.parametrize(
        'input_provider',
        ['visualcrossing', 'VisualCrossing'],
    )
    def test_weather_api_is_visualcrossing_when_configured(
        self,
        monkeypatch: pytest.MonkeyPatch,
        input_provider: str,
    ) -> None:
        monkeypatch.setenv('WEATHER_API_KEY', 'valid_api_key')
        monkeypatch.setenv('WEATHER_API_PROVIDER', input_provider)

        weather_service = WeatherService()

        assert isinstance(weather_service.weather_api, VisualCrossing)

    def test_it_returns_none_when_no_weather_api(self) -> None:
        weather_service = WeatherService()
        weather_service.weather_api = None
        point = self.get_gpx_point(datetime.utcnow())

        weather_data = weather_service.get_weather(point)

        assert weather_data is None

    def test_it_returns_none_when_point_time_is_none(self) -> None:
        weather_service = WeatherService()
        weather_service.weather_api = VisualCrossing('api_key')
        point = self.get_gpx_point(None)

        weather_data = weather_service.get_weather(point)

        assert weather_data is None

    def test_it_returns_none_when_weather_api_raises_exception(self) -> None:
        weather_api = Mock()
        weather_api.get_weather = Mock()
        weather_api.get_weather.side_effect = Exception()
        weather_service = WeatherService()
        weather_service.weather_api = weather_api
        point = self.get_gpx_point(datetime.utcnow())

        weather_data = weather_service.get_weather(point)

        assert weather_data is None

    def test_it_returns_weather_data(self) -> None:
        weather_api = Mock()
        weather_api.get_weather = Mock()
        weather_api.get_weather.return_value = sentinel
        weather_service = WeatherService()
        weather_service.weather_api = weather_api
        point = self.get_gpx_point(datetime.utcnow())

        weather_data = weather_service.get_weather(point)

        assert weather_data == sentinel

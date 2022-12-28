from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional

from gpxpy.gpx import GPXTrackPoint


class BaseWeather(ABC):
    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key

    @abstractmethod
    def _get_data(
        self, latitude: float, longitude: float, time: datetime
    ) -> Optional[Dict]:
        # Expected dict:
        # {
        #     "humidity": 0.69,
        #     "icon": "partly-cloudy-day",
        #     "temperature": 12.26,
        #     "wind": 3.49,
        #     "windBearing": 315
        # }
        #
        # FitTrackee expects the following units:
        #   temperature: Celsius,
        #   humidity: in fraction (rather than percent)
        #   windSpeed: m/s
        #   windBearing: direction wind is from in degrees (0 is north)
        #
        # Expected icon values (for UI):
        # - "clear-day",
        # - "clear-night",
        # - "cloudy",
        # - "fog",
        # - "partly-cloudy-day",
        # - "partly-cloudy-night",
        # - "rain",
        # - "sleet",
        # - "snow",
        # - "wind"
        pass

    def get_weather(self, point: GPXTrackPoint) -> Optional[Dict]:
        if not point.time:
            # if there's no time associated with the point,
            # we cannot get weather
            return None

        return self._get_data(point.latitude, point.longitude, point.time)

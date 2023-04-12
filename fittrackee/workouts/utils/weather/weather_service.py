import os
from typing import Dict, Optional, Union

from gpxpy.gpx import GPXTrackPoint

from fittrackee import appLog

from .visual_crossing import VisualCrossing


class WeatherService:
    """
    Available API:
    - VisualCrossing
    """

    def __init__(self) -> None:
        self.weather_api = self._get_weather_api()

    @staticmethod
    def _get_weather_api() -> Union[VisualCrossing, None]:
        weather_api_key: str = os.getenv('WEATHER_API_KEY', '')
        weather_api_provider: str = os.getenv(
            'WEATHER_API_PROVIDER', ''
        ).lower()

        if not weather_api_key:
            return None
        if weather_api_provider == 'visualcrossing':
            return VisualCrossing(weather_api_key)
        return None

    def get_weather(self, point: GPXTrackPoint) -> Optional[Dict]:
        if not self.weather_api:
            return None
        try:
            return self.weather_api.get_weather(point)
        except Exception as e:
            appLog.error(f'error when getting weather data: {e}')
            return None

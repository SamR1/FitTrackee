import os
from typing import Dict, Optional, Union

from gpxpy.gpx import GPXTrackPoint

from fittrackee import appLog

from .dark_sky import DarkSky
from .visual_crossing import VisualCrossing


class WeatherService:
    """
    Available API:
    - DarkSky (deprecated, will end on March 31st, 2023)
    - VisualCrossing
    """

    def __init__(self) -> None:
        self.weather_api = self._get_weather_api()

    @staticmethod
    def _get_weather_api() -> Union[DarkSky, VisualCrossing, None]:
        weather_api_key: str = os.getenv('WEATHER_API_KEY', '')
        weather_api_provider: str = os.getenv(
            'WEATHER_API_PROVIDER', ''
        ).lower()

        if not weather_api_key:
            return None
        if weather_api_provider == 'darksky':  # deprecated
            return DarkSky(weather_api_key)
        if weather_api_provider == 'visualcrossing':
            return VisualCrossing(weather_api_key)
        return None

    def get_weather(self, point: GPXTrackPoint) -> Optional[Dict]:
        if not self.weather_api:
            return None
        try:
            return self.weather_api.get_weather(point)
        except Exception as e:
            appLog.error(e)
            return None

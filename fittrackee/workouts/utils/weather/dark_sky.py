from datetime import datetime
from typing import Dict, Optional

import forecastio
import pytz

from .base_weather import BaseWeather


class DarkSky(BaseWeather):
    # Deprecated (API will end on March 31st, 2023)

    def _get_data(
        self, latitude: float, longitude: float, time: datetime
    ) -> Optional[Dict]:
        # get point time in UTC
        point_time = (
            pytz.utc.localize(time)
            if time.tzinfo is None  # naive datetime
            else time
        )

        forecast = forecastio.load_forecast(
            self.api_key,
            latitude,
            longitude,
            time=point_time,
            units='si',
        )
        weather = forecast.currently()
        return {
            'humidity': weather.humidity,
            'icon': weather.icon,
            'temperature': weather.temperature,
            'wind': weather.windSpeed,
            'windBearing': weather.windBearing,
        }

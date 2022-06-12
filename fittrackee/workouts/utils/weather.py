import os
from typing import Dict, Optional

import forecastio
import pytz
from gpxpy.gpx import GPXTrackPoint

from fittrackee import appLog

API_KEY = os.getenv('WEATHER_API_KEY')


def get_weather(point: GPXTrackPoint) -> Optional[Dict]:
    if not API_KEY or not point.time:
        return None
    try:
        point_time = (
            pytz.utc.localize(point.time)
            if point.time.tzinfo is None
            else point.time.astimezone(pytz.utc)
        )
        forecast = forecastio.load_forecast(
            API_KEY,
            point.latitude,
            point.longitude,
            time=point_time,
            units='si',
        )
        weather = forecast.currently()
        return {
            'summary': weather.summary,
            'icon': weather.icon,
            'temperature': weather.temperature,
            'humidity': weather.humidity,
            'wind': weather.windSpeed,
            'windBearing': weather.windBearing,
        }
    except Exception as e:
        appLog.error(e)
        return None

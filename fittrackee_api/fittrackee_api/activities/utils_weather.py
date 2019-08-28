import os

import forecastio
import pytz
from fittrackee_api import appLog

API_KEY = os.getenv('WEATHER_API')


def get_weather(point):
    if not API_KEY or API_KEY == '':
        return None
    try:
        point_time = pytz.utc.localize(point.time)
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
        }
    except Exception as e:
        appLog.error(e)
        return None

import os
from typing import Dict, Optional, Union

import forecastio
import requests
import pytz
from datetime import datetime, timedelta
from gpxpy.gpx import GPXTrackPoint

from fittrackee import appLog

API_KEY = os.getenv('WEATHER_API_KEY')
VC_API_KEY = os.getenv('VC_WEATHER_API_KEY')


def get_weather(point: GPXTrackPoint) -> Optional[Dict]:
    try:
        if not point.time:
            # if there's no time associated with the point; we cannot get weather
            return None
        else:
            point_time = (
                pytz.utc.localize(point.time)
                if point.time.tzinfo is None
                else point.time.astimezone(pytz.utc)
            )
            if API_KEY:
                # if darksky api key is present, use that
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
            elif VC_API_KEY:
                # if visualcrossing API key is present, use that
                return get_visual_crossing_weather(VC_API_KEY, point.latitude, 
                                                   point.longitude, point.time)
            else:
                return None

    except Exception as e:
        appLog.error(e)
        return None


def get_visual_crossing_weather(api_key: str, 
                                latitude: float, 
                                longitude: float, 
                                time: datetime) -> Dict[str, Union[str, float]]:
    # All requests to the Timeline Weather API use the following the form:

    # https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services
    # /timeline/[location]/[date1]/[date2]?key=YOUR_API_KEY 

    # location (required) – is the address, partial address or latitude,longitude location for 
    # which to retrieve weather data. You can also use US ZIP Codes.

    # date1 (optional) – is the start date for which to retrieve weather data. 
    # You can also request the information for a specific time for a single date by 
    # including time into the date1 field using the format yyyy-MM-ddTHH:mm:ss. 
    # For example 2020-10-19T13:00:00.

    # The results are returned in the ‘currentConditions’ field and are truncated to the 
    # hour requested (i.e. 2020-10-19T13:59:00 will return data at 2020-10-19T13:00:00).
    
    # first, round datetime to nearest hour by truncating, and then adding an hour if
    # the "real" time's number of minutes is 30 or more (we do this since the API only truncates)
    trunc_time = (time.replace(second=0, microsecond=0, minute=0, hour=time.hour) + 
        timedelta(hours=time.minute//30))
    appLog.debug(f'VC_weather: truncated time {time} ({time.timestamp()}) to '
                 f'{trunc_time} ({trunc_time.timestamp()})')

    base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services'
    url = f"{base_url}/timeline/{latitude},{longitude}/{int(trunc_time.timestamp())}?key={api_key}"
    params = {
        "unitGroup": "metric", 
        "contentType": "json", 
        "elements": "datetime,datetimeEpoch,temp,humidity,windspeed,winddir,conditions,description,icon",
        "include": "current"
    }
    appLog.debug(f'VC_weather: getting weather from {url}'.replace(api_key, '*****'))
    r = requests.get(url, params=params)
    r.raise_for_status()
    res = r.json()
    weather = res['currentConditions']
    # FitTrackee expects the following units:
    #   temp: Celsius, 
    #   humidity: in fraction (rather than percent)
    #   windSpeed: m/s
    #   windBearing: direction wind is from in degrees (0 is north)
    # VC provides humidity in percent, wind in km/h
    data =  {
        'summary': weather['conditions'],
        'icon': f"vc-{weather['icon']}",
        'temperature': weather['temp'],
        'humidity': weather['humidity'] / 100,
        'wind': weather['windspeed'] * 1000 / (60 * 60), # km/h to m/s
        'windBearing': weather['winddir'],
    }
    return data

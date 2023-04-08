from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

from fittrackee import appLog

from .base_weather import BaseWeather


class VisualCrossing(BaseWeather):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = (
            'https://weather.visualcrossing.com/'
            'VisualCrossingWebServices/rest/services'
        )
        self.params = {
            "key": self.api_key,
            "iconSet": "icons1",  # default value, same as Darksky
            "unitGroup": "metric",
            "contentType": "json",
            "elements": (
                "datetime,datetimeEpoch,temp,humidity,windspeed,"
                "winddir,conditions,description,icon"
            ),
            "include": "current",  # to get only specific time data
        }

    @staticmethod
    def _get_timestamp(time: datetime) -> int:
        # The results are returned in the ‘currentConditions’ field and are
        # truncated to the hour requested (i.e. 2020-10-19T13:59:00 will return
        # data at 2020-10-19T13:00:00).

        # first, round datetime to nearest hour by truncating, and then adding
        # an hour if the "real" time's number of minutes is 30 or more (we do
        # this since the API only truncates)
        trunc_time = time.replace(
            second=0, microsecond=0, minute=0, hour=time.hour
        ) + timedelta(hours=time.minute // 30)
        appLog.debug(
            f'VC_weather: truncated time {time} ({time.timestamp()})'
            f' to {trunc_time} ({trunc_time.timestamp()})'
        )
        return int(trunc_time.timestamp())

    def _get_data(
        self, latitude: float, longitude: float, time: datetime
    ) -> Optional[Dict]:
        # All requests to the Timeline Weather API use the following the form:

        # https://weather.visualcrossing.com/VisualCrossingWebServices/rest
        # /services/timeline/[location]/[date1]/[date2]?key=YOUR_API_KEY

        # location (required) – is the address, partial address or
        # latitude,longitude location for
        # which to retrieve weather data. You can also use US ZIP Codes.

        # date1 (optional) – is the start date for which to retrieve weather
        # data. All dates and times are in local time of the **location**
        # specified.
        url = (
            f"{self.base_url}/timeline/{latitude},{longitude}"
            f"/{self._get_timestamp(time)}"
        )
        appLog.debug(
            f'VC_weather: getting weather from {url}'.replace(
                self.api_key, '*****'
            )
        )
        r = requests.get(url, params=self.params, timeout=10)
        r.raise_for_status()
        res = r.json()
        weather = res['currentConditions']

        data = {
            'icon': weather['icon'],
            'temperature': weather['temp'],
            'humidity': weather['humidity'] / 100,
            'wind': weather['windspeed'] * 1000 / (60 * 60),  # km/h to m/s
            'windBearing': weather['winddir'],
        }
        return data

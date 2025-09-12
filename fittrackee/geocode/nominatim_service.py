import os
from typing import Dict, List

import requests

from fittrackee import VERSION, appLog
from fittrackee.utils import TimedLRUCache


class NominatimService:
    """
    documentation:
    https://nominatim.org/release-docs/develop/api/Overview/
    """

    def __init__(self) -> None:
        self.base_url = os.environ.get(
            "NOMINATIM_URL", "https://nominatim.openstreetmap.org"
        )
        self.params = {"format": "jsonv2"}
        self.headers = {"User-Agent": f"FitTrackee v{VERSION}"}

    @TimedLRUCache(seconds=1800)  # 30 minutes
    def get_locations_from_city(self, city: str) -> List[Dict]:
        url = f"{self.base_url}/search"
        appLog.debug(f"Nominatim: getting location for query: '{city}'")
        r = requests.get(
            url,
            params={**self.params, "city": city},
            timeout=30,
            headers=self.headers,
        )
        r.raise_for_status()
        locations = r.json()

        return [
            {
                "coordinates": f"{location['lat']},{location['lon']}",
                "display_name": location["display_name"],
                "name": location["name"],
                "addresstype": location["addresstype"],
                "osm_id": f"{location['osm_type'][0]}{location['osm_id']}",
            }
            for location in locations
        ]

    @TimedLRUCache(seconds=1800)  # 30 minutes
    def get_location_from_id(self, osm_id: str) -> Dict:
        url = f"{self.base_url}/lookup"
        appLog.debug(f"Nominatim: getting location for id: '{osm_id}'")
        r = requests.get(
            url,
            params={**self.params, "osm_ids": osm_id},
            timeout=30,
            headers=self.headers,
        )
        r.raise_for_status()
        locations = r.json()

        if not locations:
            return {}

        location = locations[0]
        return {
            "coordinates": f"{location['lat']},{location['lon']}",
            "display_name": location["display_name"],
            "name": location["name"],
            "addresstype": location["addresstype"],
            "osm_id": osm_id,
        }

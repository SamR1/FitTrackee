import os

import requests

from fittrackee import VERSION, appLog


class NominatimService:
    def __init__(self) -> None:
        self.base_url = os.environ.get(
            "NOMINATIM_URL", "https://nominatim.openstreetmap.org"
        )
        self.params = {"format": "jsonv2"}
        self.headers = {"User-Agent": f"FitTrackee v{VERSION}"}

    def get_locations_from_query(self, query: str) -> list[dict]:
        url = f"{self.base_url}/search"
        appLog.debug(f"Nominatim: getting location for query: '{query}'")
        r = requests.get(
            url,
            params={**self.params, "q": query},
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
            }
            for location in locations
        ]

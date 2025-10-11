from typing import TYPE_CHECKING, Dict, List, Union

import requests
from flask import current_app

from fittrackee import appLog

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint


class OpenElevationService:
    """
    Documentation:
    https://github.com/Jorl17/open-elevation/blob/master/docs/api.md
    """

    def __init__(self) -> None:
        self.url = self._get_api_url()

    @property
    def is_enabled(self) -> bool:
        return self.url is not None

    @staticmethod
    def _get_api_url() -> Union[str, None]:
        base_url = current_app.config["OPEN_ELEVATION_API_URL"]
        if not base_url:
            return None
        return f"{base_url}/api/v1/lookup"

    def get_elevations(self, points: List["GPXTrackPoint"]) -> List[Dict]:
        if not self.url:
            return []

        appLog.debug("Open Elevation API: getting missing elevations")

        try:
            r = requests.post(
                self.url,
                json={
                    "locations": [
                        {
                            "latitude": point.latitude,
                            "longitude": point.longitude,
                        }
                        for point in points
                    ]
                },
                timeout=30,
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            appLog.exception(
                "Open Elevation API: error when getting missing elevations"
            )
            return []

        results = r.json().get("results", [])

        # Should not happen
        if len(results) != len(points):
            appLog.error(
                "Open Elevation API: mismatch between number of points in "
                "results, ignoring results"
            )
            return []
        return results

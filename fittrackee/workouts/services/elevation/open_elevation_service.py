from typing import TYPE_CHECKING, List

import requests

from fittrackee import appLog

from .base_elevation_service import BaseElevationService

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint


class OpenElevationService(BaseElevationService):
    """
    Documentation:
    https://github.com/Jorl17/open-elevation/blob/master/docs/api.md
    """

    config_key = "OPEN_ELEVATION_API_URL"
    url_pattern = "{base_url}/api/v1/lookup"
    log_label = "Open Elevation API"

    def _get_elevations_for_api(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        if not self.url:
            appLog.debug(
                "Open Elevation API: no URL set, "
                "returning empty list of elevation"
            )
            return []

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
        return [int(r["elevation"]) for r in results]

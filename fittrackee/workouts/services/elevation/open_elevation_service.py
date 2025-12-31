from typing import TYPE_CHECKING, List

import requests

from .base_elevation_service import BaseElevationService
from .exceptions import ElevationServiceException

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
            raise ElevationServiceException("Open Elevation API: no URL set")

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
        results = r.json().get("results", [])
        return [int(r["elevation"]) for r in results]

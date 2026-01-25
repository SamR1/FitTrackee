from typing import TYPE_CHECKING, List

import requests

from .base_elevation_service import BaseElevationService
from .exceptions import ElevationServiceException

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint


class ValhallaElevationService(BaseElevationService):
    """
    Documentation:
    https://valhalla.github.io/valhalla/api/elevation/api-reference/
    """

    config_key = "VALHALLA_API_URL"
    url_pattern = "{base_url}/height"
    log_label = "Valhalla Elevation API"

    def _get_elevations_for_api(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        if not self.url:
            raise ElevationServiceException("Valhalla API: no URL set")

        r = requests.post(
            self.url,
            json={
                "shape": [
                    {"lat": point.latitude, "lon": point.longitude}
                    for point in points
                ]
            },
            timeout=30,
        )
        r.raise_for_status()
        results = r.json().get("height", [])
        return results

from typing import TYPE_CHECKING, List

import requests

from fittrackee import appLog

from .base_elevation_service import BaseElevationService

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
            appLog.debug(
                "Valhalla Elevation API: no URL set, "
                "returning empty list of elevation"
            )
            return []

        try:
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
        except requests.exceptions.HTTPError:
            appLog.exception(
                "Valhalla Elevation API: error when getting missing elevations"
            )
            return []

        results = r.json().get("height", [])
        return results

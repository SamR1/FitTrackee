from typing import TYPE_CHECKING, List, Union

import requests
from flask import current_app

from fittrackee import appLog

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint


class ValhallaElevationService:
    """
    Documentation:
    https://valhalla.github.io/valhalla/api/elevation/api-reference/
    """

    def __init__(self) -> None:
        self.url = self._get_api_url()

    @property
    def is_enabled(self) -> bool:
        return self.url is not None

    @staticmethod
    def _get_api_url() -> Union[str, None]:
        base_url = current_app.config["VALHALLA_API_URL"]
        if not base_url:
            return None
        return f"{base_url}/height"

    def get_elevations(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        if not self.url:
            return []

        appLog.debug("Valhalla Elevation API: getting missing elevations")

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

        # Should not happen
        if len(results) != len(points):
            appLog.error(
                "Valhalla Elevation API: mismatch between number of points in "
                "results, ignoring results"
            )
            return []

        return results

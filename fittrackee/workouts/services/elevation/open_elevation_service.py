from typing import TYPE_CHECKING, Dict, List, Union

import numpy as np
import requests
from flask import current_app

from fittrackee import appLog

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint

WINDOW_LEN = 51


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

    @staticmethod
    def smooth_elevations(points: List[Dict]) -> List[Dict]:
        """
        smooth elevations using 'flat' window

        based on SciPy Cookbook:
        https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
        """
        if len(points) < 3:
            return points

        points_array = np.array([point["elevation"] for point in points])
        window_len = len(points) if len(points) < WINDOW_LEN else WINDOW_LEN

        s = np.r_[
            points_array[window_len - 1 : 0 : -1],
            points_array,
            points_array[-2 : -window_len - 1 : -1],
        ]
        w = np.ones(window_len, "d")
        y = np.convolve(w / w.sum(), s, mode="valid")
        start = window_len // 2 + 1
        end = start + len(points_array)
        smooth_array = y[start:end]

        for index in range(len(points)):
            points[index]["elevation"] = int(smooth_array[index])
        return points

    def get_elevations(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[Dict]:
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

        if smooth:
            return self.smooth_elevations(results)
        return results

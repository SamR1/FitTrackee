import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

import numpy as np

from fittrackee import appLog

from .exceptions import ElevationServiceException

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint

WINDOW_LEN = 51


class BaseElevationService(ABC):
    config_key: str = ""
    url_pattern: str = ""
    log_label: str = ""

    def __init__(self) -> None:
        self.url = self._get_api_url()

    @property
    def is_enabled(self) -> bool:
        return self.url != ""

    def _get_api_url(self) -> str:
        base_url = os.environ.get(self.config_key)
        if not base_url:
            return ""
        return self.url_pattern.format(base_url=base_url)

    @staticmethod
    def smooth_elevations(points: List[int]) -> List[int]:
        """
        smooth elevations using 'flat' window

        based on SciPy Cookbook:
        https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
        """
        if len(points) < 3:
            return [int(p) for p in points]

        points_array = np.array(points)
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

        return [int(p) for p in smooth_array]

    @abstractmethod
    def _get_elevations_for_api(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        pass

    def get_elevations(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        appLog.debug(
            "{log_label}: getting missing elevations".format(
                log_label=self.log_label
            )
        )

        results = self._get_elevations_for_api(points)

        # Should not happen
        if len(results) != len(points):
            error = (
                f"{self.log_label}: mismatch between number of points in "
                "results"
            )
            appLog.error(error)
            raise ElevationServiceException(error)

        if smooth:
            return self.smooth_elevations(results)
        return results

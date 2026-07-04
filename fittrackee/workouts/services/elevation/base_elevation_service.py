import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from fittrackee import appLog

from .elevation_mixin import ElevationMixin
from .exceptions import ElevationServiceException

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint


class BaseElevationService(ABC, ElevationMixin):
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

    @abstractmethod
    def _get_elevations_for_api(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        pass

    def get_elevations(
        self, points: List["GPXTrackPoint"], smooth: bool = False
    ) -> List[int]:
        appLog.debug(
            "{log_label}: getting elevations".format(log_label=self.log_label)
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

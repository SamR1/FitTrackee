from typing import TYPE_CHECKING, List, Tuple, Union

from fittrackee.constants import ElevationDataSource

from .open_elevation_service import OpenElevationService
from .valhalla_elevation_service import ValhallaElevationService

if TYPE_CHECKING:
    from gpxpy.gpx import GPXTrackPoint

WINDOW_LEN = 51


class ElevationService:
    """
    Available elevation services:
    - Open Elevation (with or without smoothing processing)
    - Valhalla
    """

    def __init__(self, elevation_data_source: "ElevationDataSource") -> None:
        self.elevation_service, self.smooth = self._get_elevation_service(
            elevation_data_source
        )

    @staticmethod
    def _get_elevation_service(
        elevation_data_source: "ElevationDataSource",
    ) -> Tuple[
        Union["OpenElevationService", "ValhallaElevationService", None], bool
    ]:
        if elevation_data_source == ElevationDataSource.FILE:
            return None, False

        if elevation_data_source in [
            ElevationDataSource.OPEN_ELEVATION,
            ElevationDataSource.OPEN_ELEVATION_SMOOTH,
        ]:
            service: Union[
                "OpenElevationService", "ValhallaElevationService"
            ] = OpenElevationService()
            return (
                service if service.is_enabled else None,
                (
                    elevation_data_source
                    == ElevationDataSource.OPEN_ELEVATION_SMOOTH
                ),
            )

        if elevation_data_source == ElevationDataSource.VALHALLA:
            service = ValhallaElevationService()
            return service if service.is_enabled else None, False

        return None, False

    def get_elevations(self, points: List["GPXTrackPoint"]) -> List[int]:
        if not self.elevation_service:
            return []

        return self.elevation_service.get_elevations(
            points, smooth=self.smooth
        )

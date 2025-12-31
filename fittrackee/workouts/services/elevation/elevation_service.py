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
        self.elevation_service, self.smooth, self.elevation_data_source = (
            self._get_elevation_service(elevation_data_source)
        )

    @staticmethod
    def _get_elevation_service(
        elevation_data_source: "ElevationDataSource",
    ) -> Tuple[
        Union["OpenElevationService", "ValhallaElevationService", None],
        bool,
        "ElevationDataSource",
    ]:
        if elevation_data_source == ElevationDataSource.FILE:
            return None, False, elevation_data_source

        service: Union[
            "OpenElevationService", "ValhallaElevationService", None
        ] = None
        if elevation_data_source in [
            ElevationDataSource.OPEN_ELEVATION,
            ElevationDataSource.OPEN_ELEVATION_SMOOTH,
        ]:
            service = OpenElevationService()

        if elevation_data_source == ElevationDataSource.VALHALLA:
            service = ValhallaElevationService()

        if service and service.is_enabled:
            return (
                service,
                (
                    elevation_data_source
                    == ElevationDataSource.OPEN_ELEVATION_SMOOTH
                ),
                elevation_data_source,
            )
        return None, False, ElevationDataSource.FILE

    def get_elevations(self, points: List["GPXTrackPoint"]) -> List[int]:
        if not self.elevation_service:
            return []

        return self.elevation_service.get_elevations(
            points, smooth=self.smooth
        )

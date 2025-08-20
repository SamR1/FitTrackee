import zipfile
from typing import IO, TYPE_CHECKING

from ...exceptions import WorkoutFileException
from .workout_kml_service import WorkoutKmlService

if TYPE_CHECKING:
    import gpxpy.gpx


class WorkoutKmzService(WorkoutKmlService):
    @classmethod
    def parse_file(
        cls,
        workout_file: IO[bytes],
        segments_creation_event: str,
    ) -> "gpxpy.gpx.GPX":
        """
        Only kmz files with Tracks are supported.
        Notes:
        - for now kmz with photos are not supported
        - segments_creation_event is not used (only for .fit files)

        Tested with files generated with OpenTracks.
        """
        with zipfile.ZipFile(workout_file, "r") as kmz_ref:
            try:
                kml_content = kmz_ref.open("doc.kml")
            except KeyError as e:
                raise WorkoutFileException(
                    "error", "error when parsing kmz file"
                ) from e
        return super().parse_file(kml_content, segments_creation_event)

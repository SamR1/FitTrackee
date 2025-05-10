import zipfile
from typing import IO, TYPE_CHECKING

from ...exceptions import WorkoutFileException
from .workout_kml_creation_service import WorkoutKmlCreationService

if TYPE_CHECKING:
    import gpxpy.gpx


class WorkoutKmzCreationService(WorkoutKmlCreationService):
    @classmethod
    def parse_file(cls, workout_file: IO[bytes]) -> "gpxpy.gpx.GPX":
        """
        Only kmz files with Tracks are supported.
        Note: for now kmz with photos are not supported.

        Tested with files generated with OpenTracks.
        """
        with zipfile.ZipFile(workout_file, "r") as kmz_ref:
            try:
                kml_content = kmz_ref.open("doc.kml")
            except KeyError as e:
                raise WorkoutFileException(
                    "error", "error when parsing kmz file"
                ) from e
        return super().parse_file(kml_content)

from typing import IO

import gpxpy.gpx
import xmltodict
from gpxpy.gpxfield import parse_time

from ...exceptions import WorkoutFileException
from .workout_gpx_creation_service import WorkoutGpxCreationService


class WorkoutKmlCreationService(WorkoutGpxCreationService):
    @classmethod
    def parse_file(cls, workout_file: IO[bytes]) -> "gpxpy.gpx.GPX":
        try:
            kml_dict = xmltodict.parse(workout_file)
        except Exception as e:
            raise WorkoutFileException(
                "error", "error when parsing kml file"
            ) from e

        placemark = kml_dict["kml"].get("Document", {}).get("Placemark", {})
        kml_tracks = placemark.get("MultiTrack", {}).get("Track")
        coordinates_key = "coord"
        if not kml_tracks:
            kml_tracks = placemark.get("gx:MultiTrack", {}).get("gx:Track")
            if not kml_tracks:
                raise WorkoutFileException(
                    "error", "no tracks in kml file"
                ) from None
            coordinates_key = "gx:coord"

        if isinstance(kml_tracks, dict):
            kml_tracks = [kml_tracks]

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.name = placemark.get("name")
        gpx_track.description = placemark.get("description")
        for kml_track in kml_tracks:
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)
            coords = kml_track.get(coordinates_key, [])
            for index, date in enumerate(kml_track.get("when", [])):
                if not coords[index]:
                    continue
                longitude, latitude, elevation = coords[index].split()
                gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(
                        longitude=float(longitude),
                        latitude=float(latitude),
                        elevation=float(elevation),
                        time=parse_time(date),
                    )
                )
        gpx = gpxpy.gpx.GPX()
        gpx.tracks.append(gpx_track)
        return gpx

from typing import IO

import gpxpy.gpx
import xmltodict
from gpxpy.gpxfield import parse_time

from ...exceptions import WorkoutFileException
from .workout_gpx_service import WorkoutGpxService


class WorkoutKmlService(WorkoutGpxService):
    @classmethod
    def parse_file(
        cls,
        workout_file: IO[bytes],
        segments_creation_event: str,
    ) -> "gpxpy.gpx.GPX":
        """
        Only kml files with Placemark/MultiTrack/Tracks are supported.
        Files with folders or multiple Placemark are no supported.

        For now, a gpx file generated from kml file contains one track (<trk>)
        corresponding to the first MultiTrack, containing one segment
        (<trkseg>) per kml track (<Track>).

        Tested with files generated with OpenTracks.

        Note:
        - segments_creation_event is not used (only for .fit files)
        """
        try:
            kml_dict = xmltodict.parse(workout_file)
        except Exception as e:
            raise WorkoutFileException(
                "error", "error when parsing kml file"
            ) from e

        placemarks = kml_dict["kml"].get("Document", {}).get("Placemark", [])
        if not placemarks:
            raise WorkoutFileException(
                "error", "unsupported kml file"
            ) from None
        if isinstance(placemarks, dict):
            placemarks = [placemarks]
        placemark = placemarks[0]

        kml_tracks = placemark.get("MultiTrack", {}).get("Track", [])
        coordinates_key = "coord"
        if not kml_tracks:
            kml_tracks = placemark.get("gx:MultiTrack", {}).get("gx:Track", [])
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

            coords = kml_track.get(coordinates_key, [])
            if not coords:
                continue
            if isinstance(coords, dict):
                coords = [coords]
            times = kml_track.get("when", [])
            if isinstance(times, dict):
                times = [times]

            heart_rates = []
            cadences = []
            powers = []
            extended_data = (
                kml_track.get("ExtendedData", {})
                .get("SchemaData", {})
                .get("gx:SimpleArrayData", [])
            )
            for data in extended_data:
                if data["@name"] == "heartrate":
                    heart_rates = data["gx:value"]
                if data["@name"] == "cadence":
                    cadences = data["gx:value"]
                if data["@name"] == "power":
                    powers = data["gx:value"]

            for index, date in enumerate(times):
                if not coords[index]:
                    continue
                longitude, latitude, elevation = coords[index].split()
                point = gpxpy.gpx.GPXTrackPoint(
                    longitude=float(longitude),
                    latitude=float(latitude),
                    elevation=float(elevation),
                    time=parse_time(date),
                )
                heart_rate = (
                    heart_rates[index] if len(heart_rates) > index else None
                )
                cadence = cadences[index] if len(cadences) > index else None
                power = powers[index] if len(powers) > index else None
                if (
                    heart_rate is not None
                    or cadence is not None
                    or power is not None
                ):
                    point.extensions.append(
                        cls._get_extensions(heart_rate, cadence, power)
                    )

                gpx_segment.points.append(point)
            gpx_track.segments.append(gpx_segment)
        gpx = gpxpy.gpx.GPX()
        gpx.tracks.append(gpx_track)
        return gpx

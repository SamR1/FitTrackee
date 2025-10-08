from typing import Optional

import gpxpy.gpx


def open_gpx_file(gpx_file: str) -> Optional[gpxpy.gpx.GPX]:
    gpx_file = open(gpx_file, "r")  # type: ignore
    gpx = gpxpy.parse(gpx_file)
    if len(gpx.tracks) == 0:
        return None
    return gpx


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()

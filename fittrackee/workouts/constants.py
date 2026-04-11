WORKOUT_DATE_FORMAT = "%Y-%m-%d %H:%M"

# sports with cadence displayed in revolutions per minute
RPM_CADENCE_SPORTS = [
    "Cycling (Sport)",
    "Cycling (Trekking)",
    "Cycling (Transport)",
    "Cycling (Virtual)",
    "Halfbike",
    "Mountain Biking",
    "Mountain Biking (Electric)",
    "Open Water Swimming",
]
# sports with cadence displayed in steps per minute
SPM_CADENCE_SPORTS = [
    "Hiking",
    "Mountaineering",
    "Snowshoes",
    "Running",
    "Trail",
    "Walking",
]
CADENCE_SPORTS = [*RPM_CADENCE_SPORTS, *SPM_CADENCE_SPORTS]
POWER_SPORTS = [
    "Cycling (Sport)",
    "Cycling (Trekking)",
    "Cycling (Transport)",
    "Cycling (Virtual)",
    "Halfbike",
    "Mountain Biking",
    "Mountain Biking (Electric)",
]
PACE_SPORTS = [
    "Hiking",
    "Running",
    "Trail",
    "Walking",
]
# elevation data (ascent, descent, min and max alt), if present, are not
# stored and/or displayed
SPORTS_WITHOUT_ELEVATION_DATA = [
    "Ice Skating",
    # racket sports
    "Padel (Outdoor)",
    "Tennis (Outdoor)",
    # flatwater sports
    "Canoeing",
    "Kayaking",
    "Open Water Swimming",
    "Rowing",
    "Standup Paddleboarding",
]

WORKOUT_FILE_MIMETYPES = {
    "fit": "application/vnd.ant.fit",
    "gpx": "application/gpx+xml",
    "kml": "application/vnd.google-earth.kml+xml",
    "kmz": "application/vnd.google-earth.kmz",
    "tcx": "application/vnd.garmin.tcx+xml",
}
WORKOUT_ALLOWED_EXTENSIONS = set(WORKOUT_FILE_MIMETYPES.keys())
XML_MIMETYPE = "text/xml"
OCTET_STREAM_MIMETYPE = "application/octet-stream"
ZIP_MIMETYPE = "application/zip"
WORKOUT_FILE_MAGIC_MIMETYPES = {
    "fit": [OCTET_STREAM_MIMETYPE],
    "gpx": [XML_MIMETYPE],
    "kml": [XML_MIMETYPE],
    "kmz": [WORKOUT_FILE_MIMETYPES["kmz"], ZIP_MIMETYPE],
    "tcx": [XML_MIMETYPE],
    "zip": [OCTET_STREAM_MIMETYPE, ZIP_MIMETYPE],
}
WORKOUT_ALL_ALLOWED_EXTENSIONS = set(WORKOUT_FILE_MAGIC_MIMETYPES.keys())

NSMAP = {
    "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
}
TRACK_EXTENSION_NSMAP = {
    "gpxtrkx": "http://www.garmin.com/xmlschemas/TrackStatsExtension/v1"
}

WGS84_CRS = 4326  # World Geodetic System 1984, in degrees

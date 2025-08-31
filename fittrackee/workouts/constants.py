WORKOUT_ALLOWED_EXTENSIONS = {"gpx", "fit", "kml", "kmz", "tcx"}
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
POWER_SPORTS = [
    "Cycling (Sport)",
    "Cycling (Trekking)",
    "Cycling (Transport)",
    "Cycling (Virtual)",
    "Halfbike",
    "Mountain Biking",
    "Mountain Biking (Electric)",
]
# elevation data (ascent, descent, min and max alt), if present, are not
# displayed
SPORTS_WITHOUT_ELEVATION_DATA = [
    "Tennis (Outdoor)",
]

WORKOUT_FILE_MIMETYPES = {
    "fit": "application/vnd.ant.fit",
    "gpx": "application/gpx+xml",
    "kml": "application/vnd.google-earth.kml+xml",
    "tcx": "application/vnd.garmin.tcx+xml",
}

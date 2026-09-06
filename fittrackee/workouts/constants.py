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
# sports for which the segments are associated with sports
MULTI_ACTIVITIES_SPORTS = {
    "Swimrun": [
        "Open Water Swimming",
        "Running",
        "Trail",
    ],
    "Triathlon": [
        "Cycling (Sport)",
        "Open Water Swimming",
        "Running",
        "Trail",
    ],
}
# Only sports for multiple activities sport for now
FIT_MATCHING_SPORTS = {
    "cycling|generic": "Cycling (Sport)",
    "cycling|mountain": "Mountain Biking",
    "running|trail": "Trail",
    "running|generic": "Running",
    "swimming|open_water": "Open Water Swimming",
}


# for file download
WORKOUT_FILE_MIMETYPES = {
    "fit": "application/vnd.ant.fit",
    "gpx": "application/gpx+xml",
    "kml": "application/vnd.google-earth.kml+xml",
    "kmz": "application/vnd.google-earth.kmz",
    "tcx": "application/vnd.garmin.tcx+xml",
}
WORKOUT_ALLOWED_EXTENSIONS = set(WORKOUT_FILE_MIMETYPES.keys())

TIMEDELTA_COLUMNS = [
    "duration",
    "pauses",
    "moving",
    "ave_pace",
    "best_pace",
]

# detected mime types on file upload
XML_MIMETYPE = "text/xml"
OCTET_STREAM_MIMETYPE = "application/octet-stream"
ZIP_MIMETYPE = "application/zip"
WORKOUT_FILE_DETECTED_MIMETYPES = {
    "fit": [OCTET_STREAM_MIMETYPE],
    "gpx": [XML_MIMETYPE],
    "kml": [XML_MIMETYPE],
    "kmz": [
        WORKOUT_FILE_MIMETYPES["kmz"],
        OCTET_STREAM_MIMETYPE,
        ZIP_MIMETYPE,
    ],
    "tcx": [XML_MIMETYPE],
    "zip": [OCTET_STREAM_MIMETYPE, ZIP_MIMETYPE],
}
WORKOUT_ALL_ALLOWED_EXTENSIONS = set(WORKOUT_FILE_DETECTED_MIMETYPES.keys())

NSMAP = {
    "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
}
TRACK_EXTENSION_NSMAP = {
    "gpxtrkx": "http://www.garmin.com/xmlschemas/TrackStatsExtension/v1"
}

WGS84_CRS = 4326  # World Geodetic System 1984, in degrees
WEB_MERCATOR_CRS = 3857  # Web Mercator, in meters

DEFAULT_HEATMAP_ZOOM = 10
MAX_HEATMAP_ZOOM = 20
MAX_HEATMAP_CELLS = 20000
# how many times a view can be merged further to fit MAX_HEATMAP_CELLS
MAX_HEATMAP_MERGES = 4

TILE_SIZE = 256  # in pixels

WEB_MERCATOR_WORLD_SIZE = 40075016.6855785  # in meters

# cells are stored at the resolution given by HEATMAP_BASE_ZOOM (see config):
# around 38 m by default, and they can only be merged, so it is the finest
# detail the heatmap can display
HEATMAP_DEFAULT_BASE_ZOOM = 20
HEATMAP_MIN_BASE_ZOOM = 20
# finer cells mostly resolve the GPS noise, for twice the rows at each level
HEATMAP_MAX_BASE_ZOOM = 24

# cells are merged to keep them around this size on screen, so that the
# heatmap stays similarly grained when zooming out. Below a pixel the tracks
# read as thin lines; denser views are merged back by MAX_HEATMAP_CELLS.
HEATMAP_CELL_PIXELS = 1  # in pixels

# tracks are subdivided into pieces of at most this many vertices before being
# gridded, to keep their bounding boxes small
SUBDIVIDE_MAX_VERTICES = 8

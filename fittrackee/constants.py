import os
from enum import Enum, IntEnum

TASKS_TIME_LIMIT = int(os.environ.get("TASKS_TIME_LIMIT", "1800")) * 1000


class TaskPriority(IntEnum):
    LOW = 100
    MEDIUM = 50
    HIGH = 0


class ElevationDataSource(str, Enum):  # to make enum serializable
    FILE = "file"
    OPEN_ELEVATION = "open_elevation"
    OPEN_ELEVATION_SMOOTH = "open_elevation_smooth"
    VALHALLA = "valhalla"

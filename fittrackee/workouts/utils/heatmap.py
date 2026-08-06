import math
from typing import List, Tuple

from flask import current_app

from ..constants import (
    HEATMAP_CELL_PIXELS,
    TILE_SIZE,
    WEB_MERCATOR_WORLD_SIZE,
)

# Web Mercator (EPSG:3857) sphere radius, in meters
EARTH_RADIUS = 6378137.0

# latitudes beyond this value are not representable in Web Mercator
MAX_MERCATOR_LATITUDE = 85.051129


def get_base_cell_size() -> float:
    """
    Size of a stored cell, in meters in Web Mercator
    """
    return (
        WEB_MERCATOR_WORLD_SIZE / 2 ** current_app.config["HEATMAP_BASE_ZOOM"]
    )


def get_cells_shift(zoom: int) -> int:
    """
    How many times cells must be merged in each direction to stay around
    HEATMAP_CELL_PIXELS wide at the given zoom level. They cannot be split, so
    the shift stops at 0.
    """
    pixels_ratio = int(math.log2(TILE_SIZE / HEATMAP_CELL_PIXELS))
    base_zoom = current_app.config["HEATMAP_BASE_ZOOM"]
    return max(0, base_zoom - zoom - pixels_ratio)


def get_cell_size(shift: int) -> float:
    return get_base_cell_size() * 2**shift


def to_web_mercator(longitude: float, latitude: float) -> Tuple[float, float]:
    clamped_latitude = max(
        -MAX_MERCATOR_LATITUDE, min(MAX_MERCATOR_LATITUDE, latitude)
    )
    return (
        EARTH_RADIUS * math.radians(longitude),
        EARTH_RADIUS
        * math.log(math.tan(math.pi / 4 + math.radians(clamped_latitude) / 2)),
    )


def get_cells_range(
    bbox: List[float], shift: int
) -> Tuple[int, int, int, int]:
    """
    Indices of the stored cells covering a bounding box given as
    min_lng,min_lat,max_lng,max_lat.

    Returned at the stored resolution, so that they can be compared to the
    columns and use their index, and expanded to whole merged cells, else the
    cells overlapping the edges would only be counted in part.
    """
    min_lng, min_lat, max_lng, max_lat = bbox
    min_x, min_y = to_web_mercator(min_lng, min_lat)
    max_x, max_y = to_web_mercator(max_lng, max_lat)
    cell_size = get_cell_size(shift)
    return (
        math.floor(min_x / cell_size) << shift,
        math.floor(min_y / cell_size) << shift,
        ((math.floor(max_x / cell_size) + 1) << shift) - 1,
        ((math.floor(max_y / cell_size) + 1) << shift) - 1,
    )

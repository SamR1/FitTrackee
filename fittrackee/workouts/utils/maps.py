import hashlib
from typing import List

from flask import current_app
from staticmap import Line, StaticMap

from fittrackee.files import get_absolute_file_path


def generate_map(map_filepath: str, map_data: List) -> None:
    """
    Generate and save map image from map data
    """
    m = StaticMap(400, 225, 10)
    if not current_app.config['TILE_SERVER']['DEFAULT_STATICMAP']:
        m.url_template = current_app.config['TILE_SERVER']['URL'].replace(
            '{s}.', ''
        )
    line = Line(map_data, '#3388FF', 4)
    m.add_line(line)
    image = m.render()
    image.save(map_filepath)


def get_map_hash(map_filepath: str) -> str:
    """
    Generate a md5 hash used as id instead of workout id, to retrieve map
    image (maps are sensitive data)
    """
    md5 = hashlib.md5()
    absolute_map_filepath = get_absolute_file_path(map_filepath)
    with open(absolute_map_filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

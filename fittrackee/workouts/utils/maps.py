import hashlib
import random
from typing import Dict, List

from flask import current_app
from staticmap import Line, StaticMap

from fittrackee import VERSION
from fittrackee.files import get_absolute_file_path


def get_static_map_tile_server_url(tile_server_config: Dict) -> str:
    if tile_server_config['STATICMAP_SUBDOMAINS']:
        subdomains = tile_server_config['STATICMAP_SUBDOMAINS'].split(',')
        subdomain = f'{random.choice(subdomains)}.'  # nosec
    else:
        subdomain = ''
    return tile_server_config['URL'].replace('{s}.', subdomain)


def generate_map(map_filepath: str, map_data: List) -> None:
    """
    Generate and save map image from map data
    """
    m = StaticMap(400, 225, 10)
    m.headers = {'User-Agent': f'FitTrackee v{VERSION}'}
    if not current_app.config['TILE_SERVER']['DEFAULT_STATICMAP']:
        m.url_template = get_static_map_tile_server_url(
            current_app.config['TILE_SERVER']
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
    md5 = hashlib.md5()  # nosec  # need 3.9+ to use 'usedforsecurity' flag
    absolute_map_filepath = get_absolute_file_path(map_filepath)
    with open(absolute_map_filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

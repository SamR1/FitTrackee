import os
from typing import Union

from flask import current_app


def display_readable_file_size(size_in_bytes: Union[float, int]) -> str:
    """
    Return readable file size from size in bytes
    """
    if size_in_bytes == 0:
        return '0 bytes'
    if size_in_bytes == 1:
        return '1 byte'
    for unit in [' bytes', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_in_bytes) < 1024.0:
            return f'{size_in_bytes:3.1f}{unit}'
        size_in_bytes /= 1024.0
    return f'{size_in_bytes} bytes'


def get_absolute_file_path(relative_path: str) -> str:
    return os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)

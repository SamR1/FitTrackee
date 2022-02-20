import os

from fittrackee.files import get_absolute_file_path


def get_upload_dir_size() -> int:
    """
    Return upload directory size
    """
    upload_path = get_absolute_file_path('')
    total_size = 0
    for dir_path, _, filenames in os.walk(upload_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            total_size += os.path.getsize(fp)
    return total_size

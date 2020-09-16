import os

from flask import current_app


def get_absolute_file_path(relative_path):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)

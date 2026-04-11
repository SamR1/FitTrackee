import os
from typing import IO, TYPE_CHECKING, Dict, Union
from uuid import uuid4

import magic
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename

from fittrackee.workouts.constants import OCTET_STREAM_MIMETYPE

from .exceptions import FileException

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

INVALID_FILE_ERROR_MESSAGE = "invalid file"


def display_readable_file_size(size_in_bytes: Union[float, int]) -> str:
    """
    Return readable file size from size in bytes
    """
    if size_in_bytes == 0:
        return "0 bytes"
    if size_in_bytes == 1:
        return "1 byte"
    for unit in [" bytes", "KB", "MB", "GB", "TB"]:
        if abs(size_in_bytes) < 1024.0:
            return f"{size_in_bytes:3.1f}{unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes} bytes"


def get_absolute_file_path(relative_path: str) -> str:
    return os.path.join(current_app.config["UPLOAD_FOLDER"], relative_path)


def get_file_extension(filename: str) -> str:
    return secure_filename(filename).rsplit(".", 1)[-1].lower()


def check_zip_archive(file_buffer: bytes) -> bool:
    # zip archive magic numbers
    return (
        len(file_buffer) > 3
        and file_buffer[0] == 0x50
        and file_buffer[1] == 0x4B
        and (
            file_buffer[3] == 0x4
            or file_buffer[3] == 0x6
            or file_buffer[3] == 0x8
        )
    )


def check_mime_type(
    extension: str,
    file: Union[IO[bytes], "FileStorage"],
    valid_content_types: Dict,
) -> None:
    buffer = file.read(2048)

    # python-magic can raise error when detecting mime type on .fit file
    if extension == "fit":
        file_type = magic.from_buffer(buffer)
        if not file_type.startswith("FIT Map data"):
            raise FileException(INVALID_FILE_ERROR_MESSAGE)
        file.seek(0)
        return

    try:
        mime_type = magic.from_buffer(buffer, mime=True)
    except Exception as e:
        raise FileException(INVALID_FILE_ERROR_MESSAGE) from e

    # python-magic return default mime type ('application/octet-stream') for
    # archives, check magic numbers instead
    if (
        mime_type == OCTET_STREAM_MIMETYPE
        and extension in ["zip", "kmz"]
        and not check_zip_archive(buffer)
    ):
        raise FileException(INVALID_FILE_ERROR_MESSAGE)

    elif mime_type not in valid_content_types.get(extension, ""):
        raise FileException(INVALID_FILE_ERROR_MESSAGE)

    file.seek(0)


def check_file(file: "FileStorage", valid_content_types: Dict) -> str:
    if not file.filename:
        raise FileException("invalid file name")

    extension = get_file_extension(file.filename)
    if extension not in valid_content_types.keys():
        raise FileException("file extension not allowed")

    check_mime_type(extension, file, valid_content_types)

    return extension


def generate_filename(extension: str) -> str:
    return f"{uuid4().hex}.{extension}"


def get_image_without_exif(file: "FileStorage") -> "Image.Image":
    image = Image.open(file.stream)
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(image.get_flattened_data())
    return image_without_exif

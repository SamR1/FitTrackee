import os
import uuid
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import numpy as np
import PIL.ExifTags
from flask import current_app
from PIL import Image, ImageOps

from fittrackee import db
from fittrackee.constants import IMAGE_CONTENT_TYPES
from fittrackee.files import get_absolute_file_path, get_file_extension

from .exceptions import MediaException
from .models import Media

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

    from fittrackee.users.models import User

THUMBNAIL_MAX_SIZE = (350, 350)


class MediaService:
    def __init__(self, auth_user: "User", media_file: "FileStorage"):
        self.auth_user = auth_user
        self.media_file = media_file

    def _get_user_path(self) -> str:
        user_path = os.path.join("media", str(self.auth_user.id))
        absolute_user_path = get_absolute_file_path(user_path)
        if not os.path.exists(absolute_user_path):
            os.makedirs(absolute_user_path)
        return user_path

    @staticmethod
    def get_image_without_exif(image: "Image.Image") -> "Image.Image":
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(image.get_flattened_data())
        return image_without_exif

    @staticmethod
    def convert_to_degrees(value: Tuple) -> float:
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    def get_gps_info(self, exif: Dict | None) -> Optional[Dict]:
        if not exif:
            return None

        gps_info: Dict = {}
        for k, v in exif.items():
            if k in PIL.ExifTags.TAGS and PIL.ExifTags.TAGS[k] == "GPSInfo":
                gps_info = {}
                for key in v.keys():
                    decode = PIL.ExifTags.GPSTAGS.get(key, key)
                    gps_info[decode] = v[key]
                break

        if not gps_info:
            return None

        latitude = self.convert_to_degrees(gps_info["GPSLatitude"])
        if gps_info["GPSLatitudeRef"] != "N":
            latitude = -latitude
        if np.isnan(latitude):
            return None

        longitude = self.convert_to_degrees(gps_info["GPSLongitude"])
        if gps_info["GPSLongitudeRef"] != "E":
            longitude = -longitude
        if np.isnan(longitude):
            return None

        return {"longitude": longitude, "latitude": latitude}

    def create_image_media(self) -> "Media":
        if not self.media_file.filename:
            raise MediaException("error", "invalid file name")

        extension = get_file_extension(self.media_file.filename)
        if extension not in current_app.config["PICTURE_ALLOWED_EXTENSIONS"]:
            raise MediaException("error", "media file invalid extension")

        try:
            image = Image.open(self.media_file.stream)
        except Exception as e:
            raise MediaException(
                "error", "error when reading media file"
            ) from e

        try:
            gps_info = self.get_gps_info(image._getexif())  # type: ignore[attr-defined]
        except Exception:
            gps_info = None

        # rotate image based on EXIF tags
        updated_image = ImageOps.exif_transpose(image)
        if updated_image:
            image = updated_image  # type: ignore[assignment]

        image_without_exif = self.get_image_without_exif(image)
        image_name = uuid.uuid4().hex
        new_filename = f"{image_name}.{extension}"
        image_without_exif.save(
            get_absolute_file_path(
                os.path.join(self._get_user_path(), new_filename)
            )
        )

        # generate image thumbnail
        image_without_exif.thumbnail(size=THUMBNAIL_MAX_SIZE)
        thumbnail_filename = f"{image_name}.thumbnail.{extension}"
        thumbnail_absolute_file_path = get_absolute_file_path(
            os.path.join(self._get_user_path(), thumbnail_filename)
        )
        image_without_exif.save(thumbnail_absolute_file_path)

        media = Media(
            user_id=self.auth_user.id,
            file_name=new_filename,
            file_size=self.media_file.stream.tell(),
            file_content_type=IMAGE_CONTENT_TYPES[extension],
        )
        media.meta = {
            "coordinates": gps_info,
            "thumbnail": {
                "file_name": thumbnail_filename,
                "file_size": os.path.getsize(thumbnail_absolute_file_path),
            },
        }

        db.session.add(media)
        db.session.commit()

        return media

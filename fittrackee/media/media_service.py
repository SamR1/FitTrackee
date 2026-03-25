import os
import uuid
from typing import TYPE_CHECKING

from flask import current_app
from PIL import Image

from fittrackee import db
from fittrackee.files import get_absolute_file_path, get_file_extension

from .exceptions import MediaException
from .models import Media

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage

    from fittrackee.users.models import User


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

        image_without_exif = self.get_image_without_exif(image)
        new_filename = f"{uuid.uuid4().hex}.{extension}"
        absolute_workout_filepath = get_absolute_file_path(
            os.path.join(self._get_user_path(), new_filename)
        )
        image_without_exif.save(absolute_workout_filepath)

        media = Media(
            user_id=self.auth_user.id,
            file_name=new_filename,
            file_size=self.media_file.stream.tell(),
        )

        db.session.add(media)
        db.session.commit()

        return media

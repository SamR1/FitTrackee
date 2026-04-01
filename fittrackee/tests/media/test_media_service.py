import os
import uuid
from io import BytesIO
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from fittrackee.files import get_absolute_file_path, get_file_extension
from fittrackee.media.exceptions import MediaException
from fittrackee.media.media_service import MediaService
from fittrackee.media.models import Media

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class MediaServiceTestCase:
    @staticmethod
    def create_media_file(
        app: "Flask",
        filename: str = "image_with_gps_exif.jpg",
    ) -> "FileStorage":
        file_path = os.path.join(app.root_path, f"tests/files/{filename}")
        extension = get_file_extension(filename)
        with open(file_path, "rb") as image_file:
            return FileStorage(
                filename=f"image.{extension}",
                stream=BytesIO(image_file.read()),
            )


class TestMediaServiceInstantiation(MediaServiceTestCase):
    def test_it_instantiates_service(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media_file = self.create_media_file(app)

        service = MediaService(user_1, media_file)

        assert service.auth_user == user_1
        assert service.media_file == media_file


class TestMediaServiceGetImageWithoutExif(MediaServiceTestCase):
    def test_it_creates_new_image_without_exif_data(
        self, app: "Flask", user_1: "User"
    ) -> None:
        service = MediaService(user_1, self.create_media_file(app))
        image = Image.open(
            os.path.join(app.root_path, "tests/files/image_with_gps_exif.jpg")
        )

        new_image = service.get_image_without_exif(image)

        assert dict(new_image.getexif()) == {}


class TestMediaServiceCreateImageMedia(MediaServiceTestCase):
    def test_it_raises_error_if_file_storage_has_no_filename(
        self, app: "Flask", user_1: "User"
    ) -> None:

        service = MediaService(user_1, FileStorage(stream=BytesIO()))

        with pytest.raises(MediaException, match="invalid file name"):
            service.create_image_media()

    def test_it_raises_error_if_extension_is_invalid(
        self, app: "Flask", user_1: "User"
    ) -> None:

        service = MediaService(
            user_1, FileStorage(filename="invalid.bmp", stream=BytesIO())
        )

        with pytest.raises(
            MediaException, match="media file invalid extension"
        ):
            service.create_image_media()

    def test_it_raises_error_when_pillow_can_not_read_image(
        self, app: "Flask", user_1: "User"
    ) -> None:

        service = MediaService(
            user_1, FileStorage(filename="image.jpg", stream=BytesIO())
        )

        with pytest.raises(
            MediaException, match="error when reading media file"
        ):
            service.create_image_media()

    def test_it_creates_image_media_in_database(
        self, app: "Flask", user_1: "User"
    ) -> None:
        service = MediaService(
            user_1,
            self.create_media_file(app, filename="image_without_exif.png"),
        )

        with patch.object(uuid, "uuid4") as uuid4_mock:
            uuid4_mock.return_value.hex = "12z3e4"
            service.create_image_media()

        media = Media.query.one()
        assert media.file_path == f"media/{user_1.id}/12z3e4.png"
        assert media.file_size == 138
        assert media.user_id == user_1.id
        assert media.meta == {"coordinates": None}

    def test_it_creates_image_media_when_image_has_gps_exif(
        self, app: "Flask", user_1: "User"
    ) -> None:
        service = MediaService(
            user_1,
            self.create_media_file(app, filename="image_with_gps_exif.jpg"),
        )

        with patch.object(uuid, "uuid4") as uuid4_mock:
            uuid4_mock.return_value.hex = "12z3e4"
            service.create_image_media()

        media = Media.query.one()
        assert media.file_path == f"media/{user_1.id}/12z3e4.jpg"
        assert media.file_size == 1173
        assert media.user_id == user_1.id
        assert media.meta == {
            "coordinates": {
                "latitude": 45.755833333333335,
                "longitude": 4.8308333333333335,
            }
        }

    def test_it_returns_media(self, app: "Flask", user_1: "User") -> None:
        service = MediaService(user_1, self.create_media_file(app))

        media = service.create_image_media()

        assert isinstance(media, Media)

    def test_it_stores_file_without_exif(
        self, app: "Flask", user_1: "User"
    ) -> None:
        service = MediaService(user_1, self.create_media_file(app))

        media = service.create_image_media()

        image = Image.open(get_absolute_file_path(media.file_path))
        assert dict(image.getexif()) == {}

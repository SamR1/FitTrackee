import os
from io import BytesIO
from typing import TYPE_CHECKING

import pytest
from PIL import Image, ImageChops
from werkzeug.datastructures import FileStorage

from fittrackee.constants import IMAGE_MIMETYPES
from fittrackee.exceptions import FileException
from fittrackee.files import (
    check_file,
    get_file_extension,
    get_image_without_exif,
)
from fittrackee.tests.workouts.mixins import WorkoutFileMixin
from fittrackee.workouts.constants import WORKOUT_FILE_DETECTED_MIMETYPES

from .mixins import ImageMixin

if TYPE_CHECKING:
    from flask import Flask


class TestGetFileExtension:
    @pytest.mark.parametrize(
        "input_filename,expected_extension",
        [
            ("", ""),
            ("image.png", "png"),
            ("workout.gpx", "gpx"),
            ("test.py", "py"),
            ("multiple-extensions.py.tcx", "tcx"),
        ],
    )
    def test_it_returns_file_extension(
        self, input_filename: str, expected_extension: str
    ) -> None:
        extension = get_file_extension(input_filename)

        assert extension == expected_extension


class TestCheckFile(ImageMixin, WorkoutFileMixin):
    def test_it_raises_error_if_file_storage_has_no_filename(self) -> None:
        file = FileStorage(stream=BytesIO())

        with pytest.raises(FileException, match="invalid file name"):
            check_file(file, IMAGE_MIMETYPES)

    def test_it_raises_error_if_extension_is_invalid(self) -> None:
        file = FileStorage(filename="invalid.bmp", stream=BytesIO())

        with pytest.raises(FileException, match="file extension not allowed"):
            check_file(file, IMAGE_MIMETYPES)

    def test_it_raises_error_if_content_is_invalid(self) -> None:
        file = FileStorage(
            filename="invalid.py.gpx", stream=BytesIO(b"import os")
        )

        with pytest.raises(FileException, match="invalid file"):
            check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

    def test_it_raises_error_when_image_can_not_be_read(self) -> None:
        file = FileStorage(filename="image.jpg", stream=BytesIO())

        with pytest.raises(FileException, match="invalid file"):
            check_file(file, IMAGE_MIMETYPES)

    def test_it_returns_extension_when_image_file_is_valid(
        self, app: "Flask"
    ) -> None:
        file = self.get_image_file_storage(app)

        extension = check_file(file, IMAGE_MIMETYPES)

        assert extension == "png"

    def test_it_returns_extension_when_gpx_file_is_valid(
        self, app: "Flask", gpx_file: str
    ) -> None:
        file = self.get_text_file_storage(content=gpx_file)

        extension = check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

        assert extension == "gpx"

    def test_it_returns_extension_when_tcx_file_is_valid(
        self, app: "Flask", tcx_with_one_lap_and_one_track: str
    ) -> None:
        file = self.get_text_file_storage(
            content=tcx_with_one_lap_and_one_track, file_name="workout.tcx"
        )

        extension = check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

        assert extension == "tcx"

    def test_it_returns_extension_when_kml_file_is_valid(
        self, app: "Flask", kml_2_3_with_one_track: str
    ) -> None:
        file = self.get_text_file_storage(
            content=kml_2_3_with_one_track, file_name="workout.kml"
        )

        extension = check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

        assert extension == "kml"

    def test_it_returns_extension_when_kmz_file_is_valid(
        self, app: "Flask"
    ) -> None:
        file = self.get_file_storage(app, file_name="example.kmz")

        extension = check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

        assert extension == "kmz"

    def test_it_returns_extension_when_fit_file_is_invalid(
        self, app: "Flask"
    ) -> None:
        file = FileStorage(
            filename="invalid.fit", stream=BytesIO(b"import os")
        )

        with pytest.raises(FileException, match="invalid file"):
            check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

    def test_it_returns_extension_when_fit_file_is_valid(
        self, app: "Flask"
    ) -> None:
        file = self.get_file_storage(app, file_name="example.fit")

        extension = check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

        assert extension == "fit"

    def test_it_returns_extension_when_zip_file_is_invalid(
        self, app: "Flask"
    ) -> None:
        file = FileStorage(
            filename="invalid.zip", stream=BytesIO(b"import os")
        )

        with pytest.raises(FileException, match="invalid file"):
            check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

    def test_it_returns_extension_when_zip_file_is_valid(
        self, app: "Flask"
    ) -> None:
        file = self.get_file_storage(
            app, file_name="gpx_multiple_extensions.zip"
        )

        extension = check_file(file, WORKOUT_FILE_DETECTED_MIMETYPES)

        assert extension == "zip"


class TestGetImageWithoutExif(ImageMixin):
    def test_it_creates_new_image_without_exif_data(
        self, app: "Flask"
    ) -> None:
        image_file_name = "image_with_gps_exif.jpg"
        image = self.get_image_file_storage(app, image_file_name)

        new_image = get_image_without_exif(image)

        # exif data is removed
        assert dict(new_image.getexif()) == {}
        # new image is the same
        assert not ImageChops.difference(
            Image.open(
                os.path.join(app.root_path, f"tests/files/{image_file_name}")
            ),
            new_image,
        ).getbbox()

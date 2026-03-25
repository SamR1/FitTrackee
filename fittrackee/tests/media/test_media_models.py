import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from time_machine import travel

from fittrackee import db
from fittrackee.files import get_absolute_file_path
from fittrackee.media.models import Media
from fittrackee.tests.mixins import RandomMixin
from fittrackee.utils import encode_uuid

from ..mixins import MediaMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class TestMediaModel(MediaMixin, RandomMixin):
    def test_it_creates_media_in_database_with_minimal_data(
        self, app: "Flask", user_1: "User"
    ) -> None:
        now = datetime.now(timezone.utc)
        with travel(now, tick=False):
            media = Media(
                user_id=user_1.id,
                file_name="img.jpg",
                file_size=1024,
            )
        db.session.add(media)
        db.session.commit()

        assert media.created_at == now
        assert media.description == ""
        assert media.file_size == 1024
        assert media.user_id == user_1.id
        assert media.workout_id is None
        assert isinstance(media.uuid, UUID)

    def test_it_creates_media_with_all_data(
        self, app: "Flask", user_1: "User", workout_cycling_user_1: "Workout"
    ) -> None:
        now = datetime.now(timezone.utc)
        media = Media(
            user_id=user_1.id,
            file_name="img.gif",
            file_size=1024,
            created_at=now,
            workout_id=workout_cycling_user_1.id,
        )
        db.session.add(media)
        db.session.commit()

        assert media.created_at == now
        assert media.description == ""
        assert media.file_size == 1024
        assert media.user_id == user_1.id
        assert media.workout_id == workout_cycling_user_1.id

    def test_short_id_returns_encoded_workout_uuid(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)

        assert media.short_id == encode_uuid(media.uuid)

    def test_file_path_returns_media_file_path(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)

        assert media.file_path == f"media/{user_1.id}/{media.file_name}"

    def test_url_returns_media_url(self, app: "Flask", user_1: "User") -> None:
        media = self.create_media(user_1)

        assert media.url == f"{app.config['UI_URL']}/media/{media.file_name}"

    def test_it_deletes_image_on_media_delete(
        self, app: "Flask", user_1: "User"
    ) -> None:
        os.makedirs(
            os.path.join(app.config["UPLOAD_FOLDER"], "media", str(user_1.id)),
            exist_ok=True,
        )
        media = self.create_media(user_1)
        absolute_path = get_absolute_file_path(media.file_path)
        open(absolute_path, "x")

        db.session.delete(media)
        db.session.commit()

        assert os.path.isfile(absolute_path) is False

    def test_serialize_returns_serialized_media(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        media.description = self.random_string()

        serialized_media = media.serialize()

        assert serialized_media == {
            "id": media.short_id,
            "description": media.description,
            "url": media.url,
        }

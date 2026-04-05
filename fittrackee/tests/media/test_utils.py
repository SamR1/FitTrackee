import os
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from fittrackee import db
from fittrackee.media.models import Media
from fittrackee.media.utils import clean_orphan_media_attachments

from ..mixins import MediaMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Workout


class TestCleanOrphanMediaAttachments(MediaMixin):
    def test_it_returns_0_when_no_media_attachments(
        self, app: "Flask"
    ) -> None:
        counts = clean_orphan_media_attachments(days=7)

        assert counts == {"deleted_media_attachments": 0, "freed_space": 0}

    def test_it_does_not_delete_media_associated_to_workout(
        self, app: "Flask", user_1: "User", workout_cycling_user_1: "Workout"
    ) -> None:
        media, media_file_path = self.create_and_store_media(
            app, user_1, workout_cycling_user_1.id
        )

        clean_orphan_media_attachments(days=0)

        db.session.refresh(media)
        assert media is not None
        assert os.path.isfile(media_file_path)

    def test_it_does_not_delete_media_created_after_limit(
        self, app: "Flask", user_1: "User", workout_cycling_user_1: "Workout"
    ) -> None:
        media, media_file_path = self.create_and_store_media(app, user_1)

        clean_orphan_media_attachments(days=1)

        db.session.refresh(media)
        assert media is not None
        assert os.path.isfile(media_file_path)

    def test_it_deletes_media_when_days_equal_zero(
        self, app: "Flask", user_1: "User", workout_cycling_user_1: "Workout"
    ) -> None:
        _, media_file_path = self.create_and_store_media(app, user_1)

        clean_orphan_media_attachments(days=0)

        assert Media.query.count() == 0
        assert os.path.isfile(media_file_path) is False

    def test_it_deletes_media_created_before_limit(
        self, app: "Flask", user_1: "User", workout_cycling_user_1: "Workout"
    ) -> None:
        media, media_file_path = self.create_and_store_media(app, user_1)
        media.created_at = datetime.now(tz=timezone.utc) - timedelta(
            days=2, minutes=1
        )
        db.session.commit()

        counts = clean_orphan_media_attachments(days=2)

        assert Media.query.count() == 0
        assert os.path.isfile(media_file_path) is False
        assert counts == {
            "deleted_media_attachments": 1,
            "freed_space": media.file_size,
        }

import os
from datetime import datetime, timedelta, timezone
from typing import Dict

from flask import current_app

from fittrackee import db
from fittrackee.media.models import Media


def clean_orphan_media_attachments(days: int) -> Dict:
    counts = {"deleted_media_attachments": 0, "freed_space": 0}
    limit = datetime.now(timezone.utc) - timedelta(days=days)
    orphan_media_attachments = Media.query.filter(
        Media.created_at < limit,
        Media.workout_id == None,  # noqa: E711
    ).all()

    if not orphan_media_attachments:
        return counts

    for media in orphan_media_attachments:
        if os.path.exists(
            os.path.join(current_app.config["UPLOAD_FOLDER"], media.file_path)
        ):
            counts["freed_space"] += (
                media.file_size + media.thumbnail_file_size
            )
        # Media is deleted when row is deleted
        db.session.delete(media)
        counts["deleted_media_attachments"] += 1

    db.session.commit()
    return counts

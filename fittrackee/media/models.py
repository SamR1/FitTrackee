import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from flask import current_app
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import text

from fittrackee import BaseModel, appLog, db
from fittrackee.database import TZDateTime
from fittrackee.dates import aware_utc_now
from fittrackee.files import get_absolute_file_path
from fittrackee.utils import encode_uuid

MEDIA_DESCRIPTION_MAX_CHARACTERS = 1500


class Media(BaseModel):
    __tablename__ = "media"

    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        server_default=text("gen_random_uuid ()"),
        nullable=False,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workout_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=aware_utc_now, index=True
    )
    file_name: Mapped[str] = mapped_column(
        db.String(255), nullable=False, index=True, unique=True
    )
    file_size: Mapped[int] = mapped_column()
    file_content_type: Mapped[str] = mapped_column(
        db.String(10), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        db.String(MEDIA_DESCRIPTION_MAX_CHARACTERS),
        nullable=False,
        server_default=text("''"),
    )
    meta: Mapped[Dict] = mapped_column(
        postgresql.JSONB, nullable=False, server_default="{}"
    )

    def __init__(
        self,
        user_id: int,
        file_name: str,
        file_size: int,
        file_content_type: str,
        created_at: Optional[datetime] = None,
        workout_id: Optional[int] = None,
    ):
        self.user_id = user_id
        self.file_name = file_name
        self.file_size = file_size
        self.file_content_type = file_content_type
        self.created_at = (
            created_at if created_at else datetime.now(timezone.utc)
        )
        self.workout_id = workout_id

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    @property
    def url(self) -> str:
        return f"{current_app.config['UI_URL']}/media/{self.file_name}"

    @property
    def thumbnail(self) -> str:
        return self.meta["thumbnail"]["file_name"]

    @property
    def thumbnail_file_size(self) -> int:
        return self.meta["thumbnail"]["file_size"]

    @property
    def thumbnail_url(self) -> str:
        return f"{current_app.config['UI_URL']}/media/{self.thumbnail}"

    @property
    def file_path(self) -> str:
        return os.path.join("media", str(self.user_id), self.file_name)

    @property
    def thumbnail_file_path(self) -> str:
        return os.path.join("media", str(self.user_id), self.thumbnail)

    def serialize(self, can_see_map_data: bool = False) -> Dict:
        return {
            "id": self.short_id,
            "description": self.description,
            "meta": {
                "coordinates": (
                    self.meta.get("coordinates", None)
                    if can_see_map_data
                    else None
                ),
                "thumbnail_url": self.thumbnail_url,
            },
            "url": self.url,
        }


@listens_for(Media, "after_delete")
def on_media_delete(
    mapper: Mapper, connection: Connection, old_media: "Media"
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        try:
            os.remove(
                get_absolute_file_path(
                    os.path.join(
                        "media", str(old_media.user_id), old_media.file_name
                    )
                )
            )
        except OSError:
            appLog.error("file not found when deleting media")

        if old_media.meta.get("thumbnail", {}).get("file_name"):
            try:
                os.remove(
                    get_absolute_file_path(
                        os.path.join(
                            "media",
                            str(old_media.user_id),
                            old_media.meta["thumbnail"]["file_name"],
                        )
                    )
                )
            except OSError:
                appLog.error("thumbnail file not found when deleting media")

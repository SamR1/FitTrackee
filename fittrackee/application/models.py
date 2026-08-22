import os
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

from flask import current_app
from sqlalchemy import ARRAY, cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import text

from fittrackee import BaseModel, db
from fittrackee.database import TZDateTime
from fittrackee.users.models import User

if TYPE_CHECKING:
    from .tile_servers import TileProviderBase


class AppConfig(BaseModel):
    __tablename__ = "app_config"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    max_users: Mapped[int] = mapped_column(default=0, nullable=False)
    file_sync_limit_import: Mapped[int] = mapped_column(
        default=10, nullable=False
    )
    max_single_file_size: Mapped[int] = mapped_column(
        default=1048576, nullable=False
    )
    max_zip_file_size: Mapped[int] = mapped_column(
        default=10485760, nullable=False
    )
    admin_contact: Mapped[Optional[str]] = mapped_column(
        db.String(255), nullable=True
    )
    privacy_policy_date: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    privacy_policy: Mapped[Optional[str]] = mapped_column(
        db.Text, nullable=True
    )
    about: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    stats_workouts_limit: Mapped[int] = mapped_column(
        default=10000, nullable=False
    )
    file_limit_import: Mapped[int] = mapped_column(default=10, nullable=False)
    global_map_workouts_limit: Mapped[int] = mapped_column(
        server_default="10000", nullable=False
    )
    max_image_size: Mapped[int] = mapped_column(
        server_default="5242880", nullable=False
    )
    tile_providers: Mapped[list[str]] = mapped_column(
        ARRAY(db.String),
        server_default=cast(postgresql.array(["osm"]), ARRAY(db.String)),
    )
    default_tile_provider: Mapped[Optional[str]] = mapped_column(
        db.String(25), nullable=False, server_default="osm"
    )

    @property
    def is_registration_enabled(self) -> bool:
        result = db.session.execute(text("SELECT COUNT(*) FROM users;"))
        nb_users = result.one()[0]
        return self.max_users == 0 or nb_users < self.max_users

    @property
    def available_tile_providers(self) -> Dict[str, "TileProviderBase"]:
        available_tile_providers = {}
        if self.tile_providers:
            available_tile_providers = {
                key: current_app.config["TILE_PROVIDERS"][key]
                for key in self.tile_providers
                if not current_app.config["TILE_PROVIDERS"][
                    key
                ].api_key_is_missing
            }
        if not available_tile_providers:
            available_tile_providers = {
                "osm": current_app.config["TILE_PROVIDERS"]["osm"]
            }

        return available_tile_providers

    @property
    def elevation_services(self) -> Dict:
        return {
            "open_elevation": (
                current_app.config["OPEN_ELEVATION_API_URL"] != ""
            ),
            "valhalla": current_app.config["VALHALLA_API_URL"] != "",
        }

    def serialize(self) -> Dict:
        weather_provider = os.getenv("WEATHER_API_PROVIDER", "").lower()
        return {
            "about": self.about,
            "admin_contact": self.admin_contact,
            "elevation_services": self.elevation_services,
            "enable_heatmap": current_app.config["ENABLE_HEATMAP"],
            "file_limit_import": self.file_limit_import,
            "file_sync_limit_import": self.file_sync_limit_import,
            "is_email_sending_enabled": current_app.config["CAN_SEND_EMAILS"],
            "is_registration_enabled": self.is_registration_enabled,
            "global_map_workouts_limit": self.global_map_workouts_limit,
            "max_image_size": self.max_image_size,
            "max_single_file_size": self.max_single_file_size,
            "max_zip_file_size": self.max_zip_file_size,
            "max_users": self.max_users,
            "privacy_policy": self.privacy_policy,
            "privacy_policy_date": (
                self.privacy_policy_date
                if self.privacy_policy
                else current_app.config["DEFAULT_PRIVACY_POLICY_DATA"]
            ),
            "stats_workouts_limit": self.stats_workouts_limit,
            "version": current_app.config["VERSION"],
            "weather_provider": (
                weather_provider
                if weather_provider in ["visualcrossing"]
                else None
            ),
        }


def update_app_config() -> None:
    config = AppConfig.query.first()
    if config:
        current_app.config["is_registration_enabled"] = (
            config.is_registration_enabled
        )


@listens_for(User, "after_insert")
def on_user_insert(mapper: Mapper, connection: Connection, user: User) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        update_app_config()


@listens_for(User, "after_delete")
def on_user_delete(
    mapper: Mapper, connection: Connection, old_user: User
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        update_app_config()

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import text
from sqlalchemy.types import Enum

from fittrackee import BaseModel, db
from fittrackee.database import TZDateTime
from fittrackee.dates import aware_utc_now
from fittrackee.utils import encode_uuid
from fittrackee.visibility_levels import VisibilityLevel, can_view

if TYPE_CHECKING:
    from fittrackee.users.models import User, UserSportPreference
    from fittrackee.workouts.models import Workout

from .exceptions import EquipmentForbiddenException

WorkoutEquipment = db.Table(
    "workout_equipments",
    db.Column(
        "workout_id",
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "equipment_id",
        db.Integer,
        db.ForeignKey("equipments.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


class Equipment(BaseModel):
    __tablename__ = "equipments"
    # a single user can only have one equipment with the same label
    __table_args__ = (
        UniqueConstraint(
            "label",
            "user_id",
            name="equipment_user_label_unique",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id"), index=True, nullable=False
    )
    label: Mapped[str] = mapped_column(
        db.String(50), unique=False, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        db.String(200), default=None, nullable=True
    )
    equipment_type_id: Mapped[int] = mapped_column(
        db.ForeignKey("equipment_types.id")
    )
    creation_date: Mapped[datetime] = mapped_column(
        TZDateTime, default=aware_utc_now
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    total_distance: Mapped[float] = mapped_column(
        db.Numeric(10, 3),
        nullable=False,
        server_default=text("0.0"),  # kilometers
    )
    total_duration: Mapped[timedelta] = mapped_column(
        db.Interval, nullable=False, server_default=text("'00:00:00'")
    )
    total_moving: Mapped[timedelta] = mapped_column(
        db.Interval, nullable=False, server_default=text("'00:00:00'")
    )
    total_workouts: Mapped[int] = mapped_column(
        nullable=False, server_default=text("0")
    )
    visibility: Mapped[VisibilityLevel] = mapped_column(
        Enum(VisibilityLevel, name="visibility_levels"),
        server_default="PRIVATE",
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User", lazy="select", single_parent=True
    )
    workouts: Mapped[List["Workout"]] = relationship(
        "Workout", secondary=WorkoutEquipment, back_populates="equipments"
    )
    equipment_type: Mapped["EquipmentType"] = relationship(
        "EquipmentType", lazy="joined", single_parent=True
    )
    default_for_sports: Mapped[List["UserSportPreference"]] = relationship(
        "UserSportPreference",
        primaryjoin=(
            "Equipment.id == "
            "users_sports_preferences_equipments.c.equipment_id"
        ),
        secondaryjoin="""and_(
            UserSportPreference.user_id == 
            users_sports_preferences_equipments.c.user_id,
            UserSportPreference.sport_id == 
            users_sports_preferences_equipments.c.sport_id,
        )""",
        secondary="users_sports_preferences_equipments",
        lazy="select",
        back_populates="default_equipments",
    )

    def __repr__(self) -> str:
        return f"<Equipment {self.id!r} {self.label!r}>"

    def __init__(
        self,
        label: str,
        equipment_type_id: int,
        description: str,
        user_id: int,
        is_active: bool,
    ) -> None:
        self.label = label
        self.equipment_type_id = equipment_type_id
        self.description = description
        self.user_id = user_id
        self.is_active = is_active

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def serialize(self, *, current_user: Optional["User"]) -> Dict:
        if not can_view(self, "visibility", current_user):
            raise EquipmentForbiddenException()

        serialized_equipment = {
            "label": self.label,
            "is_active": self.is_active,
            "equipment_type": self.equipment_type.serialize(),
        }

        if not current_user or current_user.id != self.user_id:
            return serialized_equipment

        serialized_equipment = {
            **serialized_equipment,
            "id": self.short_id,
            "user_id": self.user_id,
            "description": self.description,
            "default_for_sport_ids": [
                sport_preference.sport_id
                for sport_preference in self.default_for_sports
            ],
            "creation_date": self.creation_date,
            "total_distance": (
                0.0
                if self.total_distance is None
                else float(self.total_distance)
            ),
            "total_duration": (
                "0:00:00"
                if self.total_duration is None
                else str(self.total_duration)
            ),
            "total_moving": (
                "0:00:00"
                if self.total_moving is None
                else str(self.total_moving)
            ),
            "visibility": self.visibility,
            "workouts_count": (
                0 if self.total_workouts is None else self.total_workouts
            ),
        }
        return serialized_equipment


class EquipmentType(BaseModel):
    __tablename__ = "equipment_types"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(
        db.String(50), unique=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    equipments: Mapped[List["Equipment"]] = relationship(
        "Equipment", lazy="select", back_populates="equipment_type"
    )

    def __repr__(self) -> str:
        return f"<EquipmentType {self.label!r}>"

    def __init__(self, label: str, is_active: bool) -> None:
        self.label = label
        self.is_active = is_active

    def serialize(self, is_admin: bool = False) -> Dict:
        serialized_equipment_type = {
            "id": self.id,
            "label": self.label,
            "is_active": self.is_active,
        }
        if is_admin:
            serialized_equipment_type["has_equipments"] = (
                len(self.equipments) > 0
            )
        return serialized_equipment_type

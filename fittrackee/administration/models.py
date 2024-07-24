from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session

from fittrackee import BaseModel, db
from fittrackee.users.models import Notification, User
from fittrackee.utils import encode_uuid

from .exceptions import (
    AdminActionAppealForbiddenException,
    AdminActionForbiddenException,
    InvalidAdminActionAppealException,
    InvalidAdminActionAppealUserException,
    InvalidAdminActionException,
)

REPORT_ACTION_TYPES = [
    "report_reopening",
    "report_resolution",
]
USER_ACTION_TYPES = [
    "user_suspension",
    "user_unsuspension",
    "user_warning",
]
COMMENT_ACTION_TYPES = [
    "comment_suspension",
    "comment_unsuspension",
]
WORKOUT_ACTION_TYPES = [
    "workout_suspension",
    "workout_unsuspension",
]
OBJECTS_ADMIN_ACTION_TYPES = (
    COMMENT_ACTION_TYPES + USER_ACTION_TYPES + WORKOUT_ACTION_TYPES
)
ADMIN_ACTION_TYPES = REPORT_ACTION_TYPES + OBJECTS_ADMIN_ACTION_TYPES


class AdminAction(BaseModel):
    __tablename__ = "admin_actions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    admin_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,  # to keep log if an admin is deleted
    )
    report_id = db.Column(
        db.Integer,
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    comment_id = db.Column(
        db.Integer,
        db.ForeignKey('comments.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    action_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(), nullable=True)

    admin_user = db.relationship(
        "User",
        primaryjoin=admin_user_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    user = db.relationship(
        "User",
        primaryjoin=user_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    appeal = db.relationship(
        "AdminActionAppeal",
        uselist=False,
        backref=db.backref("action", lazy='joined', single_parent=True),
    )
    comment = db.relationship(
        'Comment',
        lazy=True,
        backref=db.backref('comment_admin_action', lazy='select'),
    )
    workout = db.relationship(
        'Workout',
        lazy=True,
        backref=db.backref('workout_admin_action', lazy='select'),
    )

    def __init__(
        self,
        action_type: str,
        admin_user_id: int,
        user_id: Optional[int] = None,
        report_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        workout_id: Optional[int] = None,
        reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        if action_type not in ADMIN_ACTION_TYPES:
            raise InvalidAdminActionException()
        if action_type in REPORT_ACTION_TYPES and not report_id:
            raise InvalidAdminActionException()
        if action_type in OBJECTS_ADMIN_ACTION_TYPES and not user_id:
            raise InvalidAdminActionException()
        if action_type in WORKOUT_ACTION_TYPES and not workout_id:
            raise InvalidAdminActionException()
        if action_type in COMMENT_ACTION_TYPES and not comment_id:
            raise InvalidAdminActionException()

        self.action_type = action_type
        self.admin_user_id = admin_user_id
        self.created_at = created_at if created_at else datetime.utcnow()
        self.comment_id = (
            comment_id if action_type in COMMENT_ACTION_TYPES else None
        )
        self.reason = reason
        self.report_id = report_id
        self.user_id = (
            user_id if action_type in OBJECTS_ADMIN_ACTION_TYPES else None
        )
        self.workout_id = (
            workout_id if action_type in WORKOUT_ACTION_TYPES else None
        )

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def serialize(self, current_user: User, full: bool = True) -> Dict:
        if not current_user.admin and current_user.id != self.user_id:
            raise AdminActionForbiddenException()
        action = {
            "action_type": self.action_type,
            "appeal": (
                self.appeal.serialize(current_user) if self.appeal else None
            ),
            "created_at": self.created_at,
            "id": self.short_id,
            "reason": self.reason,
        }

        if current_user.admin:
            action["admin_user"] = self.admin_user.serialize(
                current_user, light=True
            )
            action["user"] = (
                self.user.serialize(current_user, light=True)
                if self.user
                else None
            )
        if not full:
            return action

        if current_user.admin:
            action = {
                **action,
                "report_id": self.report_id,
                "comment": (
                    self.comment.serialize(user=current_user, for_report=True)
                    if self.comment_id
                    else None
                ),
                "workout": (
                    self.workout.serialize(user=current_user, for_report=True)
                    if self.workout_id
                    else None
                ),
            }
        else:
            action["comment"] = (
                self.comment.serialize(user=current_user)
                if self.comment_id
                else None
            )
            action["workout"] = (
                self.workout.serialize(user=current_user)
                if self.workout_id
                else None
            )

        return action


class AdminActionAppeal(BaseModel):
    __tablename__ = "admin_action_appeals"
    __table_args__ = (
        db.UniqueConstraint(
            'action_id', 'user_id', name='action_id_user_id_unique'
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    action_id = db.Column(
        db.Integer,
        db.ForeignKey("admin_actions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    admin_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at = db.Column(db.DateTime)
    approved = db.Column(db.Boolean, nullable=True)
    text = db.Column(db.String(), nullable=False)
    reason = db.Column(db.String(), nullable=True)

    admin_user = db.relationship(
        "User",
        primaryjoin=admin_user_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    user = db.relationship(
        "User",
        primaryjoin=user_id == User.id,
        lazy="joined",
        single_parent=True,
    )

    def __init__(
        self,
        action_id: int,
        user_id: int,
        text: str,
        created_at: Optional[datetime] = None,
    ):
        action = AdminAction.query.filter_by(id=action_id).first()
        if action.action_type not in [
            "comment_suspension",
            "user_suspension",
            "user_warning",
            "workout_suspension",
        ]:
            raise InvalidAdminActionAppealException()
        if action.user_id != user_id:
            raise InvalidAdminActionAppealUserException()
        self.action_id = action_id
        self.created_at = created_at if created_at else datetime.utcnow()
        self.text = text
        self.user_id = user_id

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def serialize(self, current_user: User) -> Dict:
        if not current_user.admin and current_user.id != self.user_id:
            raise AdminActionAppealForbiddenException()
        appeal = {
            "approved": self.approved,
            "created_at": self.created_at,
            "id": self.short_id,
            "reason": self.reason,
            "text": self.text,
            "updated_at": self.updated_at,
        }
        if current_user.admin:
            appeal["admin_user"] = (
                self.admin_user.serialize(current_user, light=True)
                if self.admin_user
                else None
            )
            appeal["user"] = self.user.serialize(current_user, light=True)
        return appeal


@listens_for(AdminAction, 'after_insert')
def on_admin_insert(
    mapper: Mapper, connection: Connection, new_action: AdminAction
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.administration.models import (
            COMMENT_ACTION_TYPES,
            WORKOUT_ACTION_TYPES,
        )

        if (
            new_action.action_type
            in COMMENT_ACTION_TYPES + WORKOUT_ACTION_TYPES + ["user_warning"]
        ):
            notification = Notification(
                from_user_id=new_action.admin_user_id,
                to_user_id=new_action.user_id,
                created_at=new_action.created_at,
                event_type=new_action.action_type,
                event_object_id=new_action.id,
            )
            session.add(notification)


@listens_for(AdminActionAppeal, 'after_insert')
def on_admin_action_appeal_insert(
    mapper: Mapper, connection: Connection, new_appeal: AdminActionAppeal
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import Notification, User

        for admin in User.query.filter(
            User.admin == True,  # noqa
            User.id != new_appeal.user_id,
            User.is_active == True,  # noqa
        ).all():
            notification = Notification(
                from_user_id=new_appeal.user_id,
                to_user_id=admin.id,
                created_at=new_appeal.created_at,
                event_type='suspension_appeal',
                event_object_id=new_appeal.id,
            )
            session.add(notification)

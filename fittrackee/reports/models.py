from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, Mapper, Session, mapped_column, relationship

from fittrackee import BaseModel, db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment
from fittrackee.database import TZDateTime
from fittrackee.dates import aware_utc_now
from fittrackee.users.models import Notification, User
from fittrackee.users.roles import UserRole
from fittrackee.utils import encode_uuid
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Workout

from .exceptions import (
    InvalidReportActionAppealException,
    InvalidReportActionAppealUserException,
    InvalidReportActionException,
    InvalidReporterException,
    InvalidReportException,
    ReportActionAppealForbiddenException,
    ReportActionForbiddenException,
    ReportCommentForbiddenException,
    ReportForbiddenException,
)

REPORT_OBJECT_TYPES = [
    "comment",
    "user",
    "workout",
]
REPORT_ACTION_TYPES = [
    "report_reopening",
    "report_resolution",
]
USER_ACTION_TYPES = [
    "user_suspension",
    "user_unsuspension",
    "user_warning",
]
ALL_USER_ACTION_TYPES = [
    *USER_ACTION_TYPES,
    "user_warning_lifting",
]
COMMENT_ACTION_TYPES = [
    "comment_suspension",
    "comment_unsuspension",
]
WORKOUT_ACTION_TYPES = [
    "workout_suspension",
    "workout_unsuspension",
]
OBJECTS_ACTION_TYPES = (
    COMMENT_ACTION_TYPES + ALL_USER_ACTION_TYPES + WORKOUT_ACTION_TYPES
)
ALL_ACTION_TYPES = REPORT_ACTION_TYPES + OBJECTS_ACTION_TYPES


class Report(BaseModel):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=aware_utc_now
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    reported_by: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reported_comment_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("comments.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reported_user_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    reported_workout_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("workouts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    resolved_by: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    object_type: Mapped[str] = mapped_column(
        db.String(50), nullable=False, index=True
    )
    note: Mapped[str] = mapped_column(db.String(), nullable=False)

    reported_comment: Mapped["Comment"] = relationship("Comment", lazy=True)
    reported_user: Mapped["User"] = relationship(
        "User", primaryjoin=reported_user_id == User.id
    )
    reported_workout: Mapped["Workout"] = relationship("Workout", lazy=True)
    reporter: Mapped["User"] = relationship(
        "User", primaryjoin=reported_by == User.id
    )
    resolver: Mapped["User"] = relationship(
        "User", primaryjoin=resolved_by == User.id
    )
    comments: Mapped[List["ReportComment"]] = relationship(
        "ReportComment", back_populates="report"
    )
    report_actions: Mapped[List["ReportAction"]] = relationship(
        "ReportAction",
        lazy=True,
        back_populates="report",
        order_by="ReportAction.created_at.asc()",
    )

    @property
    def reported_object(self) -> Union[Comment, None, User, Workout]:
        # util method, used by tests
        if self.object_type == "comment":
            return self.reported_comment
        if self.object_type == "user":
            return self.reported_user
        if self.object_type == "workout":
            return self.reported_workout
        return None

    @property
    def is_reported_user_warned(self) -> bool:
        return (
            ReportAction.query.filter_by(
                action_type="user_warning",
                report_id=self.id,
                user_id=self.reported_user_id,
            ).first()
            is not None
        )

    def __init__(
        self,
        note: str,
        reported_by: int,
        reported_object: Union[Comment, User, Workout],
        created_at: Optional[datetime] = None,
    ):
        object_type = reported_object.__class__.__name__.lower()
        if object_type not in REPORT_OBJECT_TYPES:
            raise InvalidReportException()
        user_id = (
            reported_object.id
            if isinstance(reported_object, User)
            else reported_object.user_id
        )
        if user_id == reported_by:
            raise InvalidReporterException()

        self.created_at = (
            created_at if created_at else datetime.now(timezone.utc)
        )
        self.note = note
        self.object_type = object_type
        self.reported_by = reported_by
        self.reported_comment_id = (
            reported_object.id
            if isinstance(reported_object, Comment)
            else None
        )
        self.reported_user_id = user_id
        self.reported_workout_id = (
            reported_object.id
            if isinstance(reported_object, Workout)
            else None
        )
        self.resolved = False

    def serialize(self, current_user: User, full: bool = False) -> Dict:
        if (
            not current_user.has_moderator_rights
            and self.reported_by != current_user.id
        ):
            raise ReportForbiddenException()

        try:
            reported_comment = (
                self.reported_comment.serialize(current_user, for_report=True)
                if self.reported_comment_id
                else None
            )
        except CommentForbiddenException:
            reported_comment = {"id": "_COMMENT_UNAVAILABLE_"}

        try:
            reported_workout = (
                self.reported_workout.serialize(
                    user=current_user, for_report=True
                )
                if self.reported_workout
                else None
            )
        except WorkoutForbiddenException:
            reported_workout = {"id": "_WORKOUT_UNAVAILABLE_"}

        report = {
            "created_at": self.created_at,
            "id": self.id,
            "is_reported_user_warned": self.is_reported_user_warned,
            "note": self.note,
            "object_type": self.object_type,
            "reported_by": (
                self.reporter.serialize(current_user=current_user)
                if self.reported_by
                else None
            ),
            "reported_comment": reported_comment,
            "reported_user": (
                self.reported_user.serialize(current_user=current_user)
                if self.reported_user_id
                else None
            ),
            "reported_workout": reported_workout,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }
        if current_user.has_moderator_rights:
            if full:
                report["report_actions"] = [
                    action.serialize(current_user, full=False)
                    for action in self.report_actions
                ]
                report["comments"] = [
                    comment.serialize(current_user)
                    for comment in self.comments
                ]
            report["resolved_by"] = (
                None
                if self.resolved_by is None
                else self.resolver.serialize(current_user=current_user)
            )
            report["updated_at"] = self.updated_at
        return report


@listens_for(Report, "after_insert")
def on_report_insert(
    mapper: Mapper, connection: Connection, new_report: Report
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        if not new_report.reported_by:
            return

        from fittrackee.users.models import Notification, User

        for admin in User.query.filter(
            User.role >= UserRole.MODERATOR.value,
            User.id != new_report.reported_by,
            User.is_active == True,  # noqa
        ).all():
            notification = Notification(
                from_user_id=new_report.reported_by,
                to_user_id=admin.id,
                created_at=new_report.created_at,
                event_type="report",
                event_object_id=new_report.id,
            )
            session.add(notification)


class ReportComment(BaseModel):
    __tablename__ = "report_comments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=aware_utc_now
    )
    report_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    comment: Mapped[str] = mapped_column(db.String(), nullable=False)

    user: Mapped["User"] = relationship("User")
    report: Mapped["Report"] = relationship(
        "Report",
        lazy="select",
        single_parent=True,
    )

    def __init__(
        self,
        report_id: int,
        user_id: int,
        comment: str,
        created_at: Optional[datetime] = None,
    ):
        self.created_at = (
            created_at if created_at else datetime.now(timezone.utc)
        )
        self.comment = comment
        self.report_id = report_id
        self.user_id = user_id

    def serialize(self, current_user: User) -> Dict:
        if not current_user.has_moderator_rights:
            raise ReportCommentForbiddenException()
        return {
            "created_at": self.created_at,
            "comment": self.comment,
            "id": self.id,
            "report_id": self.report_id,
            "user": self.user.serialize(current_user=current_user),
        }


class ReportAction(BaseModel):
    __tablename__ = "report_actions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=aware_utc_now, index=True
    )
    moderator_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,  # to keep log if an moderator is deleted
    )
    report_id: Mapped[int] = mapped_column(
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    workout_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("workouts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    comment_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("comments.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    action_type: Mapped[str] = mapped_column(db.String(50), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(db.String(), nullable=True)

    moderator: Mapped["User"] = relationship(
        "User",
        primaryjoin=moderator_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        primaryjoin=user_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    appeal: Mapped["ReportActionAppeal"] = relationship(
        "ReportActionAppeal",
        uselist=False,
        back_populates="action",
    )
    comment: Mapped["Comment"] = relationship("Comment", lazy=True)
    workout: Mapped["Workout"] = relationship("Workout", lazy=True)
    report: Mapped["Report"] = relationship(
        "Report", lazy="select", single_parent=True
    )

    def __init__(
        self,
        action_type: str,
        moderator_id: int,
        report_id: int,
        *,
        user_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        workout_id: Optional[int] = None,
        reason: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        if action_type not in ALL_ACTION_TYPES:
            raise InvalidReportActionException()
        if action_type in OBJECTS_ACTION_TYPES and not user_id:
            raise InvalidReportActionException()
        if action_type in WORKOUT_ACTION_TYPES and not workout_id:
            raise InvalidReportActionException()
        if action_type in COMMENT_ACTION_TYPES and not comment_id:
            raise InvalidReportActionException()

        self.action_type = action_type
        self.moderator_id = moderator_id
        self.created_at = (
            created_at if created_at else datetime.now(timezone.utc)
        )
        self.comment_id = (
            comment_id if action_type in COMMENT_ACTION_TYPES else None
        )
        self.reason = reason
        self.report_id = report_id
        self.user_id = user_id if action_type in OBJECTS_ACTION_TYPES else None
        self.workout_id = (
            workout_id if action_type in WORKOUT_ACTION_TYPES else None
        )

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def serialize(self, current_user: User, full: bool = True) -> Dict:
        if (
            not current_user.has_moderator_rights
            and current_user.id != self.user_id
        ):
            raise ReportActionForbiddenException()
        action: Dict[str, Any] = {
            "action_type": self.action_type,
            "appeal": (
                self.appeal.serialize(current_user) if self.appeal else None
            ),
            "created_at": self.created_at,
            "id": self.short_id,
            "reason": self.reason,
        }

        if current_user.has_moderator_rights:
            action["report_id"] = self.report_id
            action["moderator"] = self.moderator.serialize(
                current_user=current_user
            )
            action["user"] = (
                self.user.serialize(current_user=current_user)
                if self.user
                else None
            )
        if not full:
            return action

        if current_user.has_moderator_rights:
            action = {
                **action,
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
            if self.report.object_type == "comment":
                action["comment"] = (
                    self.comment.serialize(user=current_user)
                    if self.comment_id
                    else None
                )
            if self.report.object_type == "workout":
                action["workout"] = (
                    self.workout.serialize(user=current_user)
                    if self.workout_id
                    else None
                )

        return action


class ReportActionAppeal(BaseModel):
    __tablename__ = "report_action_appeals"
    __table_args__ = (
        db.UniqueConstraint(
            "action_id", "user_id", name="action_id_user_id_unique"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    action_id: Mapped[int] = mapped_column(
        db.ForeignKey("report_actions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    moderator_id: Mapped[Optional[int]] = mapped_column(
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=aware_utc_now, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TZDateTime, nullable=True
    )
    approved: Mapped[Optional[bool]] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(db.String(), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(db.String(), nullable=True)

    moderator: Mapped["User"] = relationship(
        "User",
        primaryjoin=moderator_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        primaryjoin=user_id == User.id,
        lazy="joined",
        single_parent=True,
    )
    action: Mapped["ReportAction"] = relationship(
        "ReportAction", lazy="joined", single_parent=True
    )

    def __init__(
        self,
        action_id: int,
        user_id: int,
        text: str,
        created_at: Optional[datetime] = None,
    ):
        action = ReportAction.query.filter_by(id=action_id).one()
        if action.action_type not in [
            "comment_suspension",
            "user_suspension",
            "user_warning",
            "workout_suspension",
        ]:
            raise InvalidReportActionAppealException()
        if action.user_id != user_id:
            raise InvalidReportActionAppealUserException()
        self.action_id = action_id
        self.created_at = (
            created_at if created_at else datetime.now(timezone.utc)
        )
        self.text = text
        self.user_id = user_id

    @property
    def short_id(self) -> str:
        return encode_uuid(self.uuid)

    def serialize(self, current_user: User) -> Dict:
        if (
            not current_user.has_moderator_rights
            and current_user.id != self.user_id
        ):
            raise ReportActionAppealForbiddenException()
        appeal: Dict[str, Any] = {
            "approved": self.approved,
            "created_at": self.created_at,
            "id": self.short_id,
            "reason": self.reason,
            "text": self.text,
            "updated_at": self.updated_at,
        }
        if current_user.has_moderator_rights:
            appeal["moderator"] = (
                self.moderator.serialize(current_user=current_user)
                if self.moderator
                else None
            )
            appeal["user"] = self.user.serialize(current_user=current_user)
        return appeal


@listens_for(ReportAction, "after_insert")
def on_report_action_insert(
    mapper: Mapper, connection: Connection, new_action: ReportAction
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        if not new_action.moderator_id or not new_action.user_id:
            return

        if (
            new_action.action_type
            in COMMENT_ACTION_TYPES
            + WORKOUT_ACTION_TYPES
            + ["user_warning", "user_warning_lifting"]
        ):
            notification = Notification(
                from_user_id=new_action.moderator_id,
                to_user_id=new_action.user_id,
                created_at=new_action.created_at,
                event_type=new_action.action_type,
                event_object_id=new_action.id,
            )
            session.add(notification)


@listens_for(ReportActionAppeal, "after_insert")
def on_report_action_appeal_insert(
    mapper: Mapper, connection: Connection, new_appeal: ReportActionAppeal
) -> None:
    @listens_for(db.Session, "after_flush", once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
        from fittrackee.users.models import Notification, User

        report_action = ReportAction.query.filter_by(
            id=new_appeal.action_id
        ).first()
        if report_action:
            for admin in User.query.filter(
                User.role >= UserRole.MODERATOR.value,
                User.id != new_appeal.user_id,
                User.is_active == True,  # noqa
            ).all():
                notification = Notification(
                    from_user_id=new_appeal.user_id,
                    to_user_id=admin.id,
                    created_at=new_appeal.created_at,
                    event_type=(
                        "user_warning_appeal"
                        if report_action.action_type == "user_warning"
                        else "suspension_appeal"
                    ),
                    event_object_id=new_appeal.id,
                )
                session.add(notification)

from datetime import datetime
from typing import Dict, Optional, Union
from uuid import uuid4

from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapper, Session

from fittrackee import BaseModel, db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment
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
ALL_USER_ACTION_TYPES = USER_ACTION_TYPES + [
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
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    reported_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    reported_comment_id = db.Column(
        db.Integer,
        db.ForeignKey('comments.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    reported_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    reported_workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    resolved_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        index=True,
        nullable=True,
    )
    resolved = db.Column(db.Boolean, default=False, nullable=False)
    object_type = db.Column(db.String(50), nullable=False, index=True)
    note = db.Column(db.String(), nullable=False)

    reported_comment = db.relationship(
        'Comment',
        lazy=True,
        backref=db.backref('comment_reports', lazy='joined'),
    )
    reported_user = db.relationship(
        'User',
        primaryjoin=reported_user_id == User.id,
        backref=db.backref('user_reports', lazy='joined'),
    )
    reported_workout = db.relationship(
        'Workout',
        lazy=True,
        backref=db.backref('workouts_reports', lazy='joined'),
    )
    reporter = db.relationship(
        'User',
        primaryjoin=reported_by == User.id,
        backref=db.backref(
            'user_own_reports',
            lazy='joined',
            single_parent=True,
        ),
    )
    resolver = db.relationship(
        'User',
        primaryjoin=resolved_by == User.id,
        backref=db.backref(
            'user_resolved_reports',
            lazy='joined',
            single_parent=True,
        ),
    )
    comments = db.relationship(
        'ReportComment',
        backref=db.backref('report', lazy='joined'),
    )
    report_actions = db.relationship(
        'ReportAction',
        lazy=True,
        backref=db.backref('report', lazy='joined', single_parent=True),
        order_by='ReportAction.created_at.asc()',
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
            if object_type == "user"
            else reported_object.user_id
        )
        if user_id == reported_by:
            raise InvalidReporterException()

        self.created_at = created_at if created_at else datetime.utcnow()
        self.note = note
        self.object_type = object_type
        self.reported_by = reported_by
        self.reported_comment_id = (
            reported_object.id if object_type == "comment" else None
        )
        self.reported_user_id = user_id
        self.reported_workout_id = (
            reported_object.id if object_type == "workout" else None
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
            reported_comment = '_COMMENT_UNAVAILABLE_'

        try:
            reported_workout = (
                self.reported_workout.serialize(
                    user=current_user, for_report=True
                )
                if self.reported_workout
                else None
            )
        except WorkoutForbiddenException:
            reported_workout = '_WORKOUT_UNAVAILABLE_'

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


@listens_for(Report, 'after_insert')
def on_report_insert(
    mapper: Mapper, connection: Connection, new_report: Report
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
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
                event_type='report',
                event_object_id=new_report.id,
            )
            session.add(notification)


class ReportComment(BaseModel):
    __tablename__ = 'report_comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    report_id = db.Column(
        db.Integer,
        db.ForeignKey('reports.id', ondelete='CASCADE'),
        index=True,
        nullable=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
        nullable=True,
    )
    comment = db.Column(db.String(), nullable=False)

    user = db.relationship(
        'User',
        backref=db.backref('user_report_comments', lazy='joined'),
    )

    def __init__(
        self,
        report_id: int,
        user_id: int,
        comment: str,
        created_at: Optional[datetime] = None,
    ):
        self.created_at = created_at if created_at else datetime.utcnow()
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        postgresql.UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    moderator_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,  # to keep log if an admin is deleted
    )
    report_id = db.Column(
        db.Integer,
        db.ForeignKey("reports.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
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

    moderator = db.relationship(
        "User",
        primaryjoin=moderator_id == User.id,
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
        "ReportActionAppeal",
        uselist=False,
        backref=db.backref("action", lazy='joined', single_parent=True),
    )
    comment = db.relationship(
        'Comment',
        lazy=True,
        backref=db.backref('comment_report_action', lazy='select'),
    )
    workout = db.relationship(
        'Workout',
        lazy=True,
        backref=db.backref('workout_report_action', lazy='select'),
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
        self.created_at = created_at if created_at else datetime.utcnow()
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
        action = {
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


class ReportActionAppeal(BaseModel):
    __tablename__ = "report_action_appeals"
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
        db.ForeignKey("report_actions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    moderator_id = db.Column(
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

    moderator = db.relationship(
        "User",
        primaryjoin=moderator_id == User.id,
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
        action = ReportAction.query.filter_by(id=action_id).first()
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
        self.created_at = created_at if created_at else datetime.utcnow()
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
        appeal = {
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


@listens_for(ReportAction, 'after_insert')
def on_report_action_insert(
    mapper: Mapper, connection: Connection, new_action: ReportAction
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Connection) -> None:
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


@listens_for(ReportActionAppeal, 'after_insert')
def on_report_action_appeal_insert(
    mapper: Mapper, connection: Connection, new_appeal: ReportActionAppeal
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
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
                        'user_warning_appeal'
                        if report_action.action_type == 'user_warning'
                        else 'suspension_appeal'
                    ),
                    event_object_id=new_appeal.id,
                )
                session.add(notification)

from datetime import datetime
from typing import Dict, Optional, Union

from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session

from fittrackee import BaseModel, db
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Workout

from .exceptions import (
    InvalidReporterException,
    InvalidReportException,
    ReportCommentForbiddenException,
    ReportForbiddenException,
)

REPORT_OBJECT_TYPES = [
    "comment",
    "user",
    "workout",
]


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
    admin_actions = db.relationship(
        'AdminAction',
        lazy=True,
        backref=db.backref('report', lazy='joined', single_parent=True),
        order_by='AdminAction.created_at.asc()',
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
        if not current_user.admin and self.reported_by != current_user.id:
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
                self.reported_workout.serialize(current_user, for_report=True)
                if self.reported_workout
                else None
            )
        except WorkoutForbiddenException:
            reported_workout = '_WORKOUT_UNAVAILABLE_'

        report = {
            "created_at": self.created_at,
            "id": self.id,
            "note": self.note,
            "object_type": self.object_type,
            "reported_by": (
                self.reporter.serialize(current_user)
                if self.reported_by
                else None
            ),
            "reported_comment": reported_comment,
            "reported_user": (
                self.reported_user.serialize(
                    current_user if self.object_type == 'user' else None
                )
                if self.reported_user_id
                else None
            ),
            "reported_workout": reported_workout,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }
        if current_user.admin:
            if full:
                report["admin_actions"] = [
                    action.serialize(current_user, full=False)
                    for action in self.admin_actions
                ]
                report["comments"] = [
                    comment.serialize(current_user)
                    for comment in self.comments
                ]
            report["resolved_by"] = (
                None
                if self.resolved_by is None
                else self.resolver.serialize(current_user)
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
            User.admin == True,  # noqa
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
        if not current_user.admin:
            raise ReportCommentForbiddenException()
        return {
            "created_at": self.created_at,
            "comment": self.comment,
            "id": self.id,
            "report_id": self.report_id,
            "user": self.user.serialize(current_user),
        }

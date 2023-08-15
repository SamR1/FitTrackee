from datetime import datetime
from typing import Dict, Optional

from fittrackee import BaseModel, db
from fittrackee.users.models import User

from .exceptions import (
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
    reported_by = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
        nullable=True,
    )
    reported_comment_id = db.Column(
        db.Integer,
        db.ForeignKey('comments.id', ondelete='CASCADE'),
        index=True,
        nullable=True,
    )
    reported_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
        nullable=True,
    )
    reported_workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id', ondelete='CASCADE'),
        index=True,
        nullable=True,
    )
    resolved = db.Column(db.Boolean, default=False, nullable=False)
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

    comments = db.relationship(
        'ReportComment',
        backref=db.backref('report', lazy='joined'),
    )

    def __init__(
        self,
        reported_by: int,
        note: str,
        object_id: int,
        object_type: str,
        created_at: Optional[datetime] = None,
    ):
        if object_type not in REPORT_OBJECT_TYPES:
            raise InvalidReportException()
        setattr(self, f"reported_{object_type}_id", object_id)

        self.created_at = created_at if created_at else datetime.utcnow()
        self.note = note
        self.reported_by = reported_by
        self.resolved = False

    def serialize(self, current_user: User) -> Dict:
        if not current_user.admin and self.reported_by != current_user.id:
            raise ReportForbiddenException()
        report = {
            "created_at": self.created_at,
            "note": self.note,
            "reported_by": self.reporter.serialize(current_user),
            "reported_comment": (
                self.reported_comment.serialize(current_user)
                if self.reported_comment_id
                else None
            ),
            "reported_user": (
                self.reported_user.serialize(current_user)
                if self.reported_user_id
                else None
            ),
            "reported_workout": (
                self.reported_workout.serialize(current_user)
                if self.reported_workout
                else None
            ),
            "resolved": self.resolved,
            "updated_at": self.updated_at,
        }
        if current_user.admin:
            report["comments"] = [
                comment.serialize(current_user) for comment in self.comments
            ]
        return report


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
            "report_id": self.report_id,
            "user": self.user.serialize(current_user),
        }

from datetime import datetime
from typing import Dict, Optional

from fittrackee import BaseModel, db
from fittrackee.users.models import User

from .exceptions import (
    AdminActionForbiddenException,
    InvalidAdminActionException,
)

REPORT_ACTION_TYPES = [
    "report_reopening",
    "report_resolution",
]
# TODO: add other users actions
USER_ACTION_TYPES = [
    "user_suspension",
    "user_unsuspension",
]
ADMIN_ACTION_TYPES = REPORT_ACTION_TYPES + USER_ACTION_TYPES


class AdminAction(BaseModel):
    __tablename__ = "admin_actions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    action_type = db.Column(db.String(50), nullable=False)

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
        action_type: str,
        admin_user_id: int,
        user_id: Optional[int] = None,
        report_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        if action_type not in ADMIN_ACTION_TYPES:
            raise InvalidAdminActionException()
        if action_type in REPORT_ACTION_TYPES and not report_id:
            raise InvalidAdminActionException()
        if action_type in USER_ACTION_TYPES and not user_id:
            raise InvalidAdminActionException()

        self.action_type = action_type
        self.admin_user_id = admin_user_id
        self.created_at = created_at if created_at else datetime.utcnow()
        self.report_id = report_id
        self.user_id = user_id if action_type in USER_ACTION_TYPES else None

    def serialize(self, current_user: User) -> Dict:
        if not current_user.admin:
            raise AdminActionForbiddenException
        return {
            "action_type": self.action_type,
            "admin_user": self.admin_user.serialize(current_user),
            "created_at": self.created_at,
            "id": self.id,
            "report_id": self.report_id,
            "user": self.user.serialize(current_user) if self.user else None,
        }

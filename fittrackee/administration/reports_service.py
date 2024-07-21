from datetime import datetime
from typing import Dict, Optional, Union

from sqlalchemy import func

from fittrackee import db
from fittrackee.administration.models import (
    COMMENT_ACTION_TYPES,
    USER_ACTION_TYPES,
    WORKOUT_ACTION_TYPES,
    AdminAction,
)
from fittrackee.administration.users_service import UserManagerService
from fittrackee.comments.models import Comment
from fittrackee.comments.utils import get_comment
from fittrackee.reports.exceptions import (
    InvalidAdminActionException,
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
)
from fittrackee.reports.models import Report, ReportComment
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout
from fittrackee.workouts.utils.workouts import get_workout


class ReportService:
    @staticmethod
    def create_report(
        *,
        reporter: User,
        note: str,
        object_id: str,
        object_type: str,
    ) -> Report:
        if object_type == "comment":
            target_object = get_comment(object_id, reporter)
        elif object_type == "workout":
            target_object = get_workout(object_id, reporter)
        else:  # object_type == "user"
            target_object = User.query.filter(
                func.lower(User.username) == func.lower(object_id),
            ).first()
            if not target_object or not target_object.is_active:
                raise UserNotFoundException()

        if target_object and target_object.suspended_at:
            raise SuspendedObjectException(object_type)

        existing_unresolved_report = Report.query.filter_by(
            reported_by=reporter.id,
            resolved=False,
            **{f"reported_{object_type}_id": target_object.id},
        ).first()
        if existing_unresolved_report:
            raise InvalidReportException("a report already exists")

        new_report = Report(
            note=note,
            reported_by=reporter.id,
            reported_object=target_object,
        )
        db.session.add(new_report)
        db.session.commit()

        return new_report

    @staticmethod
    def update_report(
        *,
        report_id: int,
        admin_user: User,
        report_comment: str,
        resolved: Optional[bool] = None,
    ) -> Report:
        report = Report.query.filter_by(id=report_id).first()
        if not report:
            raise ReportNotFoundException()
        previous_resolved = report.resolved

        new_report_comment = ReportComment(
            comment=report_comment, report_id=report_id, user_id=admin_user.id
        )
        db.session.add(new_report_comment)

        now = datetime.utcnow()
        report.updated_at = now
        report_action = None
        if resolved is not None:
            report.resolved = resolved
        if resolved is True and report.resolved_by is None:
            report.resolved_at = now
            report.resolved_by = admin_user.id
            report_action = AdminAction(
                report_id=report.id,
                admin_user_id=admin_user.id,
                action_type="report_resolution",
                created_at=now,
            )
        if resolved is False:
            report.resolved_at = None
            report.resolved_by = None
            if previous_resolved is True:
                report_action = AdminAction(
                    report_id=report.id,
                    admin_user_id=admin_user.id,
                    action_type="report_reopening",
                    created_at=now,
                )

        if report_action:
            db.session.add(report_action)

        db.session.commit()

        return report

    @staticmethod
    def create_admin_action(
        *,
        report: Report,
        admin_user: User,
        action_type: str,
        reason: Optional[str] = None,
        data: Dict,
    ) -> None:
        reported_user: User = report.reported_user

        # if reported user has been deleted after report creation
        if not reported_user:
            raise InvalidAdminActionException("invalid 'username'")

        if action_type in USER_ACTION_TYPES:
            username = data.get("username")
            if not username:
                raise InvalidAdminActionException("'username' is missing")
            if username != reported_user.username:
                raise InvalidAdminActionException("invalid 'username'")

            user_manager_service = UserManagerService(
                username=username, admin_user_id=admin_user.id
            )
            user, _, _ = user_manager_service.update(
                suspended=action_type == "user_suspension",
                report_id=report.id,
                reason=reason,
            )

        elif action_type in COMMENT_ACTION_TYPES + WORKOUT_ACTION_TYPES:
            object_type = action_type.split("_")[0]
            object_type_column = f"{object_type}_id"
            object_id = data.get(object_type_column)
            if not object_id:
                raise InvalidAdminActionException(
                    f"'{object_type_column}' is missing"
                )
            reported_object: Union[Comment, Workout] = getattr(
                report, f"reported_{object_type}"
            )
            if not reported_object or reported_object.short_id != object_id:
                raise InvalidAdminActionException(
                    f"invalid '{object_type_column}'"
                )

            now = datetime.utcnow()
            admin_action = AdminAction(
                admin_user_id=admin_user.id,
                action_type=action_type,
                created_at=now,
                report_id=report.id,
                reason=reason,
                user_id=reported_object.user_id,
                **{object_type_column: reported_object.id},
            )
            db.session.add(admin_action)

            if "_suspension" in action_type:
                if reported_object.suspended_at:
                    raise InvalidAdminActionException(
                        f"{object_type} '{object_id}' already suspended"
                    )
                reported_object.suspended_at = now

            else:
                reported_object.suspended_at = None
            db.session.flush()
        else:
            raise InvalidAdminActionException("invalid action type")

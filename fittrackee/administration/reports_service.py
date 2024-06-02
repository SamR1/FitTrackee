from datetime import datetime
from typing import Optional

from sqlalchemy import func

from fittrackee import db
from fittrackee.administration.models import AdminAction
from fittrackee.comments.utils import get_comment
from fittrackee.reports.exceptions import (
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
)
from fittrackee.reports.models import Report, ReportComment
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
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

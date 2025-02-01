from datetime import datetime, timezone
from typing import Dict, Optional, Union

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from fittrackee import db
from fittrackee.comments.models import Comment
from fittrackee.comments.utils import get_comment
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
from fittrackee.users.users_service import UserManagerService
from fittrackee.workouts.models import Workout
from fittrackee.workouts.utils.workouts import get_workout

from .exceptions import (
    InvalidReportActionException,
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
    UserWarningExistsException,
)
from .models import (
    ALL_USER_ACTION_TYPES,
    COMMENT_ACTION_TYPES,
    WORKOUT_ACTION_TYPES,
    Report,
    ReportAction,
    ReportActionAppeal,
    ReportComment,
)


class ReportService:
    @staticmethod
    def create_report(
        *,
        reporter: User,
        note: str,
        object_id: str,
        object_type: str,
    ) -> Report:
        target_object: Union[Comment, User, Workout]
        if object_type == "comment":
            target_object = get_comment(object_id, reporter)
        elif object_type == "workout":
            target_object = get_workout(object_id, reporter)
        else:  # object_type == "user"
            try:
                user = User.query.filter(
                    func.lower(User.username) == func.lower(object_id),
                ).one()
            except NoResultFound as e:
                raise UserNotFoundException() from e
            if not user.is_active:
                raise UserNotFoundException()
            target_object = user

        if target_object and target_object.suspended_at:
            raise SuspendedObjectException(object_type)

        existing_unresolved_report = Report.query.filter_by(
            reported_by=reporter.id,
            resolved=False,
            object_type=object_type,
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
        moderator: User,
        report_comment: str,
        resolved: Optional[bool] = None,
    ) -> Report:
        report = Report.query.filter_by(id=report_id).first()
        if not report:
            raise ReportNotFoundException()
        previous_resolved = report.resolved

        new_report_comment = ReportComment(
            comment=report_comment,
            report_id=report_id,
            user_id=moderator.id,
        )
        db.session.add(new_report_comment)

        now = datetime.now(timezone.utc)
        report.updated_at = now
        report_action = None
        if resolved is not None:
            report.resolved = resolved
        if resolved is True and report.resolved_by is None:
            report.resolved_at = now
            report.resolved_by = moderator.id
            report_action = ReportAction(
                report_id=report.id,
                moderator_id=moderator.id,
                action_type="report_resolution",
                created_at=now,
            )
        if resolved is False:
            report.resolved_at = None
            report.resolved_by = None
            if previous_resolved is True:
                report_action = ReportAction(
                    report_id=report.id,
                    moderator_id=moderator.id,
                    action_type="report_reopening",
                    created_at=now,
                )

        if report_action:
            db.session.add(report_action)

        db.session.commit()

        return report

    @staticmethod
    def create_report_action(
        *,
        report: Report,
        moderator: User,
        action_type: str,
        reason: Optional[str] = None,
        data: Dict,
    ) -> Optional[ReportAction]:
        reported_user: User = report.reported_user

        # if reported user has been deleted after report creation
        if not reported_user:
            raise InvalidReportActionException("invalid 'username'")

        now = datetime.now(timezone.utc)
        report_action = None
        if action_type in ALL_USER_ACTION_TYPES:
            username = data.get("username")
            if not username:
                raise InvalidReportActionException("'username' is missing")
            if username != reported_user.username:
                raise InvalidReportActionException("invalid 'username'")

            if action_type.startswith("user_warning"):
                user = User.query.filter_by(username=username).first()
                if not user:
                    raise InvalidReportActionException("invalid 'username'")

                existing_report_action = ReportAction.query.filter_by(
                    action_type=action_type,
                    report_id=report.id,
                    user_id=user.id,
                ).first()
                if existing_report_action:
                    raise UserWarningExistsException("user already warned")

                report_action = ReportAction(
                    moderator_id=moderator.id,
                    action_type=action_type,
                    created_at=now,
                    report_id=report.id,
                    reason=reason,
                    user_id=user.id,
                )
                if report.reported_comment_id:
                    report_action.comment_id = report.reported_comment_id
                elif report.reported_workout_id:
                    report_action.workout_id = report.reported_workout_id
                db.session.add(report_action)
            else:
                user_manager_service = UserManagerService(
                    username=username, moderator_id=moderator.id
                )
                user, _, _, _ = user_manager_service.update(
                    suspended=action_type == "user_suspension",
                    report_id=report.id,
                    reason=reason,
                )
                if action_type == "user_unsuspension":
                    appeal = (
                        ReportActionAppeal.query.join(ReportAction)
                        .filter(
                            ReportAction.report_id == report.id,
                            ReportAction.user_id == user.id,
                            ReportAction.action_type == "user_suspension",
                        )
                        .first()
                    )
                    if appeal:
                        appeal.approved = None
                        appeal.updated_at = datetime.now(timezone.utc)
                        db.session.flush()

        elif action_type in COMMENT_ACTION_TYPES + WORKOUT_ACTION_TYPES:
            object_type = action_type.split("_")[0]
            object_type_column = f"{object_type}_id"
            object_id = data.get(object_type_column)
            if not object_id:
                raise InvalidReportActionException(
                    f"'{object_type_column}' is missing"
                )
            reported_object: Union[Comment, Workout] = getattr(
                report, f"reported_{object_type}"
            )
            if not reported_object or reported_object.short_id != object_id:
                raise InvalidReportActionException(
                    f"invalid '{object_type_column}'"
                )

            report_action = ReportAction(
                moderator_id=moderator.id,
                action_type=action_type,
                created_at=now,
                report_id=report.id,
                reason=reason,
                user_id=reported_object.user_id,
                **{object_type_column: reported_object.id},
            )
            db.session.add(report_action)

            if "_suspension" in action_type:
                if reported_object.suspended_at:
                    raise InvalidReportActionException(
                        f"{object_type} already suspended"
                    )
                reported_object.suspended_at = now

            else:
                if reported_object.suspended_at is None:
                    raise InvalidReportActionException(
                        f"{object_type} already reactivated"
                    )
                reported_object.suspended_at = None
                appeal = (
                    ReportActionAppeal.query.join(ReportAction)
                    .filter(
                        ReportAction.report_id == report.id,
                        ReportAction.user_id == reported_object.user_id,
                        ReportAction.action_type
                        == f"{object_type}_suspension",
                    )
                    .first()
                )
                if appeal:
                    appeal.approved = None
                    appeal.updated_at = datetime.now(timezone.utc)
                    db.session.flush()
            db.session.flush()
        else:
            raise InvalidReportActionException("invalid action type")
        return report_action

    @staticmethod
    def process_appeal(
        appeal: ReportActionAppeal, moderator: User, data: Dict
    ) -> Optional[ReportAction]:
        appeal.moderator_id = moderator.id
        appeal.approved = data["approved"]
        appeal.reason = data["reason"]
        appeal.updated_at = datetime.now(timezone.utc)

        action = appeal.action
        content = None
        content_type = ""
        if action.action_type.startswith("comment_"):
            content = Comment.query.filter_by(id=action.comment_id).first()
            content_type = "comment"
        elif action.action_type.startswith("workout_"):
            content = Workout.query.filter_by(id=action.workout_id).first()
            content_type = "workout"

        new_report_action = None
        if data["approved"]:
            if action.action_type == "user_suspension":
                if not appeal.user.suspended_at:
                    raise InvalidReportActionException(
                        "user account has already been reactivated"
                    )

                user_manager_service = UserManagerService(
                    username=appeal.user.username,
                    moderator_id=moderator.id,
                )
                user, _, _, new_report_action = user_manager_service.update(
                    suspended=False, report_id=appeal.action.report_id
                )
            if action.action_type == "user_warning":
                new_report_action = ReportAction(
                    moderator_id=moderator.id,
                    action_type="user_warning_lifting",
                    created_at=datetime.now(timezone.utc),
                    report_id=action.report_id,
                    user_id=action.user_id,
                )
                db.session.add(new_report_action)
            if (
                action.action_type
                in ["comment_suspension", "workout_suspension"]
                and content
            ):
                if not content.suspended_at:
                    raise InvalidReportActionException(
                        f"{content_type} already reactivated"
                    )
                content_id = {f"{content_type}_id": content.id}
                new_report_action = ReportAction(
                    moderator_id=moderator.id,
                    action_type=f"{content_type}_unsuspension",
                    created_at=datetime.now(timezone.utc),
                    report_id=action.report_id,
                    user_id=action.user_id,
                    **content_id,
                )
                db.session.add(new_report_action)
                content.suspended_at = None
        else:
            if (
                action.action_type == "user_suspension"
                and not appeal.user.suspended_at
            ):
                if not appeal.user.suspended_at:
                    raise InvalidReportActionException(
                        "user account has been reactivated after appeal"
                    )
            if (
                action.action_type
                in ["comment_suspension", "workout_suspension"]
                and content
                and not content.suspended_at
            ):
                raise InvalidReportActionException(
                    f"{content_type} has been reactivated after appeal"
                )
        return new_report_action

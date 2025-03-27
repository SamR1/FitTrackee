from typing import Dict, Optional, Tuple

from flask import current_app

from fittrackee.comments.models import Comment
from fittrackee.dates import get_date_string_for_user
from fittrackee.emails.tasks import send_email
from fittrackee.users.models import User
from fittrackee.users.utils.language import get_language
from fittrackee.workouts.models import Workout

from .exceptions import InvalidReportActionException
from .models import Report, ReportAction


class ReportEmailService:
    @staticmethod
    def _get_email_data(
        report: Report,
        reason: Optional[str] = None,
        with_user_image: bool = False,
    ) -> Tuple[Dict, Dict, str]:
        fittrackee_url = current_app.config["UI_URL"]
        reported_user: User = report.reported_user
        user_data = {
            "language": get_language(reported_user.language),
            "email": reported_user.email,
        }
        email_data = {
            "username": reported_user.username,
            "fittrackee_url": fittrackee_url,
            "reason": reason,
        }
        if with_user_image:
            email_data["user_image_url"] = (
                f"{fittrackee_url}/api/users/{reported_user.username}/picture"
                if reported_user.picture
                else f"{fittrackee_url}/img/user.png"
            )
        return user_data, email_data, fittrackee_url

    @staticmethod
    def _get_comment_email_data(
        email_data: Dict,
        comment: Comment,
        reported_user: User,
        fittrackee_url: str,
    ) -> Dict:
        comment_email_data = {
            **email_data,
            "created_at": get_date_string_for_user(
                comment.created_at, reported_user
            ),
            "text": comment.text,
        }
        if comment.workout_id:
            comment_email_data["comment_url"] = (
                f"{fittrackee_url}/workouts/{comment.workout.short_id}"
                f"/comments/{comment.short_id}"
            )
        else:
            comment_email_data["comment_url"] = (
                f"{fittrackee_url}/comments/{comment.short_id}"
            )

        return comment_email_data

    @staticmethod
    def _get_workout_email_data(
        email_data: Dict,
        workout: Workout,
        reported_user: User,
        fittrackee_url: str,
    ) -> Dict:
        return {
            **email_data,
            "map": (
                f"{fittrackee_url}/api/workouts/map/{workout.map_id}"
                if workout.map_id
                else None
            ),
            "title": workout.title,
            "workout_date": get_date_string_for_user(
                workout.workout_date, reported_user
            ),
            "workout_url": f"{fittrackee_url}/workouts/{workout.short_id}",
        }

    def _send_user_suspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason
        )
        email_data["appeal_url"] = f"{fittrackee_url}/profile/suspension"
        send_email.send(user_data, email_data, template="user_suspension")

    def _send_user_unsuspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, _ = self._get_email_data(report, reason)
        email_data["without_user_action"] = True
        send_email.send(user_data, email_data, template="user_unsuspension")

    def _send_user_warning_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        if not report_action:
            raise InvalidReportActionException("invalid action action")

        if report.reported_comment_id:
            email_data = self._get_comment_email_data(
                email_data,
                report.reported_comment,
                report.reported_user,
                fittrackee_url,
            )
        elif report.reported_workout_id:
            email_data = self._get_workout_email_data(
                email_data,
                report.reported_workout,
                report.reported_user,
                fittrackee_url,
            )
        email_data["appeal_url"] = (
            f"{fittrackee_url}/profile/moderation/"
            f"sanctions/{report_action.short_id}"
        )
        send_email.send(user_data, email_data, template="user_warning")

    def _send_user_warning_lifting_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        if not report_action:
            raise InvalidReportActionException("invalid action action")

        if report.reported_comment_id:
            email_data = self._get_comment_email_data(
                email_data,
                report.reported_comment,
                report.reported_user,
                fittrackee_url,
            )
        elif report.reported_workout_id:
            email_data = self._get_workout_email_data(
                email_data,
                report.reported_workout,
                report.reported_user,
                fittrackee_url,
            )
        email_data["without_user_action"] = True
        send_email.send(user_data, email_data, template="user_warning_lifting")

    def _send_comment_suspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_comment_email_data(
            email_data,
            report.reported_comment,
            report.reported_user,
            fittrackee_url,
        )
        send_email.send(user_data, email_data, template="comment_suspension")

    def _send_comment_unsuspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_comment_email_data(
            email_data,
            report.reported_comment,
            report.reported_user,
            fittrackee_url,
        )
        email_data["without_user_action"] = True
        send_email.send(user_data, email_data, template="comment_unsuspension")

    def _send_workout_suspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_workout_email_data(
            email_data,
            report.reported_workout,
            report.reported_user,
            fittrackee_url,
        )
        send_email.send(user_data, email_data, template="workout_suspension")

    def _send_workout_unsuspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_workout_email_data(
            email_data,
            report.reported_workout,
            report.reported_user,
            fittrackee_url,
        )
        email_data["without_user_action"] = True
        send_email.send(user_data, email_data, template="workout_unsuspension")

    def _send_appeal_rejected_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        report_action: Optional[ReportAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )

        if not report_action:
            raise InvalidReportActionException("invalid action action")

        if report.reported_comment_id:
            email_data = self._get_comment_email_data(
                email_data,
                report.reported_comment,
                report.reported_user,
                fittrackee_url,
            )
        elif report.reported_workout_id:
            email_data = self._get_workout_email_data(
                email_data,
                report.reported_workout,
                report.reported_user,
                fittrackee_url,
            )
        email_data["without_user_action"] = True
        email_data["action_type"] = report_action.action_type
        send_email.send(user_data, email_data, template="appeal_rejected")

    def send_report_action_email(
        self,
        report: Report,
        action_type: str,
        reason: Optional[str],
        report_action: Optional[
            ReportAction
        ] = None,  # needed only for user warning and appeal
    ) -> None:
        send_email_func = getattr(self, f"_send_{action_type}_email")
        send_email_func(
            report=report, reason=reason, report_action=report_action
        )

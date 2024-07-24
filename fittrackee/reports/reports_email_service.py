from typing import Dict, Optional, Tuple

from flask import current_app

from fittrackee.administration.models import AdminAction
from fittrackee.comments.models import Comment
from fittrackee.emails.tasks import (
    comment_suspension_email,
    comment_unsuspension_email,
    user_suspension_email,
    user_unsuspension_email,
    user_warning_email,
    workout_suspension_email,
    workout_unsuspension_email,
)
from fittrackee.users.models import User
from fittrackee.users.utils.language import get_language
from fittrackee.utils import get_date_string_for_user
from fittrackee.workouts.models import Workout

from .exceptions import InvalidAdminActionException
from .models import Report


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
            'language': get_language(reported_user.language),
            'email': reported_user.email,
        }
        email_data = {
            'username': reported_user.username,
            'fittrackee_url': fittrackee_url,
            'reason': reason,
        }
        if with_user_image:
            email_data["user_image_url"] = (
                f'{fittrackee_url}/api/users/{reported_user.username}/picture'
                if reported_user.picture
                else f'{fittrackee_url}/img/user.png'
            )
        return user_data, email_data, fittrackee_url

    @staticmethod
    def _get_comment_email_data(
        email_data: Dict,
        comment: Comment,
        reported_user: User,
        *,
        fittrackee_url_for_appeal: Optional[str] = None,
    ) -> Dict:
        comment_email_data = {
            **email_data,
            "text": comment.handle_mentions()[0],
            "created_at": get_date_string_for_user(
                comment.created_at, reported_user
            ),
        }
        if fittrackee_url_for_appeal:
            if comment.workout_id:
                workout = Workout.query.filter_by(
                    id=comment.workout_id
                ).first()
                comment_email_data["appeal_url"] = (
                    f'{fittrackee_url_for_appeal}/workouts/{workout.short_id}'
                    f'/comments/{comment.short_id}'
                )
            else:
                comment_email_data["appeal_url"] = (
                    f'{fittrackee_url_for_appeal}/comments'
                    f'/{comment.short_id}'
                )

        return comment_email_data

    @staticmethod
    def _get_workout_email_data(
        email_data: Dict,
        workout: Workout,
        reported_user: User,
        *,
        fittrackee_url: str,
        with_appeal_url: bool = False,
    ) -> Dict:
        workout_email_data = {
            **email_data,
            "title": workout.title,
            "workout_date": get_date_string_for_user(
                workout.workout_date, reported_user
            ),
            "map": (
                f"{fittrackee_url}/api/workouts/map/{workout.map_id}"
                if workout.map_id
                else None
            ),
        }
        if with_appeal_url:
            workout_email_data["appeal_url"] = (
                f'{fittrackee_url}/workouts/{workout.short_id}'
            )
        return workout_email_data

    def _send_user_suspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason
        )
        email_data['appeal_url'] = f'{fittrackee_url}/profile/suspension'
        user_suspension_email.send(user_data, email_data)

    def _send_user_unsuspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, _ = self._get_email_data(report, reason)
        user_unsuspension_email.send(user_data, email_data)

    def _send_user_warning_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason
        )
        if not admin_action:
            raise InvalidAdminActionException('invalid action action')

        email_data['appeal_url'] = (
            f'{fittrackee_url}/profile/warning/{admin_action.short_id}/appeal'
        )
        user_warning_email.send(user_data, email_data)

    def _send_comment_suspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_comment_email_data(
            email_data,
            report.reported_comment,
            report.reported_user,
            fittrackee_url_for_appeal=fittrackee_url,
        )
        comment_suspension_email.send(user_data, email_data)

    def _send_comment_unsuspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_comment_email_data(
            email_data, report.reported_comment, report.reported_user
        )
        comment_unsuspension_email.send(user_data, email_data)

    def _send_workout_suspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_workout_email_data(
            email_data,
            report.reported_workout,
            report.reported_user,
            fittrackee_url=fittrackee_url,
            with_appeal_url=True,
        )
        workout_suspension_email.send(user_data, email_data)

    def _send_workout_unsuspension_email(
        self,
        *,
        report: Report,
        reason: Optional[str],
        admin_action: Optional[AdminAction],
    ) -> None:
        user_data, email_data, fittrackee_url = self._get_email_data(
            report, reason, with_user_image=True
        )
        email_data = self._get_workout_email_data(
            email_data,
            report.reported_workout,
            report.reported_user,
            fittrackee_url=fittrackee_url,
        )
        workout_unsuspension_email.send(user_data, email_data)

    def send_admin_action_email(
        self,
        report: Report,
        action_type: str,
        reason: Optional[str],
        admin_action: Optional[
            AdminAction
        ] = None,  # needed only for user warning
    ) -> None:
        send_email_func = getattr(self, f"_send_{action_type}_email")
        send_email_func(
            report=report, reason=reason, admin_action=admin_action
        )

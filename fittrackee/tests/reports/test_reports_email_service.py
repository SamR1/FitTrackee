from datetime import datetime, timezone
from typing import Dict
from unittest.mock import MagicMock

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.dates import get_date_string_for_user
from fittrackee.reports.reports_email_service import ReportEmailService
from fittrackee.reports.reports_service import ReportService
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ReportMixin
from .mixins import ReportServiceCreateReportActionMixin


class TestReportEmailServiceForUserSuspension(
    ReportServiceCreateReportActionMixin
):
    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_user_suspension(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        reports_send_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "user_suspension", input_reason.get("reason")
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "username": user_3.username,
                "fittrackee_url": app.config["UI_URL"],
                "appeal_url": f"{app.config['UI_URL']}/profile/suspension",
                "reason": input_reason.get("reason"),
            },
            template="user_suspension",
        )


class TestReportEmailServiceForUserReactivation(
    ReportServiceCreateReportActionMixin
):
    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_user_reactivation(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        reports_send_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "user_unsuspension", input_reason.get("reason")
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "username": user_3.username,
                "fittrackee_url": app.config["UI_URL"],
                "reason": input_reason.get("reason"),
                "without_user_action": True,
            },
            template="user_unsuspension",
        )


class TestReportEmailServiceForUserWarning(
    ReportServiceCreateReportActionMixin
):
    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_user_warning_for_user_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        reports_send_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning",
            reason=None,
            data={"username": user_3.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning", input_reason.get("reason"), user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "username": user_3.username,
                "fittrackee_url": app.config["UI_URL"],
                "appeal_url": (
                    f"{app.config['UI_URL']}/profile/moderation/sanctions"
                    f"/{user_warning.short_id}"  # type:ignore
                ),
                "reason": input_reason.get("reason"),
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
            },
            template="user_warning",
        )

    def test_it_sends_an_email_on_user_warning_for_comment_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning",
            reason=None,
            data={"username": user_3.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "appeal_url": (
                    f"{app.config['UI_URL']}/profile/moderation/sanctions"
                    f"/{user_warning.short_id}"  # type:ignore
                ),
                "comment_url": (
                    f"{app.config['UI_URL']}/workouts"
                    f"/{workout_cycling_user_2.short_id}"
                    f"/comments/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
            },
            template="user_warning",
        )

    def test_it_sends_an_email_on_user_warning_for_comment_report_when_workout_is_deleted(  # noqa
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning",
            reason=None,
            data={"username": user_3.username},
        )
        db.session.delete(workout_cycling_user_2)
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "appeal_url": (
                    f"{app.config['UI_URL']}/profile/moderation/sanctions"
                    f"/{user_warning.short_id}"  # type:ignore
                ),
                "comment_url": (
                    f"{app.config['UI_URL']}/comments"
                    f"/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
            },
            template="user_warning",
        )

    def test_it_sends_an_email_on_user_warning_for_workout_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning",
            reason=None,
            data={"username": user_2.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "appeal_url": (
                    f"{app.config['UI_URL']}/profile/moderation/sanctions"
                    f"/{user_warning.short_id}"  # type:ignore
                ),
                "fittrackee_url": app.config["UI_URL"],
                "map": None,
                "reason": None,
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="user_warning",
        )

    def test_it_sends_an_email_on_user_warning_for_workout_with_gpx_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning",
            reason=None,
            data={"username": user_2.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "appeal_url": (
                    f"{app.config['UI_URL']}/profile/moderation/sanctions"
                    f"/{user_warning.short_id}"  # type:ignore
                ),
                "fittrackee_url": app.config["UI_URL"],
                "map": (
                    f"{app.config['UI_URL']}/api/workouts/map"
                    f"/{workout_cycling_user_2.map_id}"
                ),
                "reason": None,
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="user_warning",
        )


class TestReportEmailServiceForUserWarningLifting(
    ReportServiceCreateReportActionMixin
):
    def test_it_sends_an_email_on_user_warning_for_user_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning_lifting",
            reason=None,
            data={"username": user_3.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning_lifting", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "username": user_3.username,
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "without_user_action": True,
            },
            template="user_warning_lifting",
        )

    def test_it_sends_an_email_on_user_warning_for_comment_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning_lifting",
            reason=None,
            data={"username": user_3.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning_lifting", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "comment_url": (
                    f"{app.config['UI_URL']}/workouts"
                    f"/{workout_cycling_user_2.short_id}"
                    f"/comments/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
                "without_user_action": True,
            },
            template="user_warning_lifting",
        )

    def test_it_sends_an_email_on_user_warning_for_workout_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning_lifting",
            reason=None,
            data={"username": user_2.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning_lifting", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "fittrackee_url": app.config["UI_URL"],
                "map": None,
                "reason": None,
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
                "without_user_action": True,
            },
            template="user_warning_lifting",
        )

    def test_it_sends_an_email_on_user_warning_for_workout_with_gpx_report(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        user_warning = report_service.create_report_action(
            report=report,
            moderator=user_1_moderator,
            action_type="user_warning_lifting",
            reason=None,
            data={"username": user_2.username},
        )
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "user_warning_lifting", None, user_warning
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "fittrackee_url": app.config["UI_URL"],
                "map": (
                    f"{app.config['UI_URL']}/api/workouts/map"
                    f"/{workout_cycling_user_2.map_id}"
                ),
                "reason": None,
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
                "without_user_action": True,
            },
            template="user_warning_lifting",
        )


class TestReportEmailServiceForComment(ReportServiceCreateReportActionMixin):
    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_comment_suspension(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_reason: Dict,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "comment_suspension", input_reason.get("reason")
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "comment_url": (
                    f"{app.config['UI_URL']}/workouts"
                    f"/{workout_cycling_user_2.short_id}"
                    f"/comments/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": input_reason.get("reason"),
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
            },
            template="comment_suspension",
        )

    def test_it_sends_an_email_on_comment_suspension_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()
        db.session.delete(workout_cycling_user_2)
        db.session.flush()

        report_email_service.send_report_action_email(
            report, "comment_suspension", None
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "comment_url": (
                    f"{app.config['UI_URL']}/comments"
                    f"/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
            },
            template="comment_suspension",
        )

    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_comment_reactivation(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_comment.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "comment_unsuspension", input_reason.get("reason")
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "comment_url": (
                    f"{app.config['UI_URL']}/workouts"
                    f"/{workout_cycling_user_2.short_id}"
                    f"/comments/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": input_reason.get("reason"),
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
                "without_user_action": True,
            },
            template="comment_unsuspension",
        )

    def test_it_sends_an_email_on_comment_reactivation_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_comment.suspended_at = datetime.now(timezone.utc)
        db.session.delete(workout_cycling_user_2)
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "comment_unsuspension", None
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "comment_url": (
                    f"{app.config['UI_URL']}/comments"
                    f"/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "text": report.reported_comment.handle_mentions()[0],
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_3.username,
                "without_user_action": True,
            },
            template="comment_unsuspension",
        )


class TestReportEmailServiceForWorkout(ReportServiceCreateReportActionMixin):
    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_workout_suspension(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_reason: Dict,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "workout_suspension", input_reason.get("reason")
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "fittrackee_url": app.config["UI_URL"],
                "map": None,
                "reason": input_reason.get("reason"),
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="workout_suspension",
        )

    def test_it_sends_an_email_on_workout_with_gpx_suspension(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "workout_suspension", None
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "fittrackee_url": app.config["UI_URL"],
                "map": (
                    f"{app.config['UI_URL']}/api/workouts/map"
                    f"/{workout_cycling_user_2.map_id}"
                ),
                "reason": None,
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="workout_suspension",
        )

    @pytest.mark.parametrize("input_reason", [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_workout_reactivation(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "workout_unsuspension", input_reason.get("reason")
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "fittrackee_url": app.config["UI_URL"],
                "map": None,
                "reason": input_reason.get("reason"),
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "without_user_action": True,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="workout_unsuspension",
        )

    def test_it_sends_an_email_on_workout_with_gpx_reactivation(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "workout_unsuspension", None
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "fittrackee_url": app.config["UI_URL"],
                "map": (
                    f"{app.config['UI_URL']}/api/workouts/map"
                    f"/{workout_cycling_user_2.map_id}"
                ),
                "reason": None,
                "title": workout_cycling_user_2.title,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "username": user_2.username,
                "without_user_action": True,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="workout_unsuspension",
        )


class TestReportEmailServiceForAppealRejected(
    ReportServiceCreateReportActionMixin, ReportMixin
):
    @pytest.mark.parametrize(
        "input_action_type", ["user_suspension", "user_warning"]
    )
    def test_it_sends_an_email_for_user_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        reports_send_email_mock: MagicMock,
        input_action_type: str,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        report_action = self.create_report_user_action(
            user_1_moderator, user_3, input_action_type, report.id
        )
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "appeal_rejected", None, report_action
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "username": user_3.username,
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "without_user_action": True,
                "action_type": input_action_type,
            },
            template="appeal_rejected",
        )

    def test_it_sends_an_email_on_workout_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        workout_cycling_user_2.suspended_at = datetime.now(timezone.utc)
        db.session.flush()
        report_action = self.create_report_workout_action(
            user_1_moderator, user_3, workout_cycling_user_2
        )
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "appeal_rejected", None, report_action
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_2.email,
            },
            {
                "username": user_2.username,
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "without_user_action": True,
                "action_type": report_action.action_type,
                "map": (
                    f"{app.config['UI_URL']}/api/workouts/map"
                    f"/{workout_cycling_user_2.map_id}"
                ),
                "title": workout_cycling_user_2.title,
                "workout_date": get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                "workout_url": (
                    f"{app.config['UI_URL']}/workouts/"
                    f"{workout_cycling_user_2.short_id}"
                ),
            },
            template="appeal_rejected",
        )

    def test_it_sends_an_email_on_comment_action(
        self,
        app: Flask,
        user_1_moderator: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        reports_send_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_action = self.create_report_comment_action(
            user_1_moderator, user_3, report.reported_comment
        )
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_report_action_email(
            report, "appeal_rejected", None, report_action
        )

        reports_send_email_mock.send.assert_called_once_with(
            {
                "language": "en",
                "email": user_3.email,
            },
            {
                "username": user_3.username,
                "fittrackee_url": app.config["UI_URL"],
                "reason": None,
                "user_image_url": f"{app.config['UI_URL']}/img/user.png",
                "without_user_action": True,
                "action_type": report_action.action_type,
                "comment_url": (
                    f"{app.config['UI_URL']}/workouts"
                    f"/{workout_cycling_user_2.short_id}"
                    f"/comments/{report.reported_comment.short_id}"
                ),
                "created_at": get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                "text": report.reported_comment.handle_mentions()[0],
            },
            template="appeal_rejected",
        )

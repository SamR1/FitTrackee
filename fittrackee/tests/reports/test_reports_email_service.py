from datetime import datetime
from typing import Dict
from unittest.mock import MagicMock

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.reports.reports_email_service import ReportEmailService
from fittrackee.reports.reports_service import ReportService
from fittrackee.users.models import User
from fittrackee.utils import get_date_string_for_user
from fittrackee.workouts.models import Sport, Workout

from .mixins import ReportServiceCreateAdminActionMixin


class TestReportEmailServiceForUser(ReportServiceCreateAdminActionMixin):
    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_user_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_suspension_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "user_suspension", input_reason.get("reason")
        )

        user_suspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'username': user_3.username,
                'fittrackee_url': app.config['UI_URL'],
                'appeal_url': f'{app.config["UI_URL"]}/profile/suspension',
                'reason': input_reason.get('reason'),
            },
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_user_reactivation(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_unsuspension_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.utcnow()
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "user_unsuspension", input_reason.get("reason")
        )

        user_unsuspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'username': user_3.username,
                'fittrackee_url': app.config['UI_URL'],
                'reason': input_reason.get('reason'),
            },
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_user_warning(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_warning_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.utcnow()
        db.session.flush()
        report_email_service = ReportEmailService()
        user_warning = report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_warning",
            reason=None,
            data={"username": user_3.username},
        )
        db.session.flush()

        report_email_service.send_admin_action_email(
            report, "user_warning", input_reason.get("reason"), user_warning
        )

        user_warning_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'username': user_3.username,
                'fittrackee_url': app.config['UI_URL'],
                'appeal_url': (
                    f'{app.config["UI_URL"]}/profile/warning'
                    f'/{user_warning.short_id}/appeal'  # type:ignore
                ),
                'reason': input_reason.get('reason'),
            },
        )


class TestReportEmailServiceForComment(ReportServiceCreateAdminActionMixin):
    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_comment_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_reason: Dict,
        comment_suspension_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "comment_suspension", input_reason.get("reason")
        )

        comment_suspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'comment_url': (
                    f'{app.config["UI_URL"]}/workouts'
                    f'/{workout_cycling_user_2.short_id}'
                    f'/comments/{report.reported_comment.short_id}'
                ),
                'created_at': get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                'fittrackee_url': app.config['UI_URL'],
                'reason': input_reason.get('reason'),
                'text': report.reported_comment.handle_mentions()[0],
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_3.username,
            },
        )

    def test_it_sends_an_email_on_comment_suspension_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_suspension_email_mock: MagicMock,
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

        report_email_service.send_admin_action_email(
            report, "comment_suspension", None
        )

        comment_suspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'comment_url': (
                    f'{app.config["UI_URL"]}/comments'
                    f'/{report.reported_comment.short_id}'
                ),
                'created_at': get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                'fittrackee_url': app.config['UI_URL'],
                'reason': None,
                'text': report.reported_comment.handle_mentions()[0],
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_3.username,
            },
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_comment_reactivation(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_unsuspension_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_comment.suspended_at = datetime.utcnow()
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "comment_unsuspension", input_reason.get("reason")
        )

        comment_unsuspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'comment_url': (
                    f'{app.config["UI_URL"]}/workouts'
                    f'/{workout_cycling_user_2.short_id}'
                    f'/comments/{report.reported_comment.short_id}'
                ),
                'created_at': get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                'fittrackee_url': app.config['UI_URL'],
                'reason': input_reason.get('reason'),
                'text': report.reported_comment.handle_mentions()[0],
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_3.username,
            },
        )

    def test_it_sends_an_email_on_comment_reactivation_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        comment_unsuspension_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_comment.suspended_at = datetime.utcnow()
        db.session.delete(workout_cycling_user_2)
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "comment_unsuspension", None
        )

        comment_unsuspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_3.email,
            },
            {
                'comment_url': (
                    f'{app.config["UI_URL"]}/comments'
                    f'/{report.reported_comment.short_id}'
                ),
                'created_at': get_date_string_for_user(
                    report.reported_comment.created_at, user_3
                ),
                'fittrackee_url': app.config['UI_URL'],
                'reason': None,
                'text': report.reported_comment.handle_mentions()[0],
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_3.username,
            },
        )


class TestReportEmailServiceForWorkout(ReportServiceCreateAdminActionMixin):
    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_workout_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_reason: Dict,
        workout_suspension_email_mock: MagicMock,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "workout_suspension", input_reason.get("reason")
        )

        workout_suspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_2.email,
            },
            {
                'fittrackee_url': app.config['UI_URL'],
                'map': None,
                'reason': input_reason.get('reason'),
                'title': workout_cycling_user_2.title,
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_2.username,
                'workout_date': get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                'workout_url': (
                    f'{app.config["UI_URL"]}/workouts/'
                    f'{workout_cycling_user_2.short_id}'
                ),
            },
        )

    def test_it_sends_an_email_on_workout_with_gpx_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_suspension_email_mock: MagicMock,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_suspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "workout_suspension", None
        )

        workout_suspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_2.email,
            },
            {
                'fittrackee_url': app.config['UI_URL'],
                'map': (
                    f'{app.config["UI_URL"]}/api/workouts/map'
                    f'/{workout_cycling_user_2.map_id}'
                ),
                'reason': None,
                'title': workout_cycling_user_2.title,
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_2.username,
                'workout_date': get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                'workout_url': (
                    f'{app.config["UI_URL"]}/workouts/'
                    f'{workout_cycling_user_2.short_id}'
                ),
            },
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "foo"}])
    def test_it_sends_an_email_on_workout_reactivation(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_unsuspension_email_mock: MagicMock,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "workout_unsuspension", input_reason.get("reason")
        )

        workout_unsuspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_2.email,
            },
            {
                'fittrackee_url': app.config['UI_URL'],
                'map': None,
                'reason': input_reason.get('reason'),
                'title': workout_cycling_user_2.title,
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_2.username,
                'workout_date': get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                'workout_url': (
                    f'{app.config["UI_URL"]}/workouts/'
                    f'{workout_cycling_user_2.short_id}'
                ),
            },
        )

    def test_it_sends_an_email_on_workout_with_gpx_reactivation(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        workout_unsuspension_email_mock: MagicMock,
    ) -> None:
        workout_cycling_user_2.map_id = self.random_short_id()
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.flush()
        report_email_service = ReportEmailService()

        report_email_service.send_admin_action_email(
            report, "workout_unsuspension", None
        )

        workout_unsuspension_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_2.email,
            },
            {
                'fittrackee_url': app.config['UI_URL'],
                'map': (
                    f'{app.config["UI_URL"]}/api/workouts/map'
                    f'/{workout_cycling_user_2.map_id}'
                ),
                'reason': None,
                'title': workout_cycling_user_2.title,
                'user_image_url': f'{app.config["UI_URL"]}/img/user.png',
                'username': user_2.username,
                'workout_date': get_date_string_for_user(
                    workout_cycling_user_2.workout_date, user_2
                ),
                'workout_url': (
                    f'{app.config["UI_URL"]}/workouts/'
                    f'{workout_cycling_user_2.short_id}'
                ),
            },
        )

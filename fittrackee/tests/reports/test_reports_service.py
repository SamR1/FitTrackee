from datetime import datetime, timedelta

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.exceptions import (
    InvalidReporterException,
    ReportNotFoundException,
)
from fittrackee.reports.models import ReportComment
from fittrackee.reports.service import ReportService
from fittrackee.tests.comments.utils import CommentMixin
from fittrackee.users.exceptions import UserNotFoundException
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout

from ..mixins import RandomMixin


class TestReportServiceCreateForComment(CommentMixin):
    def test_it_raises_exception_when_reported_comment_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        report_service = ReportService()

        with pytest.raises(CommentForbiddenException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=self.random_short_id(),
                object_type="comment",
            )

    def test_it_raises_exception_when_reported_comment_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        report_service = ReportService()

        with pytest.raises(CommentForbiddenException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=comment.short_id,
                object_type="comment",
            )

    def test_it_raises_exception_when_reporter_is_comment_author(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        report_service = ReportService()

        with pytest.raises(InvalidReporterException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=comment.short_id,
                object_type="comment",
            )

    def test_it_creates_report_for_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        note = self.random_string()
        now = datetime.utcnow()
        report_service = ReportService()

        with freeze_time(now):
            comment_report = report_service.create_report(
                reporter=user_2,
                note=note,
                object_id=comment.short_id,
                object_type="comment",
            )

        assert comment_report.created_at == now
        assert comment_report.note == note
        assert comment_report.object_type == "comment"
        assert comment_report.reported_by == user_2.id
        assert comment_report.reported_comment_id == comment_report.id
        assert comment_report.reported_workout_id is None
        assert comment_report.reported_user_id is None
        assert comment_report.resolved is False
        assert comment_report.resolved_at is None
        assert comment_report.resolved_by is None
        assert comment_report.updated_at is None


class TestReportServiceCreateForWorkout(RandomMixin):
    def test_it_raises_exception_when_reported_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        report_service = ReportService()

        with pytest.raises(WorkoutForbiddenException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=self.random_short_id(),
                object_type="workout",
            )

    def test_it_raises_exception_when_reported_workout_is_not_visible(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        report_service = ReportService()

        with pytest.raises(WorkoutForbiddenException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=workout_cycling_user_2.short_id,
                object_type="workout",
            )

    def test_it_raises_exception_when_reporter_is_workout_owner(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        report_service = ReportService()

        with pytest.raises(InvalidReporterException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=workout_cycling_user_1.short_id,
                object_type="workout",
            )

    def test_it_creates_report_for_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        note = self.random_string()
        now = datetime.utcnow()
        report_service = ReportService()

        with freeze_time(now):
            workout_report = report_service.create_report(
                reporter=user_1,
                note=note,
                object_id=workout_cycling_user_2.short_id,
                object_type="workout",
            )

        assert workout_report.created_at == now
        assert workout_report.note == note
        assert workout_report.object_type == "workout"
        assert workout_report.reported_by == user_1.id
        assert workout_report.reported_comment_id is None
        assert workout_report.reported_workout_id == workout_cycling_user_2.id
        assert workout_report.reported_user_id is None
        assert workout_report.resolved is False
        assert workout_report.resolved_at is None
        assert workout_report.resolved_by is None
        assert workout_report.updated_at is None


class TestReportServiceCreateForUser(RandomMixin):
    def test_it_raises_exception_when_reported_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        report_service = ReportService()

        with pytest.raises(UserNotFoundException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=self.random_string(),
                object_type="user",
            )

    def test_it_raises_exception_when_reported_user_is_inactive(
        self, app: Flask, user_1: User, inactive_user: User
    ) -> None:
        report_service = ReportService()

        with pytest.raises(UserNotFoundException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=inactive_user.username,
                object_type="user",
            )

    def test_it_raises_exception_when_reporter_is_reported_user(
        self, app: Flask, user_1: User
    ) -> None:
        report_service = ReportService()

        with pytest.raises(InvalidReporterException):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=user_1.username,
                object_type="user",
            )

    def test_it_creates_report_for_user(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        note = self.random_string()
        now = datetime.utcnow()
        report_service = ReportService()

        with freeze_time(now):
            user_report = report_service.create_report(
                reporter=user_1,
                note=note,
                object_id=user_2.username,
                object_type="user",
            )

        assert user_report.created_at == now
        assert user_report.note == note
        assert user_report.object_type == "user"
        assert user_report.reported_by == user_1.id
        assert user_report.reported_comment_id is None
        assert user_report.reported_workout_id is None
        assert user_report.reported_user_id == user_2.id
        assert user_report.resolved is False
        assert user_report.resolved_at is None
        assert user_report.resolved_by is None
        assert user_report.updated_at is None


class TestReportServiceUpdate(CommentMixin):
    def test_it_raises_exception_when_report_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        report_service = ReportService()

        with pytest.raises(ReportNotFoundException):
            report_service.update_report(
                report_id=self.random_int(),
                admin_user=user_1_admin,
                report_comment=self.random_string(),
            )

    def test_it_updates_report_when_adding_comment(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        note = self.random_string()
        report = report_service.create_report(
            reporter=user_2,
            note=note,
            object_id=user_3.username,
            object_type="user",
        )
        created_at = report.created_at
        now = datetime.utcnow()

        with freeze_time(now):
            updated_report = report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
            )

        assert updated_report.created_at == created_at
        assert updated_report.note == note
        assert updated_report.object_type == "user"
        assert updated_report.reported_by == user_2.id
        assert updated_report.reported_comment_id is None
        assert updated_report.reported_workout_id is None
        assert updated_report.reported_user_id == user_3.id
        assert updated_report.resolved is False
        assert updated_report.resolved_at is None
        assert updated_report.resolved_by is None
        assert updated_report.updated_at == now

    def test_it_creates_a_report_comment_when_it_updates_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=user_3.username,
            object_type="user",
        )
        comment = self.random_string()
        now = datetime.utcnow()

        with freeze_time(now):
            report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=comment,
            )

        report_comment = ReportComment.query.filter_by(
            report_id=report.id
        ).first()
        assert report_comment.comment == comment
        assert report_comment.created_at == now
        assert report_comment.user_id == user_1_admin.id

    def test_it_marks_report_as_resolved(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        note = self.random_string()
        report = report_service.create_report(
            reporter=user_2,
            note=note,
            object_id=user_3.username,
            object_type="user",
        )
        created_at = report.created_at
        now = datetime.utcnow()

        with freeze_time(now):
            updated_report = report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=True,
            )

        assert updated_report.created_at == created_at
        assert updated_report.note == note
        assert updated_report.object_type == "user"
        assert updated_report.reported_by == user_2.id
        assert updated_report.reported_comment_id is None
        assert updated_report.reported_workout_id is None
        assert updated_report.reported_user_id == user_3.id
        assert updated_report.resolved is True
        assert updated_report.resolved_at == now
        assert updated_report.resolved_by == user_1_admin.id
        assert updated_report.updated_at == now

    def test_it_marks_report_as_unresolved(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        note = self.random_string()
        report = report_service.create_report(
            reporter=user_2,
            note=note,
            object_id=user_3.username,
            object_type="user",
        )
        created_at = report.created_at
        report.resolved = True
        report.resolved_at = datetime.utcnow()
        report.resolved_by = user_1_admin.id
        now = datetime.utcnow()

        with freeze_time(now):
            updated_report = report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=False,
            )

        assert updated_report.created_at == created_at
        assert updated_report.note == note
        assert updated_report.object_type == "user"
        assert updated_report.reported_by == user_2.id
        assert updated_report.reported_comment_id is None
        assert updated_report.reported_workout_id is None
        assert updated_report.reported_user_id == user_3.id
        assert updated_report.resolved is False
        assert updated_report.resolved_at is None
        assert updated_report.resolved_by is None
        assert updated_report.updated_at == now

    def test_it_updates_resolved_report_when_adding_comment(
        self, app: Flask, user_1_admin: User, user_2_admin: User, user_3: User
    ) -> None:
        report_service = ReportService()
        note = self.random_string()
        report = report_service.create_report(
            reporter=user_2_admin,
            note=note,
            object_id=user_3.username,
            object_type="user",
        )
        created_at = report.created_at
        resolved_time = datetime.utcnow()

        # resolved by user_1_admin
        with freeze_time(resolved_time):
            report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=True,
            )

        # comment added by user_2_admin
        comment_time = resolved_time + timedelta(minutes=10)
        with freeze_time(comment_time):
            updated_report = report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
            )

        assert updated_report.created_at == created_at
        assert updated_report.note == note
        assert updated_report.object_type == "user"
        assert updated_report.reported_by == user_2_admin.id
        assert updated_report.reported_comment_id is None
        assert updated_report.reported_workout_id is None
        assert updated_report.reported_user_id == user_3.id
        assert updated_report.resolved is True
        assert updated_report.resolved_at == resolved_time
        assert updated_report.resolved_by == user_1_admin.id
        assert updated_report.updated_at == comment_time

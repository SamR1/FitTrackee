from datetime import datetime, timedelta

import pytest
from flask import Flask
from time_machine import travel

from fittrackee.administration.models import AdminAction
from fittrackee.administration.reports_service import ReportService
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.exceptions import (
    InvalidReporterException,
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
)
from fittrackee.reports.models import ReportComment
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
        user_3: User,
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
        # report from another user
        report_service.create_report(
            reporter=user_3,
            note=self.random_string(),
            object_id=comment.short_id,
            object_type="comment",
        )
        # resolved report from same user
        report = report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=comment.short_id,
            object_type="comment",
        )
        report.resolved = True

        with travel(now, tick=False):
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
        assert comment_report.reported_comment_id == comment.id
        assert comment_report.reported_workout_id is None
        assert comment_report.reported_user_id == user_1.id
        assert comment_report.resolved is False
        assert comment_report.resolved_at is None
        assert comment_report.resolved_by is None
        assert comment_report.updated_at is None

    def test_it_raises_error_when_report_from_the_same_user_already_exists(
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
        report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=comment.short_id,
            object_type="comment",
        )

        with pytest.raises(
            InvalidReportException, match='a report already exists'
        ):
            report_service.create_report(
                reporter=user_2,
                note=self.random_string(),
                object_id=comment.short_id,
                object_type="comment",
            )

    def test_it_raises_error_when_comment_is_already_suspended(
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
        comment.suspended_at = datetime.utcnow()
        report_service = ReportService()

        with pytest.raises(
            SuspendedObjectException, match='comment already suspended'
        ):
            report_service.create_report(
                reporter=user_2,
                note=self.random_string(),
                object_id=comment.short_id,
                object_type="comment",
            )


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
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        note = self.random_string()
        now = datetime.utcnow()
        report_service = ReportService()
        # report from another user
        report_service.create_report(
            reporter=user_3,
            note=note,
            object_id=workout_cycling_user_2.short_id,
            object_type="workout",
        )
        # resolved report from same user
        report = report_service.create_report(
            reporter=user_1,
            note=self.random_string(),
            object_id=workout_cycling_user_2.short_id,
            object_type="workout",
        )
        report.resolved = True

        with travel(now, tick=False):
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
        assert workout_report.reported_user_id == user_2.id
        assert workout_report.resolved is False
        assert workout_report.resolved_at is None
        assert workout_report.resolved_by is None
        assert workout_report.updated_at is None

    def test_it_raises_error_when_report_from_the_same_user_already_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report_service = ReportService()
        # report from same user
        report_service.create_report(
            reporter=user_1,
            note=self.random_string(),
            object_id=workout_cycling_user_2.short_id,
            object_type="workout",
        )

        with pytest.raises(
            InvalidReportException, match='a report already exists'
        ):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=workout_cycling_user_2.short_id,
                object_type="workout",
            )

    def test_it_raises_error_when_workout_is_already_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        report_service = ReportService()

        with pytest.raises(
            SuspendedObjectException, match='workout already suspended'
        ):
            report_service.create_report(
                reporter=user_2,
                note=self.random_string(),
                object_id=workout_cycling_user_2.short_id,
                object_type="workout",
            )


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
        self, app: Flask, user_1: User, user_2: User, user_3: User
    ) -> None:
        note = self.random_string()
        now = datetime.utcnow()
        report_service = ReportService()
        # report from another user
        report_service.create_report(
            reporter=user_3,
            note=note,
            object_id=user_2.username,
            object_type="user",
        )
        # resolved report from same user
        report = report_service.create_report(
            reporter=user_1,
            note=note,
            object_id=user_2.username,
            object_type="user",
        )
        report.resolved = True

        with travel(now, tick=False):
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

    def test_it_raises_error_when_report_from_the_same_user_already_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        # report from same user
        report_service.create_report(
            reporter=user_1,
            note=self.random_string(),
            object_id=user_2.username,
            object_type="user",
        )

        with pytest.raises(
            InvalidReportException, match='a report already exists'
        ):
            report_service.create_report(
                reporter=user_1,
                note=self.random_string(),
                object_id=user_2.username,
                object_type="user",
            )

    def test_it_raises_error_when_user_is_already_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        user_1.suspended_at = datetime.utcnow()
        report_service = ReportService()

        with pytest.raises(
            SuspendedObjectException, match='user already suspended'
        ):
            report_service.create_report(
                reporter=user_2,
                note=self.random_string(),
                object_id=user_1.username,
                object_type="user",
            )


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

        with travel(now, tick=False):
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

        with travel(now, tick=False):
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

    def test_it_does_not_create_admin_action_on_report_comment(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=user_3.username,
            object_type="user",
        )

        report_service.update_report(
            report_id=report.id,
            admin_user=user_1_admin,
            report_comment=self.random_string(),
        )

        assert AdminAction.query.filter_by(report_id=report.id).count() == 0

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

        with travel(now, tick=False):
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

    def test_it_creates_report_action_when_resolving_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=user_3.username,
            object_type="user",
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=True,
            )

        report_action = AdminAction.query.filter_by(
            report_id=report.id
        ).first()
        assert report_action.action_type == "report_resolution"
        assert report_action.admin_user_id == user_1_admin.id
        assert report_action.created_at == now
        assert report_action.report_id == report.id

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

        with travel(now, tick=False):
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

    def test_it_creates_report_action_when_make_report_as_unresolved(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=user_3.username,
            object_type="user",
        )
        report.resolved = True
        report.resolved_at = datetime.utcnow()
        report.resolved_by = user_1_admin.id
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=False,
            )

        report_action = AdminAction.query.filter_by(
            report_id=report.id
        ).first()
        assert report_action.action_type == "report_reopening"
        assert report_action.admin_user_id == user_1_admin.id
        assert report_action.created_at == now
        assert report_action.report_id == report.id

    def test_it_does_not_create_report_action_when_already_unresolved(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = report_service.create_report(
            reporter=user_2,
            note=self.random_string(),
            object_id=user_3.username,
            object_type="user",
        )

        with travel(datetime.utcnow(), tick=False):
            report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=False,
            )

        assert AdminAction.query.filter_by(report_id=report.id).count() == 0

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
        with travel(resolved_time, tick=False):
            report_service.update_report(
                report_id=report.id,
                admin_user=user_1_admin,
                report_comment=self.random_string(),
                resolved=True,
            )

        # comment added by user_2_admin
        comment_time = resolved_time + timedelta(minutes=10)
        with travel(comment_time, tick=False):
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

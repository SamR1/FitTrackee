from datetime import datetime, timedelta
from typing import Dict

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.administration.models import AdminAction, AdminActionAppeal
from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Comment
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.exceptions import (
    InvalidAdminActionException,
    InvalidReporterException,
    InvalidReportException,
    ReportNotFoundException,
    SuspendedObjectException,
    UserWarningExistsException,
)
from fittrackee.reports.models import ReportComment
from fittrackee.reports.reports_service import ReportService
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.exceptions import (
    UserAlreadySuspendedException,
    UserNotFoundException,
)
from fittrackee.users.models import User
from fittrackee.workouts.exceptions import WorkoutForbiddenException
from fittrackee.workouts.models import Sport, Workout

from ..mixins import RandomMixin, UserModerationMixin
from ..workouts.mixins import WorkoutMixin
from .mixins import ReportServiceCreateAdminActionMixin


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


class TestReportServiceCreateAdminAction(ReportServiceCreateAdminActionMixin):
    def test_it_raises_exception_when_reported_user_does_not_exist(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        db.session.delete(user_3)
        db.session.flush()

        with pytest.raises(
            InvalidAdminActionException, match="invalid 'username'"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_suspension",
                data={"username": user_3.username},
            )

    def test_it_raises_exception_when_admin_action_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )

        with pytest.raises(
            InvalidAdminActionException, match="invalid action type"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type=self.random_string(),
                data={"username": user_3.username},
            )


class TestReportServiceCreateAdminActionForUser(
    ReportServiceCreateAdminActionMixin
):
    def test_it_raises_exception_when_username_is_missing(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )

        with pytest.raises(
            InvalidAdminActionException, match="'username' is missing"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_suspension",
                data={},
            )

    def test_it_raises_exception_when_username_does_not_match_reported_user_username(  # noqa
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )

        with pytest.raises(
            InvalidAdminActionException, match="invalid 'username'"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_suspension",
                data={"username": self.random_string()},
            )

    def test_it_suspends_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_suspension",
                reason=None,
                data={"username": user_3.username},
            )

        assert (
            User.query.filter_by(username=user_3.username).first().suspended_at
            == now
        )

    def test_it_raises_exception_when_user_already_suspended(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.utcnow()
        db.session.flush()

        with pytest.raises(
            UserAlreadySuspendedException,
            match=f"user '{user_3.username}' already suspended",
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_suspension",
                reason=None,
                data={"username": user_3.username},
            )

    def test_it_reactivates_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.utcnow()
        db.session.flush()

        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_unsuspension",
            reason=None,
            data={"username": user_3.username},
        )

        assert (
            User.query.filter_by(username=user_3.username).first().suspended_at
            is None
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "some reason"}])
    def test_it_creates_admin_action_for_user_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_suspension",
                reason=input_reason.get("reason"),
                data={"username": user_3.username},
            )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "user_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == now
        assert admin_action.comment_id is None
        assert admin_action.reason == input_reason.get("reason")
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_creates_admin_action_for_user_reactivation(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        user_3.suspended_at = datetime.utcnow()
        db.session.flush()

        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_unsuspension",
            data={"username": user_3.username},
        )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "user_unsuspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_creates_admin_action_for_user_warning_on_user_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )

        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_warning",
            data={"username": user_3.username},
        )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "user_warning"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_creates_admin_action_for_user_warning_on_comment_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )

        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_warning",
            data={"username": user_3.username},
        )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "user_warning"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id == report.reported_comment_id
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_creates_admin_action_for_user_warning_on_workout_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )

        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_warning",
            data={"username": user_2.username},
        )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "user_warning"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id == report.reported_workout_id

    def test_it_raises_exception_when_user_warning_already_exists_for_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_warning",
            data={"username": user_3.username},
        )

        with pytest.raises(
            UserWarningExistsException,
            match="user already warned",
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="user_warning",
                data={"username": user_3.username},
            )

    def test_it_creates_admin_action_for_user_warning_when_warning_exists_for_another_report(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_4: User,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_user(
            report_service, reporter=user_2, reported_user=user_3
        )
        another_report = self.create_report_for_user(
            report_service, reporter=user_4, reported_user=user_3
        )
        report_service.create_admin_action(
            report=another_report,
            admin_user=user_1_admin,
            action_type="user_warning",
            data={"username": user_3.username},
        )

        report_service.create_admin_action(
            report=report,
            admin_user=user_1_admin,
            action_type="user_warning",
            data={"username": user_3.username},
        )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "user_warning"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.report_id == report.id
        assert admin_action.comment_id is None
        assert admin_action.reason is None
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None


class TestReportServiceCreateAdminActionForComment(
    ReportServiceCreateAdminActionMixin
):
    def test_it_raises_exception_when_report_is_invalid(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )

        with pytest.raises(
            InvalidAdminActionException, match="'comment_id' is missing"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="comment_suspension",
                data={},
            )

    def test_it_raises_exception_when_comment_id_does_not_match_reported_object_id(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )

        with pytest.raises(
            InvalidAdminActionException, match="invalid 'comment_id'"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="comment_suspension",
                data={"comment_id": self.random_short_id()},
            )

    def test_it_raises_error_when_comment_is_already_suspended(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
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

        with pytest.raises(
            InvalidAdminActionException,
            match=(
                f"comment '{report.reported_comment.short_id}' "
                "already suspended"
            ),
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="comment_suspension",
                data={"comment_id": report.reported_comment.short_id},
            )

    def test_it_suspends_comment(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="comment_suspension",
                data={"comment_id": report.reported_comment.short_id},
            )

        assert (
            Comment.query.filter_by(id=report.reported_comment_id)
            .first()
            .suspended_at
            == now
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "some reason"}])
    def test_it_creates_admin_action_for_comment_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            reporter=user_2,
            commenter=user_3,
            workout=workout_cycling_user_2,
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                reason=input_reason.get("reason"),
                action_type="comment_suspension",
                data={"comment_id": report.reported_comment.short_id},
            )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "comment_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == now
        assert admin_action.comment_id == report.reported_comment_id
        assert admin_action.reason == input_reason.get("reason")
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_unsuspends_comment(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
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
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="comment_unsuspension",
                data={"comment_id": report.reported_comment.short_id},
            )

        assert (
            Comment.query.filter_by(id=report.reported_comment_id)
            .first()
            .suspended_at
            is None
        )

    def test_it_creates_admin_action_for_comment_unsuspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
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
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="comment_unsuspension",
                data={"comment_id": report.reported_comment.short_id},
            )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "comment_unsuspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == now
        assert admin_action.comment_id == report.reported_comment_id
        assert admin_action.reason is None
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None


class TestReportServiceCreateAdminActionForWorkout(
    ReportServiceCreateAdminActionMixin
):
    def test_it_raises_exception_when_report_is_invalid(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_comment(
            report_service,
            commenter=user_3,
            reporter=user_2,
            workout=workout_cycling_user_2,
        )

        with pytest.raises(
            InvalidAdminActionException, match="'workout_id' is missing"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="workout_suspension",
                data={},
            )

    def test_it_raises_exception_when_workout_id_does_not_match_reported_object_id(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )

        with pytest.raises(
            InvalidAdminActionException, match="invalid 'workout_id'"
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="workout_suspension",
                data={"workout_id": self.random_short_id()},
            )

    def test_it_raises_error_when_workout_is_already_suspended(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_workout.suspended_at = datetime.utcnow()
        db.session.flush()

        with pytest.raises(
            InvalidAdminActionException,
            match=(
                f"workout '{report.reported_workout.short_id}' "
                "already suspended"
            ),
        ):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="workout_suspension",
                data={"workout_id": report.reported_workout.short_id},
            )

    def test_it_suspends_workout(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="workout_suspension",
                data={"workout_id": report.reported_workout.short_id},
            )

        assert (
            Workout.query.filter_by(id=report.reported_workout_id)
            .first()
            .suspended_at
            == now
        )

    @pytest.mark.parametrize('input_reason', [{}, {"reason": "some reason"}])
    def test_it_creates_admin_action_for_workout_suspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_reason: Dict,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                reason=input_reason.get("reason"),
                action_type="workout_suspension",
                data={"workout_id": report.reported_workout.short_id},
            )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "workout_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == now
        assert admin_action.comment_id is None
        assert admin_action.reason == input_reason.get("reason")
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id == report.reported_workout_id

    def test_it_unsuspends_workout(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()
        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_workout.suspended_at = datetime.utcnow()
        db.session.flush()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="workout_unsuspension",
                data={"workout_id": report.reported_workout.short_id},
            )

        assert (
            Workout.query.filter_by(id=report.reported_workout_id)
            .first()
            .suspended_at
            is None
        )

    def test_it_creates_admin_action_for_workout_unsuspension(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_service = ReportService()

        report = self.create_report_for_workout(
            report_service,
            reporter=user_3,
            workout=workout_cycling_user_2,
        )
        report.reported_workout.suspended_at = datetime.utcnow()
        db.session.flush()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.create_admin_action(
                report=report,
                admin_user=user_1_admin,
                action_type="workout_unsuspension",
                data={"workout_id": report.reported_workout.short_id},
            )

        admin_action = AdminAction.query.filter_by(report_id=report.id).first()
        assert admin_action.action_type == "workout_unsuspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == now
        assert admin_action.comment_id is None
        assert admin_action.reason is None
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id is report.reported_workout_id


class TestReportServiceProcessAppeal(
    ReportServiceCreateAdminActionMixin, UserModerationMixin, WorkoutMixin
):
    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_process_user_suspension_appeal(
        self, app: Flask, user_1_admin: User, user_2: User, input_data: Dict
    ) -> None:
        suspension_action = self.create_user_suspension_action(
            user_1_admin, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        report_service = ReportService()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.process_appeal(
                appeal=appeal,
                admin_user=user_1_admin,
                data=input_data,
            )

        updated_appeal = AdminActionAppeal.query.filter_by(
            id=appeal.id
        ).first()
        assert updated_appeal.admin_user_id == user_1_admin.id
        assert updated_appeal.approved is input_data["approved"]
        assert updated_appeal.reason == input_data["reason"]
        assert updated_appeal.updated_at == now

    def test_it_unsuspends_user_when_appeal_is_approved(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        suspension_action = self.create_user_suspension_action(
            user_1_admin, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        report_service = ReportService()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.process_appeal(
                appeal=appeal,
                admin_user=user_1_admin,
                data={"approved": True, "reason": "ok"},
            )

        assert user_2.suspended_at is None

    def test_it_creates_unsuspended_user_action_when_appeal_is_approved(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        suspension_action = self.create_user_suspension_action(
            user_1_admin, user_2
        )
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        report_service = ReportService()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.process_appeal(
                appeal=appeal,
                admin_user=user_1_admin,
                data={"approved": True, "reason": "ok"},
            )

        assert (
            AdminAction.query.filter_by(
                report_id=suspension_action.report_id,
                action_type="user_unsuspension",
                admin_user_id=user_1_admin.id,
                user_id=user_2.id,
                reason=None,
                created_at=now,
            ).first()
            is not None
        )

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_process_comment_suspension_appeal(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        suspension_action = self.create_admin_comment_suspension_action(
            user_1_admin, user_3, comment
        )
        comment_suspended_at = comment.suspended_at
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.commit()
        report_service = ReportService()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.process_appeal(
                appeal=appeal,
                admin_user=user_1_admin,
                data=input_data,
            )

        updated_appeal = AdminActionAppeal.query.filter_by(
            id=appeal.id
        ).first()
        assert updated_appeal.admin_user_id == user_1_admin.id
        assert updated_appeal.approved is input_data["approved"]
        assert updated_appeal.reason == input_data["reason"]
        assert updated_appeal.updated_at == now
        assert comment.suspended_at == (
            None if input_data["approved"] else comment_suspended_at
        )

    def test_it_creates_unsuspended_comment_action_when_appeal_is_approved(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        suspension_action = self.create_admin_comment_suspension_action(
            user_1_admin, user_3, comment
        )
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_3)
        db.session.commit()
        report_service = ReportService()
        reason = self.random_string()

        report_service.process_appeal(
            appeal=appeal,
            admin_user=user_1_admin,
            data={"approved": True, "reason": reason},
        )

        assert (
            AdminAction.query.filter_by(
                admin_user_id=user_1_admin.id,
                action_type="comment_unsuspension",
                comment_id=comment.id,
                report_id=suspension_action.report_id,
                user_id=user_3.id,
            ).first()
            is not None
        )

    @pytest.mark.parametrize(
        "input_data",
        [
            {"approved": True, "reason": "ok"},
            {"approved": False, "reason": "not ok"},
        ],
    )
    def test_it_process_workout_suspension_appeal(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_data: Dict,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        suspension_action = self.create_admin_workout_suspension_action(
            user_1_admin, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        workout_suspended_at = workout_cycling_user_2.suspended_at
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        report_service = ReportService()
        now = datetime.utcnow()

        with travel(now, tick=False):
            report_service.process_appeal(
                appeal=appeal,
                admin_user=user_1_admin,
                data=input_data,
            )

        updated_appeal = AdminActionAppeal.query.filter_by(
            id=appeal.id
        ).first()
        assert updated_appeal.admin_user_id == user_1_admin.id
        assert updated_appeal.approved is input_data["approved"]
        assert updated_appeal.reason == input_data["reason"]
        assert updated_appeal.updated_at == now
        assert workout_cycling_user_2.suspended_at == (
            None if input_data["approved"] else workout_suspended_at
        )

    def test_it_creates_unsuspended_workout_action_when_appeal_is_approved(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        suspension_action = self.create_admin_workout_suspension_action(
            user_1_admin, user_2, workout_cycling_user_2
        )
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        db.session.flush()
        appeal = self.create_action_appeal(suspension_action.id, user_2)
        db.session.commit()
        report_service = ReportService()
        reason = self.random_string()

        report_service.process_appeal(
            appeal=appeal,
            admin_user=user_1_admin,
            data={"approved": True, "reason": reason},
        )

        assert (
            AdminAction.query.filter_by(
                action_type="workout_unsuspension",
                admin_user_id=user_1_admin.id,
                reason=None,
                report_id=suspension_action.report_id,
                user_id=user_2.id,
                workout_id=workout_cycling_user_2.id,
            ).first()
            is not None
        )
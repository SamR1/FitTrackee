from datetime import datetime

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.exceptions import (
    InvalidReportException,
    ReportCommentForbiddenException,
    ReportForbiddenException,
)
from fittrackee.reports.models import Report, ReportComment
from fittrackee.tests.comments.utils import CommentMixin
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import RandomMixin


class TestReportModel(CommentMixin, RandomMixin):
    def test_it_raises_exception_when_reported_object_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        with pytest.raises(InvalidReportException):
            Report(
                reported_by=user_1.id,
                note=self.random_string(),
                object_type=self.random_string(),
                object_id=self.random_int(),
            )

    def test_it_creates_report_for_a_comment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        report_created_at = datetime.now()
        report_note = self.random_string()
        comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )

        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=comment.id,
            object_type='comment',
            created_at=report_created_at,
        )

        assert report.created_at == report_created_at
        assert report.note == report_note
        assert report.reported_by == user_1.id
        assert report.resolved is False
        assert report.updated_at is None
        assert report.reported_comment_id == comment.id
        assert report.reported_user_id is None
        assert report.reported_workout_id is None

    def test_it_creates_report_for_a_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        report_created_at = datetime.now()
        report_note = self.random_string()

        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=user_2.id,
            object_type='user',
            created_at=report_created_at,
        )

        assert report.created_at == report_created_at
        assert report.note == report_note
        assert report.reported_by == user_1.id
        assert report.resolved is False
        assert report.updated_at is None
        assert report.reported_comment_id is None
        assert report.reported_user_id == user_2.id
        assert report.reported_workout_id is None

    def test_it_creates_report_for_a_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report_created_at = datetime.now()
        report_note = self.random_string()

        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=workout_cycling_user_2.id,
            object_type='workout',
            created_at=report_created_at,
        )

        assert report.created_at == report_created_at
        assert report.note == report_note
        assert report.reported_by == user_1.id
        assert report.resolved is False
        assert report.updated_at is None
        assert report.reported_comment_id is None
        assert report.reported_user_id is None
        assert report.reported_workout_id == workout_cycling_user_2.id

    def test_it_creates_report_without_date(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        now = datetime.now()
        report_note = self.random_string()

        with freeze_time(now):
            report = Report(
                reported_by=user_1.id,
                note=report_note,
                object_id=user_2.id,
                object_type='user',
            )

        assert report.created_at == now
        assert report.note == report_note
        assert report.reported_by == user_1.id
        assert report.resolved is False
        assert report.updated_at is None
        assert report.reported_comment_id is None
        assert report.reported_user_id == user_2.id
        assert report.reported_workout_id is None


class TestReportSerializerAsUser(CommentMixin, RandomMixin):
    def test_it_raises_exception_when_user_is_not_reporter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        user_3: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        report_created_at = datetime.now()
        report_note = self.random_string()
        comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )
        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=comment.id,
            object_type='comment',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.commit()

        with pytest.raises(ReportForbiddenException):
            report.serialize(user_3)

    def test_it_returns_serialized_object_for_comment_report(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        report_created_at = datetime.now()
        report_note = self.random_string()
        comment = self.create_comment(
            user_2, workout_cycling_user_1, text_visibility=PrivacyLevel.PUBLIC
        )
        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=comment.id,
            object_type='comment',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.commit()

        serialized_report = report.serialize(user_1)

        assert serialized_report == {
            "created_at": report.created_at,
            "note": report_note,
            "reported_by": user_1.serialize(user_1),
            "reported_comment": comment.serialize(user_1),
            "reported_user": None,
            "reported_workout": None,
            "resolved": False,
            "updated_at": None,
        }

    def test_it_returns_serialized_object_for_user_report(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
    ) -> None:
        report_created_at = datetime.now()
        report_note = self.random_string()
        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=user_2.id,
            object_type='user',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.commit()

        serialized_report = report.serialize(user_1)

        assert serialized_report == {
            "created_at": report.created_at,
            "note": report_note,
            "reported_by": user_1.serialize(user_1),
            "reported_comment": None,
            "reported_user": user_2.serialize(user_1),
            "reported_workout": None,
            "resolved": False,
            "updated_at": None,
        }

    def test_it_returns_serialized_object_for_workout_report(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        report_created_at = datetime.now()
        report_note = self.random_string()
        report = Report(
            reported_by=user_1.id,
            note=report_note,
            object_id=workout_cycling_user_2.id,
            object_type='workout',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.commit()

        serialized_report = report.serialize(user_1)

        assert serialized_report == {
            "created_at": report.created_at,
            "note": report_note,
            "reported_by": user_1.serialize(user_1),
            "reported_comment": None,
            "reported_user": None,
            "reported_workout": workout_cycling_user_2.serialize(user_1),
            "resolved": False,
            "updated_at": None,
        }

    def test_it_returns_serialized_object_without_report_comments(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report_created_at = datetime.now()
        report_note = self.random_string()
        report = Report(
            reported_by=user_2.id,
            note=report_note,
            object_id=user_3.id,
            object_type='user',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.flush()
        report_comment = ReportComment(
            report_id=report.id,
            user_id=user_1_admin.id,
            comment=self.random_string(),
        )
        db.session.add(report_comment)
        db.session.commit()

        serialized_report = report.serialize(user_2)

        assert serialized_report == {
            "created_at": report.created_at,
            "note": report_note,
            "reported_by": user_2.serialize(user_2),
            "reported_comment": None,
            "reported_user": user_3.serialize(user_2),
            "reported_workout": None,
            "resolved": False,
            "updated_at": None,
        }


class TestReportSerializerAsAdmin(CommentMixin, RandomMixin):
    def test_it_returns_serialized_object_when_no_report_comments(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report_created_at = datetime.now()
        report_note = self.random_string()
        report = Report(
            reported_by=user_2.id,
            note=report_note,
            object_id=user_3.id,
            object_type='user',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.commit()

        serialized_report = report.serialize(user_1_admin)

        assert serialized_report == {
            "created_at": report.created_at,
            "note": report_note,
            "reported_by": user_2.serialize(user_1_admin),
            "reported_comment": None,
            "reported_user": user_3.serialize(user_1_admin),
            "reported_workout": None,
            "resolved": False,
            "updated_at": None,
            "comments": [],
        }

    def test_it_returns_serialized_object_with_report_comments(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report_created_at = datetime.now()
        report_note = self.random_string()
        report = Report(
            reported_by=user_2.id,
            note=report_note,
            object_id=user_3.id,
            object_type='user',
            created_at=report_created_at,
        )
        db.session.add(report)
        db.session.flush()
        report_comment = ReportComment(
            report_id=report.id,
            user_id=user_1_admin.id,
            comment=self.random_string(),
        )
        db.session.add(report_comment)
        db.session.commit()

        serialized_report = report.serialize(user_1_admin)

        assert serialized_report == {
            "created_at": report.created_at,
            "note": report_note,
            "reported_by": user_2.serialize(user_1_admin),
            "reported_comment": None,
            "reported_user": user_3.serialize(user_1_admin),
            "reported_workout": None,
            "resolved": False,
            "updated_at": None,
            "comments": [report_comment.serialize(user_1_admin)],
        }


class ReportCommentTestCase(CommentMixin, RandomMixin):
    def create_report(self, reporter: User, reported_user: User) -> Report:
        report = Report(
            reported_by=reporter.id,
            note=self.random_string(),
            object_type='user',
            object_id=reported_user.id,
        )
        db.session.add(report)
        db.session.commit()
        return report


class TestReportCommentModel(ReportCommentTestCase):
    def test_it_creates_comment_for_a_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
        created_at = datetime.now()
        comment = self.random_string()

        report_comment = ReportComment(
            report_id=report.id,
            user_id=user_1_admin.id,
            comment=comment,
            created_at=created_at,
        )
        db.session.add(report_comment)
        db.session.commit()

        assert report_comment.created_at == created_at
        assert report_comment.comment == comment
        assert report_comment.report_id == report.id
        assert report_comment.user_id == user_1_admin.id

    def test_it_creates_comment_for_a_report_without_date(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
        comment = self.random_string()
        now = datetime.utcnow()

        with freeze_time(now):
            report_comment = ReportComment(
                report_id=report.id,
                user_id=user_1_admin.id,
                comment=comment,
            )
        db.session.add(report_comment)
        db.session.commit()

        assert report_comment.created_at == now
        assert report_comment.comment == comment
        assert report_comment.report_id == report.id
        assert report_comment.user_id == user_1_admin.id


class TestReportCommentSerializer(ReportCommentTestCase):
    def test_it_raises_exception_when_user_has_no_admin_rights(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
        report_comment = ReportComment(
            report_id=report.id,
            user_id=user_1_admin.id,
            comment=self.random_string(),
        )

        with pytest.raises(ReportCommentForbiddenException):
            report_comment.serialize(user_2)

    def test_it_returns_serialized_report_comment(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
        comment = self.random_string()
        report_comment = ReportComment(
            report_id=report.id,
            user_id=user_1_admin.id,
            comment=comment,
        )
        db.session.add(report_comment)
        db.session.commit()

        serialized_comment = report_comment.serialize(user_1_admin)

        assert serialized_comment['created_at'] == report_comment.created_at
        assert serialized_comment['comment'] == report_comment.comment
        assert serialized_comment['report_id'] == report.id
        assert serialized_comment['user'] == user_1_admin.serialize(
            user_1_admin
        )

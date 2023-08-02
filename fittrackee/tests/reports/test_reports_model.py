from datetime import datetime

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.reports.exceptions import InvalidReportException
from fittrackee.reports.models import Report
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
                reported_by=user_1,
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


class TestReportSerializer(CommentMixin, RandomMixin):
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

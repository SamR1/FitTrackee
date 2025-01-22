from datetime import datetime, timezone
from typing import Dict

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.reports.exceptions import (
    InvalidReportActionAppealException,
    InvalidReportActionAppealUserException,
    InvalidReportActionException,
    ReportActionAppealForbiddenException,
    ReportActionForbiddenException,
)
from fittrackee.reports.models import (
    ALL_USER_ACTION_TYPES,
    COMMENT_ACTION_TYPES,
    REPORT_ACTION_TYPES,
    WORKOUT_ACTION_TYPES,
    ReportAction,
    ReportActionAppeal,
)
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..comments.mixins import CommentMixin
from ..mixins import ReportMixin


class ReportActionTestCase(ReportMixin):
    pass


class TestReportActionModel(ReportActionTestCase):
    def test_it_raises_error_when_action_type_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        with pytest.raises(InvalidReportActionException):
            ReportAction(
                moderator_id=user_1_admin.id,
                action_type=self.random_string(),
                report_id=self.create_user_report(user_1_admin, user_2).id,
                user_id=user_1_admin.id,
            )


class TestReportActionForReportModel(ReportActionTestCase):
    @pytest.mark.parametrize("input_action_type", REPORT_ACTION_TYPES)
    def test_it_creates_report_report_action_for_a_given_type(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_action_type: str,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        created_at = datetime.now(timezone.utc)

        report_action = ReportAction(
            action_type=input_action_type,
            moderator_id=user_1_admin.id,
            created_at=created_at,
            report_id=report.id,
        )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.action_type == input_action_type
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.comment_id is None
        assert report_action.created_at == created_at
        assert report_action.reason is None
        assert report_action.report_id == report.id
        assert report_action.user_id is None
        assert report_action.workout is None

    def test_it_creates_report_action_without_given_date(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        now = datetime.now(timezone.utc)
        action_type = "report_resolution"

        with travel(now, tick=False):
            report_action = ReportAction(
                action_type=action_type,
                moderator_id=user_1_admin.id,
                report_id=report.id,
            )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.action_type == action_type
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.comment_id is None
        assert report_action.created_at == now
        assert report_action.reason is None
        assert report_action.report_id == report.id
        assert report_action.user_id is None
        assert report_action.workout is None

    def test_it_does_not_store_user_id_when_action_is_for_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        now = datetime.now(timezone.utc)
        report = self.create_report(reporter=user_2, reported_object=user_3)
        action_type = "report_resolution"

        with travel(now, tick=False):
            report_action = ReportAction(
                action_type=action_type,
                moderator_id=user_1_admin.id,
                report_id=report.id,
                user_id=user_2.id,
            )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.action_type == action_type
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.comment_id is None
        assert report_action.created_at == now
        assert report_action.reason is None
        assert report_action.report_id == report.id
        assert report_action.user_id is None
        assert report_action.workout is None

    def test_it_creates_report_action_with_given_reason(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        reason = self.random_short_id()

        report_action = ReportAction(
            action_type="report_resolution",
            moderator_id=user_1_admin.id,
            report_id=report.id,
            reason=reason,
        )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.reason == reason


class TestReportActionForUserModel(ReportActionTestCase):
    @pytest.mark.parametrize("input_action_type", ALL_USER_ACTION_TYPES)
    def test_it_raises_error_when_no_user_given_for_user_report_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        with pytest.raises(InvalidReportActionException):
            ReportAction(
                action_type=input_action_type,
                moderator_id=user_1_admin.id,
                created_at=datetime.now(timezone.utc),
                report_id=self.create_report(
                    reporter=user_1_admin, reported_object=user_2
                ).id,
            )

    def test_it_creates_user_report_action(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        created_at = datetime.now(timezone.utc)

        report_action = ReportAction(
            action_type="user_suspension",
            moderator_id=user_1_admin.id,
            created_at=created_at,
            report_id=report.id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.action_type == "user_suspension"
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.comment_id is None
        assert report_action.created_at == created_at
        assert report_action.reason is None
        assert report_action.report_id == report.id
        assert report_action.user_id == user_2.id
        assert report_action.workout is None

    def test_it_sets_none_for_moderator_id_when_admin_user_is_deleted(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=user_2
        ).id
        action_type = "user_suspension"
        now = datetime.now(timezone.utc)
        report_action = ReportAction(
            action_type=action_type,
            moderator_id=user_1_admin.id,
            created_at=now,
            report_id=report_id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert report_action.action_type == action_type
        assert report_action.moderator_id is None
        assert report_action.comment_id is None
        assert report_action.created_at == now
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_2.id
        assert report_action.workout is None

    def test_it_deletes_report_action_when_user_is_deleted(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_action = ReportAction(
            action_type="user_suspension",
            moderator_id=user_1_admin.id,
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=user_2
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        db.session.delete(user_2)
        db.session.commit()

        assert ReportAction.query.first() is None


class TestReportActionForWorkoutModel(ReportActionTestCase):
    @pytest.mark.parametrize("input_action_type", WORKOUT_ACTION_TYPES)
    def test_it_raises_error_when_no_workout_id_given_for_workout_report_action(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        with pytest.raises(InvalidReportActionException):
            ReportAction(
                action_type=input_action_type,
                moderator_id=user_1_admin.id,
                created_at=datetime.now(timezone.utc),
                report_id=self.create_report(
                    reporter=user_1_admin,
                    reported_object=workout_cycling_user_2,
                ).id,
                user_id=user_2.id,
            )

    @pytest.mark.parametrize("input_action_type", WORKOUT_ACTION_TYPES)
    def test_it_raises_error_when_no_user_id_given_for_workout_report_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        with pytest.raises(InvalidReportActionException):
            ReportAction(
                action_type=input_action_type,
                moderator_id=user_1_admin.id,
                created_at=datetime.now(timezone.utc),
                report_id=self.create_report(
                    reporter=user_1_admin,
                    reported_object=workout_cycling_user_2,
                ).id,
                workout_id=workout_cycling_user_2.id,
            )

    def test_it_creates_workout_report_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_id = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        ).id
        created_at = datetime.now(timezone.utc)

        report_action = ReportAction(
            action_type="workout_suspension",
            moderator_id=user_1_admin.id,
            created_at=created_at,
            report_id=report_id,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.action_type == "workout_suspension"
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.comment_id is None
        assert report_action.created_at == created_at
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_2.id
        assert report_action.workout_id == workout_cycling_user_2.id

    def test_it_sets_none_for_moderator_id_when_admin_user_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=workout_cycling_user_2
        ).id
        created_at = datetime.now(timezone.utc)
        report_action = ReportAction(
            action_type="workout_suspension",
            moderator_id=user_1_admin.id,
            created_at=created_at,
            report_id=report_id,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert report_action.action_type == "workout_suspension"
        assert report_action.moderator_id is None
        assert report_action.comment_id is None
        assert report_action.created_at == created_at
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_2.id
        assert report_action.workout_id == workout_cycling_user_2.id

    def test_it_sets_none_for_workout_id_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=workout_cycling_user_2
        ).id
        created_at = datetime.now(timezone.utc)
        report_action = ReportAction(
            action_type="workout_suspension",
            moderator_id=user_1_admin.id,
            created_at=created_at,
            report_id=report_id,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        db.session.delete(workout_cycling_user_2)
        db.session.commit()

        assert report_action.action_type == "workout_suspension"
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.comment_id is None
        assert report_action.created_at == created_at
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_2.id
        assert report_action.workout_id is None


class TestReportActionForCommentsModel(CommentMixin, ReportActionTestCase):
    @pytest.mark.parametrize("input_action_type", COMMENT_ACTION_TYPES)
    def test_it_raises_error_when_no_comment_id_given_for_comment_report_action(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_action_type: str,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        report_id = self.create_report(
            reporter=user_2, reported_object=comment
        ).id
        with pytest.raises(InvalidReportActionException):
            ReportAction(
                action_type=input_action_type,
                moderator_id=user_1_admin.id,
                created_at=datetime.now(timezone.utc),
                report_id=report_id,
                user_id=user_2.id,
            )

    @pytest.mark.parametrize("input_action_type", COMMENT_ACTION_TYPES)
    def test_it_raises_error_when_no_user_id_given_for_comment_report_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        with pytest.raises(InvalidReportActionException):
            ReportAction(
                action_type=input_action_type,
                moderator_id=user_1_admin.id,
                comment_id=comment.id,
                report_id=self.create_report(
                    reporter=user_2, reported_object=comment
                ).id,
                created_at=datetime.now(timezone.utc),
            )

    def test_it_creates_comment_report_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        report_id = self.create_report(
            reporter=user_2, reported_object=comment
        ).id
        created_at = datetime.now(timezone.utc)

        report_action = ReportAction(
            action_type="comment_suspension",
            moderator_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            report_id=report_id,
            user_id=user_3.id,
        )
        db.session.add(report_action)
        db.session.commit()

        assert report_action.action_type == "comment_suspension"
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.created_at == created_at
        assert report_action.comment_id == comment.id
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_3.id
        assert report_action.workout_id is None

    def test_it_sets_none_for_moderator_id_when_admin_user_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        report_id = self.create_report(
            reporter=user_2, reported_object=comment
        ).id
        created_at = datetime.now(timezone.utc)
        report_action = ReportAction(
            action_type="comment_suspension",
            moderator_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            report_id=report_id,
            user_id=user_3.id,
        )
        db.session.add(report_action)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert report_action.action_type == "comment_suspension"
        assert report_action.moderator_id is None
        assert report_action.comment_id == comment.id
        assert report_action.created_at == created_at
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_3.id
        assert report_action.workout_id is None

    def test_it_sets_none_for_comment_id_when_comment_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        report_id = self.create_report(
            reporter=user_2, reported_object=comment
        ).id
        created_at = datetime.now(timezone.utc)
        report_action = ReportAction(
            action_type="comment_suspension",
            moderator_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            report_id=report_id,
            user_id=user_3.id,
        )
        db.session.add(report_action)
        db.session.commit()

        db.session.delete(comment)
        db.session.commit()

        assert report_action.action_type == "comment_suspension"
        assert report_action.moderator_id == user_1_admin.id
        assert report_action.created_at == created_at
        assert report_action.comment_id is None
        assert report_action.reason is None
        assert report_action.report_id == report_id
        assert report_action.user_id == user_3.id
        assert report_action.workout_id is None


class TestReportActionSerializer(CommentMixin, ReportActionTestCase):
    def test_it_returns_minimal_serialized_report_action(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=user_2
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(user_1_admin, full=False)

        assert serialized_action == {
            'moderator': user_1_admin.serialize(current_user=user_1_admin),
            'appeal': None,
            'action_type': report_action.action_type,
            'created_at': report_action.created_at,
            'id': report_action.short_id,
            'reason': None,
            'report_id': report_action.id,
            'user': user_2.serialize(current_user=user_1_admin),
        }

    @pytest.mark.parametrize('input_full_argument', [{}, {"full": True}])
    def test_it_returns_full_serialized_user_report_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_full_argument: Dict,
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=user_2
        ).id
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=report_id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(
            user_1_admin, **input_full_argument
        )

        assert serialized_action['action_type'] == report_action.action_type
        assert serialized_action['moderator'] == user_1_admin.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['comment'] is None
        assert serialized_action['created_at'] == report_action.created_at
        assert serialized_action['id'] == report_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] == report_id
        assert serialized_action['user'] == user_2.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['workout'] is None

    def test_it_returns_serialized_report_action_with_appeal_for_admin(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=user_2
        ).id
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=report_id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.flush()
        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.commit()

        serialized_action = report_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == report_action.action_type
        assert serialized_action['moderator'] == user_1_admin.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['appeal'] == appeal.serialize(user_1_admin)
        assert serialized_action['created_at'] == report_action.created_at
        assert serialized_action['comment'] is None
        assert serialized_action['id'] == report_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] == report_id
        assert serialized_action['user'] == user_2.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['workout'] is None

    def test_it_serialized_user_action_for_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=user_2
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(user_2)

        assert serialized_action == {
            "action_type": report_action.action_type,
            "appeal": None,
            "created_at": report_action.created_at,
            "reason": report_action.reason,
            "id": report_action.short_id,
        }

    def test_it_serialized_action_with_appeal_for_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=user_2
            ).id,
            user_id=user_2.id,
        )
        db.session.add(report_action)
        db.session.flush()
        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.commit()

        serialized_action = report_action.serialize(user_2)

        assert serialized_action == {
            "action_type": report_action.action_type,
            "appeal": appeal.serialize(user_2),
            "created_at": report_action.created_at,
            "id": report_action.short_id,
            "reason": report_action.reason,
        }

    def test_it_raises_error_when_user_is_not_action_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="user_suspension",
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=user_2
            ).id,
            user_id=user_2.id,
        )

        with pytest.raises(ReportActionForbiddenException):
            report_action.serialize(user_3)

    @pytest.mark.parametrize('input_action_type', REPORT_ACTION_TYPES)
    def test_it_raises_error_when_user_has_no_admin_rights_and_action_is_report_related(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type=input_action_type,
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=user_2
            ).id,
        )

        with pytest.raises(ReportActionForbiddenException):
            report_action.serialize(user_2)

    def test_it_returns_serialized_workout_report_action_for_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="workout_suspension",
            user_id=user_2.id,
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=workout_cycling_user_2
            ).id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(user_2)

        assert serialized_action == {
            "action_type": report_action.action_type,
            "appeal": None,
            "created_at": report_action.created_at,
            "id": report_action.short_id,
            "reason": report_action.reason,
            "workout": workout_cycling_user_2.serialize(user=user_2),
        }

    def test_it_returns_serialized_workout_report_action_for_user_when_workout_is_deleted(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="workout_suspension",
            user_id=user_2.id,
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=workout_cycling_user_2
            ).id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()
        db.session.delete(workout_cycling_user_2)
        db.session.commit()

        serialized_action = report_action.serialize(user_2)

        assert serialized_action == {
            "action_type": report_action.action_type,
            "appeal": None,
            "created_at": report_action.created_at,
            "id": report_action.short_id,
            "reason": report_action.reason,
            "workout": None,
        }

    def test_it_returns_serialized_workout_report_action_for_admin(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=workout_cycling_user_2
        ).id
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="workout_suspension",
            report_id=report_id,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == report_action.action_type
        assert serialized_action['moderator'] == user_1_admin.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['comment'] is None
        assert serialized_action['created_at'] == report_action.created_at
        assert serialized_action['id'] == report_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] == report_id
        assert serialized_action['user'] == user_2.serialize(
            current_user=user_1_admin
        )
        assert serialized_action[
            'workout'
        ] == workout_cycling_user_2.serialize(
            user=user_1_admin, for_report=True
        )

    def test_it_returns_serialized_comment_report_action_for_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="comment_suspension",
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=comment
            ).id,
            user_id=user_3.id,
            comment_id=comment.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(user_3)

        assert serialized_action == {
            "action_type": report_action.action_type,
            "appeal": None,
            "comment": comment.serialize(user=user_3),
            "created_at": report_action.created_at,
            "id": report_action.short_id,
            "reason": report_action.reason,
        }

    def test_it_returns_serialized_comment_report_action_for_user_when_comment_is_deleted(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="comment_suspension",
            report_id=self.create_report(
                reporter=user_1_admin, reported_object=comment
            ).id,
            user_id=user_3.id,
            comment_id=comment.id,
        )
        db.session.add(report_action)
        db.session.commit()
        db.session.delete(comment)
        db.session.commit()

        serialized_action = report_action.serialize(user_3)

        assert serialized_action == {
            "action_type": report_action.action_type,
            "appeal": None,
            "comment": None,
            "created_at": report_action.created_at,
            "id": report_action.short_id,
            "reason": report_action.reason,
        }

    def test_it_returns_serialized_comment_report_action_for_admin(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        report_id = self.create_report(
            reporter=user_1_admin, reported_object=comment
        ).id
        report_action = ReportAction(
            moderator_id=user_1_admin.id,
            action_type="comment_suspension",
            comment_id=comment.id,
            report_id=report_id,
            user_id=user_3.id,
        )
        db.session.add(report_action)
        db.session.commit()

        serialized_action = report_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == report_action.action_type
        assert serialized_action['moderator'] == user_1_admin.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['comment'] == comment.serialize(
            user_1_admin, for_report=True
        )
        assert serialized_action['created_at'] == report_action.created_at
        assert serialized_action['id'] == report_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] == report_id
        assert serialized_action['user'] == user_3.serialize(
            current_user=user_1_admin
        )
        assert serialized_action['workout'] is None


class TestReportActionAppealModel(CommentMixin, ReportActionTestCase):
    def test_it_raises_error_when_user_is_not_report_action_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report_action = self.create_report_user_action(user_1_admin, user_2)

        with pytest.raises(InvalidReportActionAppealUserException):
            ReportActionAppeal(
                action_id=report_action.id,
                user_id=user_3.id,
                text=self.random_string(),
            )

    @pytest.mark.parametrize(
        'input_action_type', ['user_unsuspension', 'user_warning_lifting']
    )
    def test_it_raises_error_when_user_action_is_invalid(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        report_action = self.create_report_user_action(
            user_1_admin, user_2, action_type=input_action_type
        )

        with pytest.raises(InvalidReportActionAppealException):
            ReportActionAppeal(
                action_id=report_action.id,
                user_id=user_2.id,
                text=self.random_string(),
            )

    def test_it_creates_appeal_for_user_suspension_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        appeal_text = self.random_string()
        report_action = self.create_report_user_action(user_1_admin, user_2)
        created_at = datetime.now(timezone.utc)

        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=appeal_text,
            created_at=created_at,
        )

        assert appeal.action_id == report_action.id
        assert appeal.moderator_id is None
        assert appeal.approved is None
        assert appeal.created_at == created_at
        assert appeal.reason is None
        assert appeal.updated_at is None
        assert appeal.user_id == user_2.id

    def test_it_creates_appeal_for_user_warning_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        appeal_text = self.random_string()
        report_action = self.create_report_user_action(
            user_1_admin, user_2, action_type="user_warning"
        )
        created_at = datetime.now(timezone.utc)

        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=appeal_text,
            created_at=created_at,
        )

        assert appeal.action_id == report_action.id
        assert appeal.moderator_id is None
        assert appeal.approved is None
        assert appeal.created_at == created_at
        assert appeal.reason is None
        assert appeal.updated_at is None
        assert appeal.user_id == user_2.id

    def test_it_raises_error_when_workout_action_is_invalid(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        report_action = self.create_report_workout_action(
            user_1_admin,
            user_2,
            workout_cycling_user_2,
            action_type="workout_unsuspension",
        )
        db.session.add(report_action)
        db.session.flush()

        with pytest.raises(InvalidReportActionAppealException):
            ReportActionAppeal(
                action_id=report_action.id,
                user_id=user_2.id,
                text=self.random_string(),
            )

    def test_it_creates_appeal_for_workout_suspension_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report_action = self.create_report_workout_action(
            user_1_admin, user_2, workout_cycling_user_2
        )
        db.session.add(report_action)
        appeal_text = self.random_string()
        created_at = datetime.now(timezone.utc)
        db.session.flush()

        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=appeal_text,
            created_at=created_at,
        )

        assert appeal.action_id == report_action.id
        assert appeal.moderator_id is None
        assert appeal.approved is None
        assert appeal.created_at == created_at
        assert appeal.reason is None
        assert appeal.updated_at is None
        assert appeal.user_id == user_2.id

    def test_it_raises_error_when_comment_action_is_invalid(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        report_action = self.create_report_comment_action(
            user_1_admin, user_2, comment, action_type="comment_unsuspension"
        )
        db.session.add(report_action)
        db.session.flush()

        with pytest.raises(InvalidReportActionAppealException):
            ReportActionAppeal(
                action_id=report_action.id,
                user_id=user_2.id,
                text=self.random_string(),
            )

    def test_it_creates_appeal_for_comment_suspension_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.FOLLOWERS,
        )
        report_action = self.create_report_comment_action(
            user_1_admin, user_2, comment
        )
        db.session.add(report_action)
        appeal_text = self.random_string()
        created_at = datetime.now(timezone.utc)
        db.session.flush()

        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=appeal_text,
            created_at=created_at,
        )

        assert appeal.action_id == report_action.id
        assert appeal.moderator_id is None
        assert appeal.approved is None
        assert appeal.created_at == created_at
        assert appeal.reason is None
        assert appeal.updated_at is None
        assert appeal.user_id == user_2.id

    def test_it_creates_appeal_for_a_given_action_without_creation_date(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        appeal_text = self.random_string()
        report_action = self.create_report_user_action(user_1_admin, user_2)
        now = datetime.now(timezone.utc)

        with travel(now, tick=False):
            appeal = ReportActionAppeal(
                action_id=report_action.id, user_id=user_2.id, text=appeal_text
            )

        assert appeal.action_id == report_action.id
        assert appeal.moderator_id is None
        assert appeal.approved is None
        assert appeal.created_at == now
        assert appeal.reason is None
        assert appeal.updated_at is None
        assert appeal.user_id == user_2.id

    def test_it_deletes_appeal_on_user_deletion(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        appeal_text = self.random_string()
        report_action = self.create_report_user_action(user_1_admin, user_2)
        appeal = ReportActionAppeal(
            action_id=report_action.id, user_id=user_2.id, text=appeal_text
        )
        db.session.add(appeal)
        db.session.commit()

        db.session.delete(user_2)
        db.session.commit()

        assert ReportActionAppeal.query.first() is None

    def test_it_does_not_delete_appeal_on_admin_user_deletion(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        appeal_text = self.random_string()
        report_action = self.create_report_user_action(user_1_admin, user_2)
        appeal = ReportActionAppeal(
            action_id=report_action.id, user_id=user_2.id, text=appeal_text
        )
        db.session.add(appeal)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert (
            ReportActionAppeal.query.filter_by(
                action_id=report_action.id
            ).first()
            is not None
        )


class TestReportActionAppealSerializer(ReportActionTestCase):
    def test_it_returns_serialized_appeal_for_admin(
        self, app: Flask, user_1_admin: User, user_2_admin: User, user_3: User
    ) -> None:
        report_action = self.create_report_user_action(user_1_admin, user_3)
        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_3.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.flush()

        serialized_appeal = appeal.serialize(user_2_admin)

        assert serialized_appeal["moderator"] is None
        assert serialized_appeal["approved"] is None
        assert serialized_appeal["created_at"] == appeal.created_at
        assert serialized_appeal["id"] == appeal.short_id
        assert serialized_appeal["text"] == appeal.text
        assert serialized_appeal["reason"] is None
        assert serialized_appeal["user"] == user_3.serialize(
            current_user=user_2_admin
        )
        assert serialized_appeal["updated_at"] is None

    def test_it_returns_serialized_appeal_for_appeal_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        report_action = self.create_report_user_action(user_1_admin, user_2)
        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.flush()

        serialized_appeal = appeal.serialize(user_2)

        assert serialized_appeal == {
            "approved": None,
            "created_at": appeal.created_at,
            "id": appeal.short_id,
            "reason": appeal.reason,
            "text": appeal.text,
            "updated_at": None,
        }

    def test_it_raises_error_when_user_is_not_appeal_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report_action = self.create_report_user_action(user_1_admin, user_2)
        appeal = ReportActionAppeal(
            action_id=report_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )

        with pytest.raises(ReportActionAppealForbiddenException):
            appeal.serialize(user_3)

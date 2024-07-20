from datetime import datetime

import pytest
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.administration.exceptions import (
    AdminActionAppealForbiddenException,
    AdminActionForbiddenException,
    InvalidAdminActionAppealException,
    InvalidAdminActionAppealUserException,
    InvalidAdminActionException,
)
from fittrackee.administration.models import (
    COMMENT_ACTION_TYPES,
    REPORT_ACTION_TYPES,
    USER_ACTION_TYPES,
    WORKOUT_ACTION_TYPES,
    AdminAction,
    AdminActionAppeal,
)
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..comments.utils import CommentMixin
from ..mixins import UserModerationMixin


class AdminActionTestCase(UserModerationMixin): ...


class TestAdminActionModel(AdminActionTestCase):
    def test_it_raises_error_when_action_type_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                admin_user_id=user_1_admin.id,
                action_type=self.random_string(),
                user_id=user_1_admin.id,
            )


class TestAdminActionForReportModel(AdminActionTestCase):
    @pytest.mark.parametrize("input_action_type", REPORT_ACTION_TYPES)
    def test_it_raises_error_when_no_report_given_for_report_admin_action(
        self, app: Flask, user_1_admin: User, input_action_type: str
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                created_at=datetime.now(),
                report_id=None,
            )

    @pytest.mark.parametrize("input_action_type", REPORT_ACTION_TYPES)
    def test_it_creates_report_admin_action_for_a_given_type(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_action_type: str,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type=input_action_type,
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            report_id=report.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == input_action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id is None
        assert admin_action.workout is None

    def test_it_creates_report_action_without_given_date(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        now = datetime.utcnow()
        action_type = "report_resolution"

        with travel(now, tick=False):
            admin_action = AdminAction(
                action_type=action_type,
                admin_user_id=user_1_admin.id,
                report_id=report.id,
            )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == now
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id is None
        assert admin_action.workout is None

    def test_it_does_not_store_user_id_when_action_is_for_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        now = datetime.utcnow()
        report = self.create_report(reporter=user_2, reported_object=user_3)
        action_type = "report_resolution"

        with travel(now, tick=False):
            admin_action = AdminAction(
                action_type=action_type,
                admin_user_id=user_1_admin.id,
                report_id=report.id,
                user_id=user_2.id,
            )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == now
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id is None
        assert admin_action.workout is None

    def test_it_creates_report_action_with_given_reason(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        reason = self.random_short_id()

        admin_action = AdminAction(
            action_type="report_resolution",
            admin_user_id=user_1_admin.id,
            report_id=report.id,
            reason=reason,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.reason == reason


class TestAdminActionForUserModel(AdminActionTestCase):
    @pytest.mark.parametrize("input_action_type", USER_ACTION_TYPES)
    def test_it_raises_error_when_no_user_given_for_user_admin_action(
        self, app: Flask, user_1_admin: User, input_action_type: str
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                created_at=datetime.now(),
            )

    @pytest.mark.parametrize("input_action_type", USER_ACTION_TYPES)
    def test_it_creates_user_admin_action_without_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type=input_action_type,
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == input_action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id
        assert admin_action.workout is None

    def test_it_creates_user_admin_action_with_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type="user_suspension",
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            report_id=report.id,
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == "user_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_2.id
        assert admin_action.workout is None

    def test_it_sets_none_for_admin_user_id_when_admin_user_is_deleted(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        action_type = "user_suspension"
        now = datetime.utcnow()
        admin_action = AdminAction(
            action_type=action_type,
            admin_user_id=user_1_admin.id,
            created_at=now,
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert admin_action.action_type == action_type
        assert admin_action.admin_user_id is None
        assert admin_action.comment_id is None
        assert admin_action.created_at == now
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id
        assert admin_action.workout is None

    def test_it_deletes_admin_action_when_user_is_deleted(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            action_type="user_suspension",
            admin_user_id=user_1_admin.id,
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        db.session.delete(user_2)
        db.session.commit()

        assert AdminAction.query.first() is None


class TestAdminActionForWorkoutModel(AdminActionTestCase):
    @pytest.mark.parametrize("input_action_type", WORKOUT_ACTION_TYPES)
    def test_it_raises_error_when_no_workout_id_given_for_workout_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                created_at=datetime.now(),
                user_id=user_2.id,
            )

    @pytest.mark.parametrize("input_action_type", WORKOUT_ACTION_TYPES)
    def test_it_raises_error_when_no_user_id_given_for_workout_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                created_at=datetime.now(),
                workout_id=workout_cycling_user_2.id,
            )

    @pytest.mark.parametrize("input_action_type", WORKOUT_ACTION_TYPES)
    def test_it_creates_workout_admin_action_without_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type=input_action_type,
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == input_action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id == workout_cycling_user_2.id

    def test_it_creates_workout_admin_action_with_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        report = self.create_report(
            reporter=user_3, reported_object=workout_cycling_user_2
        )
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type="workout_suspension",
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            report_id=report.id,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == "workout_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id == workout_cycling_user_2.id

    def test_it_sets_none_for_admin_user_id_when_admin_user_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        created_at = datetime.now()
        admin_action = AdminAction(
            action_type="workout_suspension",
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert admin_action.action_type == "workout_suspension"
        assert admin_action.admin_user_id is None
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id == workout_cycling_user_2.id

    def test_it_sets_none_for_workout_id_when_workout_is_deleted(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        created_at = datetime.now()
        admin_action = AdminAction(
            action_type="workout_suspension",
            admin_user_id=user_1_admin.id,
            created_at=created_at,
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        db.session.delete(workout_cycling_user_2)
        db.session.commit()

        assert admin_action.action_type == "workout_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.comment_id is None
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id
        assert admin_action.workout_id is None


class TestAdminActionForCommentsModel(CommentMixin, AdminActionTestCase):
    @pytest.mark.parametrize("input_action_type", COMMENT_ACTION_TYPES)
    def test_it_raises_error_when_no_comment_id_given_for_comment_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                created_at=datetime.now(),
                user_id=user_2.id,
            )

    @pytest.mark.parametrize("input_action_type", COMMENT_ACTION_TYPES)
    def test_it_raises_error_when_no_user_id_given_for_comment_admin_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                comment_id=comment.id,
                created_at=datetime.now(),
            )

    @pytest.mark.parametrize("input_action_type", COMMENT_ACTION_TYPES)
    def test_it_creates_comment_admin_action_without_report(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_action_type: str,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type=input_action_type,
            admin_user_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            user_id=user_3.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == input_action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == created_at
        assert admin_action.comment_id == comment.id
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_creates_comment_admin_action_with_report(
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
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        report = self.create_report(reporter=user_2, reported_object=comment)
        created_at = datetime.now()

        admin_action = AdminAction(
            action_type="comment_suspension",
            admin_user_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            report_id=report.id,
            user_id=user_3.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == "comment_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == created_at
        assert admin_action.comment_id == comment.id
        assert admin_action.reason is None
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_sets_none_for_admin_user_id_when_admin_user_is_deleted(
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
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        created_at = datetime.now()
        admin_action = AdminAction(
            action_type="comment_suspension",
            admin_user_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            user_id=user_3.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert admin_action.action_type == "comment_suspension"
        assert admin_action.admin_user_id is None
        assert admin_action.comment_id == comment.id
        assert admin_action.created_at == created_at
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None

    def test_it_sets_none_for_comment_id_when_comment_is_deleted(
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
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        created_at = datetime.now()
        admin_action = AdminAction(
            action_type="comment_suspension",
            admin_user_id=user_1_admin.id,
            comment_id=comment.id,
            created_at=created_at,
            user_id=user_3.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        db.session.delete(comment)
        db.session.commit()

        assert admin_action.action_type == "comment_suspension"
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == created_at
        assert admin_action.comment_id is None
        assert admin_action.reason is None
        assert admin_action.report_id is None
        assert admin_action.user_id == user_3.id
        assert admin_action.workout_id is None


class TestAdminActionSerializer(CommentMixin, AdminActionTestCase):
    def test_it_returns_minimal_serialized_admin_action(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_1_admin, full=False)

        assert serialized_action == {
            'admin_user': user_1_admin.serialize(user_1_admin, light=True),
            'appeal': None,
            'action_type': admin_action.action_type,
            'created_at': admin_action.created_at,
            'id': admin_action.short_id,
            'reason': None,
            'user': user_2.serialize(user_1_admin, light=True),
        }

    def test_it_returns_serialized_user_admin_action_without_report(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == admin_action.action_type
        assert serialized_action['admin_user'] == user_1_admin.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['comment'] is None
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] is None
        assert serialized_action['user'] == user_2.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['workout'] is None

    def test_it_returns_serialized_admin_action_with_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_object=user_3)
        admin_action = AdminAction(
            action_type="report_resolution",
            admin_user_id=user_1_admin.id,
            report_id=report.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == admin_action.action_type
        assert serialized_action['admin_user'] == user_1_admin.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['comment'] is None
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] == report.id
        assert serialized_action['user'] is None
        assert serialized_action['workout'] is None

    def test_it_returns_serialized_admin_action_with_appeal(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.flush()
        appeal = AdminActionAppeal(
            action_id=admin_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.commit()

        serialized_action = admin_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == admin_action.action_type
        assert serialized_action['admin_user'] == user_1_admin.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['appeal'] == appeal.serialize(user_1_admin)
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['comment'] is None
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] is None
        assert serialized_action['user'] == user_2.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['workout'] is None

    def test_it_serialized_user_action_for_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_2)

        assert serialized_action == {
            "action_type": admin_action.action_type,
            "appeal": None,
            "comment": None,
            "created_at": admin_action.created_at,
            "reason": admin_action.reason,
            "id": admin_action.short_id,
            "workout": None,
        }

    def test_it_serialized_action_with_appeal_for_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.flush()
        appeal = AdminActionAppeal(
            action_id=admin_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.commit()

        serialized_action = admin_action.serialize(user_2)

        assert serialized_action == {
            "action_type": admin_action.action_type,
            "appeal": appeal.serialize(user_2),
            "comment": None,
            "created_at": admin_action.created_at,
            "id": admin_action.short_id,
            "reason": admin_action.reason,
            "workout": None,
        }

    def test_it_raises_error_when_user_is_not_action_user(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )

        with pytest.raises(AdminActionForbiddenException):
            admin_action.serialize(user_3)

    @pytest.mark.parametrize('input_action_type', REPORT_ACTION_TYPES)
    def test_it_raises_error_when_user_has_no_admin_rights_and_action_is_report_related(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_action_type: str,
    ) -> None:
        report = self.create_report(
            reporter=user_1_admin, reported_object=user_2
        )
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type=input_action_type,
            report_id=report.id,
        )

        with pytest.raises(AdminActionForbiddenException):
            admin_action.serialize(user_2)

    def test_it_returns_serialized_workout_admin_action_for_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="workout_suspension",
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_2)

        assert serialized_action == {
            "action_type": admin_action.action_type,
            "appeal": None,
            "comment": None,
            "created_at": admin_action.created_at,
            "id": admin_action.short_id,
            "reason": admin_action.reason,
            "workout": workout_cycling_user_2.serialize(user_2),
        }

    def test_it_returns_serialized_workout_admin_action_for_admin(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="workout_suspension",
            user_id=user_2.id,
            workout_id=workout_cycling_user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == admin_action.action_type
        assert serialized_action['admin_user'] == user_1_admin.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['comment'] is None
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] is None
        assert serialized_action['user'] == user_2.serialize(
            user_1_admin, light=True
        )
        assert serialized_action[
            'workout'
        ] == workout_cycling_user_2.serialize(user_1_admin, for_report=True)

    def test_it_returns_serialized_comment_admin_action_for_user(
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
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="comment_suspension",
            user_id=user_3.id,
            comment_id=comment.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_3)

        assert serialized_action == {
            "action_type": admin_action.action_type,
            "appeal": None,
            "comment": comment.serialize(user=user_3),
            "created_at": admin_action.created_at,
            "id": admin_action.short_id,
            "reason": admin_action.reason,
            "workout": None,
        }

    def test_it_returns_serialized_comment_admin_action_for_admin(
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
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="comment_suspension",
            comment_id=comment.id,
            user_id=user_3.id,
        )
        db.session.add(admin_action)
        db.session.commit()

        serialized_action = admin_action.serialize(user_1_admin)

        assert serialized_action['action_type'] == admin_action.action_type
        assert serialized_action['admin_user'] == user_1_admin.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['comment'] == comment.serialize(
            user_1_admin, for_report=True
        )
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['reason'] is None
        assert serialized_action['report_id'] is None
        assert serialized_action['user'] == user_3.serialize(
            user_1_admin, light=True
        )
        assert serialized_action['workout'] is None


class TestAdminActionAppealModel(CommentMixin, AdminActionTestCase):
    def test_it_raises_error_when_user_is_not_admin_action_user(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        admin_action = self.create_admin_action(user_1_admin, user_2)

        with pytest.raises(InvalidAdminActionAppealUserException):
            AdminActionAppeal(
                action_id=admin_action.id,
                user_id=user_3.id,
                text=self.random_string(),
            )

    def test_it_raises_error_when_action_is_invalid(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        admin_action = self.create_admin_action(
            user_1_admin, user_2, action_type="user_unsuspension"
        )

        with pytest.raises(InvalidAdminActionAppealException):
            AdminActionAppeal(
                action_id=admin_action.id,
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
        admin_action = self.create_admin_action(user_1_admin, user_2)
        created_at = datetime.now()

        appeal = AdminActionAppeal(
            action_id=admin_action.id,
            user_id=user_2.id,
            text=appeal_text,
            created_at=created_at,
        )

        assert appeal.action_id == admin_action.id
        assert appeal.admin_user_id is None
        assert appeal.approved is None
        assert appeal.created_at == created_at
        assert appeal.reason is None
        assert appeal.updated_at is None
        assert appeal.user_id == user_2.id

    def test_it_creates_appeal_for_comment_suspension_action(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        admin_action = AdminAction(
            action_type="comment_suspension",
            admin_user_id=user_1_admin.id,
            comment_id=comment.id,
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        appeal_text = self.random_string()
        created_at = datetime.now()
        db.session.flush()

        appeal = AdminActionAppeal(
            action_id=admin_action.id,
            user_id=user_2.id,
            text=appeal_text,
            created_at=created_at,
        )

        assert appeal.action_id == admin_action.id
        assert appeal.admin_user_id is None
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
        admin_action = self.create_admin_action(user_1_admin, user_2)
        now = datetime.now()

        with travel(now, tick=False):
            appeal = AdminActionAppeal(
                action_id=admin_action.id, user_id=user_2.id, text=appeal_text
            )

        assert appeal.action_id == admin_action.id
        assert appeal.admin_user_id is None
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
        admin_action = self.create_admin_action(user_1_admin, user_2)
        appeal = AdminActionAppeal(
            action_id=admin_action.id, user_id=user_2.id, text=appeal_text
        )
        db.session.add(appeal)
        db.session.commit()

        db.session.delete(user_2)
        db.session.commit()

        assert AdminActionAppeal.query.first() is None

    def test_it_does_not_delete_appeal_on_admin_user_deletion(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        appeal_text = self.random_string()
        admin_action = self.create_admin_action(user_1_admin, user_2)
        appeal = AdminActionAppeal(
            action_id=admin_action.id, user_id=user_2.id, text=appeal_text
        )
        db.session.add(appeal)
        db.session.commit()

        db.session.delete(user_1_admin)
        db.session.commit()

        assert (
            AdminActionAppeal.query.filter_by(
                action_id=admin_action.id
            ).first()
            is not None
        )


class TestAdminActionAppealSerializer(AdminActionTestCase):
    def test_it_returns_serialized_appeal_for_admin(
        self, app: Flask, user_1_admin: User, user_2_admin: User, user_3: User
    ) -> None:
        admin_action = self.create_admin_action(user_1_admin, user_3)
        appeal = AdminActionAppeal(
            action_id=admin_action.id,
            user_id=user_3.id,
            text=self.random_string(),
        )
        db.session.add(appeal)
        db.session.flush()

        serialized_appeal = appeal.serialize(user_2_admin)

        assert serialized_appeal["admin_user"] is None
        assert serialized_appeal["approved"] is None
        assert serialized_appeal["created_at"] == appeal.created_at
        assert serialized_appeal["id"] == appeal.short_id
        assert serialized_appeal["text"] == appeal.text
        assert serialized_appeal["reason"] is None
        assert serialized_appeal["user"] == user_3.serialize(
            user_2_admin, light=True
        )
        assert serialized_appeal["updated_at"] is None

    def test_it_returns_serialized_appeal_for_appeal_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = self.create_admin_action(user_1_admin, user_2)
        appeal = AdminActionAppeal(
            action_id=admin_action.id,
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
        admin_action = self.create_admin_action(user_1_admin, user_2)
        appeal = AdminActionAppeal(
            action_id=admin_action.id,
            user_id=user_2.id,
            text=self.random_string(),
        )

        with pytest.raises(AdminActionAppealForbiddenException):
            appeal.serialize(user_3)

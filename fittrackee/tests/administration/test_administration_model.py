from datetime import datetime

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee import db
from fittrackee.administration.exceptions import (
    AdminActionForbiddenException,
    InvalidAdminActionException,
)
from fittrackee.administration.models import REPORT_ACTION_TYPES, AdminAction
from fittrackee.reports.models import Report
from fittrackee.users.models import User

from ..mixins import RandomMixin


class AdminActionTestCase(RandomMixin):
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

    @pytest.mark.parametrize(
        "input_action_type", ["user_suspension", "user_unsuspension"]
    )
    def test_it_raises_error_when_no_user_given_for_user_admin_action(
        self, app: Flask, user_1_admin: User, input_action_type: str
    ) -> None:
        with pytest.raises(InvalidAdminActionException):
            AdminAction(
                action_type=input_action_type,
                admin_user_id=user_1_admin.id,
                created_at=datetime.now(),
            )

    @pytest.mark.parametrize(
        "input_action_type", ["user_suspension", "user_unsuspension"]
    )
    def test_it_creates_user_admin_action_for_a_given_type_without_report(
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
        assert admin_action.created_at == created_at
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id

    def test_it_creates_user_admin_action_for_a_given_type_with_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
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
        assert admin_action.created_at == created_at
        assert admin_action.report_id == report.id
        assert admin_action.user_id == user_2.id

    @pytest.mark.parametrize(
        "input_action_type", ["report_reopening", "report_resolution"]
    )
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

    @pytest.mark.parametrize(
        "input_action_type", ["report_reopening", "report_resolution"]
    )
    def test_it_creates_report_admin_action_for_a_given_type(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        input_action_type: str,
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
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
        assert admin_action.created_at == created_at
        assert admin_action.report_id == report.id
        assert admin_action.user_id is None

    def test_it_does_not_store_user_id_when_action_is_for_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        now = datetime.utcnow()
        report = self.create_report(reporter=user_2, reported_user=user_3)
        action_type = "report_resolution"

        with freeze_time(now):
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
        assert admin_action.created_at == now
        assert admin_action.report_id == report.id
        assert admin_action.user_id is None

    def test_it_creates_report_action_without_given_date(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        now = datetime.utcnow()
        action_type = "user_suspension"

        with freeze_time(now):
            admin_action = AdminAction(
                action_type=action_type,
                admin_user_id=user_1_admin.id,
                user_id=user_2.id,
            )
        db.session.add(admin_action)
        db.session.commit()

        assert admin_action.action_type == action_type
        assert admin_action.admin_user_id == user_1_admin.id
        assert admin_action.created_at == now
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id

    def test_it_sets_null_for_admin_user_id_when_admin_user_is_deleted(
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
        assert admin_action.created_at == now
        assert admin_action.report_id is None
        assert admin_action.user_id == user_2.id


class TestAdminActionSerializer(AdminActionTestCase):
    def test_it_returns_serialized_admin_action_without_report(
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
            user_1_admin
        )
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['report_id'] is None
        assert serialized_action['user'] == user_2.serialize(user_1_admin)

    def test_it_returns_serialized_admin_action_with_report(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        report = self.create_report(reporter=user_2, reported_user=user_3)
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
            user_1_admin
        )
        assert serialized_action['created_at'] == admin_action.created_at
        assert serialized_action['id'] == admin_action.short_id
        assert serialized_action['report_id'] == report.id
        assert serialized_action['user'] is None

    def test_it_serialized_action_for_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type="user_suspension",
            user_id=user_2.id,
        )
        db.session.add(admin_action)
        db.session.commit()
        now = datetime.utcnow()

        with freeze_time(now):
            serialized_action = admin_action.serialize(user_2)

        assert serialized_action == {
            "action_type": admin_action.action_type,
            "created_at": admin_action.created_at,
            "id": admin_action.short_id,
            "user": user_2.serialize(user_2),
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
            reporter=user_1_admin, reported_user=user_2
        )
        admin_action = AdminAction(
            admin_user_id=user_1_admin.id,
            action_type=input_action_type,
            report_id=report.id,
        )

        with pytest.raises(AdminActionForbiddenException):
            admin_action.serialize(user_2)

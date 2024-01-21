from datetime import datetime

import pytest
from flask import Flask
from freezegun import freeze_time

from fittrackee import bcrypt
from fittrackee.administration.models import AdminAction
from fittrackee.administration.users_service import UserManagerService
from fittrackee.reports.models import Report
from fittrackee.users.exceptions import (
    InvalidEmailException,
    UserAlreadySuspendedException,
    UserCreationException,
    UserNotFoundException,
)
from fittrackee.users.models import User

from ..utils import random_email, random_string


class TestUserManagerServiceUserUpdate:
    def test_it_raises_exception_if_user_does_not_exist(
        self, app: Flask
    ) -> None:
        user_manager_service = UserManagerService(username=random_string())

        with pytest.raises(UserNotFoundException):
            user_manager_service.update()

    def test_it_does_not_update_user_when_no_args_provided(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update()

        assert user_updated is False

    def test_it_returns_user(self, app: Flask, user_1: User) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        user, _, _ = user_manager_service.update()

        assert user == user_1

    def test_it_sets_admin_right_for_a_given_user(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        user_manager_service.update(is_admin=True)

        assert user_1.admin is True

    def test_it_return_updated_user_flag_to_true(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(is_admin=True)

        assert user_updated is True

    def test_it_does_not_raise_exception_when_user_has_already_admin_right(
        self, app: Flask, user_1_admin: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=user_1_admin.username
        )

        _, user_updated, _ = user_manager_service.update(is_admin=True)

        assert user_1_admin.admin is True
        assert user_updated is True

    @pytest.mark.parametrize('input_activate', [True, False])
    def test_it_activates_admin_account_if_user_is_inactive_regardless_activate_value(  # noqa
        self, app: Flask, inactive_user: User, input_activate: bool
    ) -> None:
        user_manager_service = UserManagerService(
            username=inactive_user.username
        )

        _, user_updated, _ = user_manager_service.update(
            is_admin=True, activate=input_activate
        )

        assert inactive_user.admin is True
        assert inactive_user.is_active is True
        assert inactive_user.confirmation_token is None
        assert user_updated is True

    def test_it_activates_given_user_account(
        self, app: Flask, inactive_user: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=inactive_user.username
        )

        _, user_updated, _ = user_manager_service.update(activate=True)

        assert inactive_user.is_active is True
        assert user_updated is True

    def test_it_deactivates_given_user_account(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(activate=False)

        assert user_1.is_active is False
        assert user_1.confirmation_token is None
        assert user_updated is True

    def test_it_empties_confirmation_token(
        self, app: Flask, inactive_user: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=inactive_user.username
        )

        _, user_updated, _ = user_manager_service.update(activate=True)

        assert inactive_user.confirmation_token is None
        assert user_updated is True

    def test_it_does_not_raise_error_if_user_account_already_activated(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(activate=True)

        assert user_1.is_active is True
        assert user_updated is True

    def test_it_resets_user_password(self, app: Flask, user_1: User) -> None:
        previous_password = user_1.password
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(reset_password=True)

        assert user_1.password != previous_password
        assert user_updated is True

    def test_new_password_is_encrypted(self, app: Flask, user_1: User) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, new_password = user_manager_service.update(
            reset_password=True
        )

        assert bcrypt.check_password_hash(user_1.password, new_password)
        assert user_updated is True

    def test_it_raises_exception_if_provided_email_is_invalid(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)
        with pytest.raises(
            InvalidEmailException, match='valid email must be provided'
        ):
            user_manager_service.update(new_email=random_string())

    def test_it_raises_exception_if_provided_email_is_current_user_email(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)
        with pytest.raises(
            InvalidEmailException,
            match='new email must be different than current email',
        ):
            user_manager_service.update(new_email=user_1.email)

    def test_it_updates_user_email_to_confirm(
        self, app: Flask, user_1: User
    ) -> None:
        new_email = random_email()
        current_email = user_1.email
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(new_email=new_email)

        assert user_1.email == current_email
        assert user_1.email_to_confirm == new_email
        assert user_1.confirmation_token is not None
        assert user_updated is True

    def test_it_updates_user_email(self, app: Flask, user_1: User) -> None:
        new_email = random_email()
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(
            new_email=new_email, with_confirmation=False
        )

        assert user_1.email == new_email
        assert user_1.email_to_confirm is None
        assert user_1.confirmation_token is None
        assert user_updated is True

    def test_it_suspends_user(self, app: Flask, user_1: User) -> None:
        user_manager_service = UserManagerService(username=user_1.username)
        now = datetime.utcnow()

        with freeze_time(now):
            _, user_updated, _ = user_manager_service.update(suspended=True)

        assert user_1.is_active is True
        assert user_1.suspended_at == now
        assert user_updated is True

    def test_it_raises_error_when_user_is_already_suspended(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.suspended_at = datetime.utcnow()
        user_manager_service = UserManagerService(username=user_1.username)

        with pytest.raises(
            UserAlreadySuspendedException,
            match=f"user '{user_1.username}' already suspended",
        ):
            user_manager_service.update(suspended=True)

    def test_it_removes_admin_right_when_user_is_suspended(
        self, app: Flask, user_1_admin: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=user_1_admin.username
        )
        now = datetime.utcnow()

        with freeze_time(now):
            _, user_updated, _ = user_manager_service.update(suspended=True)

        assert user_1_admin.admin is False
        assert user_1_admin.is_active is True
        assert user_1_admin.suspended_at == now
        assert user_updated is True

    def test_it_unsuspends_user(self, app: Flask, user_1: User) -> None:
        user_1.suspended_at = datetime.utcnow()
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(suspended=False)

        assert user_1.is_active is True
        assert user_1.suspended_at is None
        assert user_updated is True

    def test_it_does_not_update_suspended_when_suspended_is_none(
        self, app: Flask, user_1: User
    ) -> None:
        suspended_at = datetime.utcnow()
        user_1.suspended_at = suspended_at
        user_manager_service = UserManagerService(username=user_1.username)

        _, user_updated, _ = user_manager_service.update(suspended=None)

        assert user_1.is_active is True
        assert user_1.suspended_at == suspended_at
        assert user_updated is False

    @pytest.mark.parametrize(
        'input_suspended, expected_action_action',
        [(True, "user_suspension"), (False, "user_unsuspension")],
    )
    @pytest.mark.parametrize('created_report', [True, False])
    def test_it_creates_admin_action_when_updated_suspended_status(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        input_suspended: bool,
        expected_action_action: str,
        created_report: bool,
    ) -> None:
        report_id = None
        if created_report:
            report_id = Report(
                reported_by=user_1_admin.id,
                note=random_string(),
                object_type='user',
                object_id=user_2.id,
            ).id

        user_manager_service = UserManagerService(
            admin_user_id=user_1_admin.id, username=user_2.username
        )
        now = datetime.utcnow()

        with freeze_time(now):
            user_manager_service.update(suspended=input_suspended)

        admin_action = AdminAction.query.filter_by(
            admin_user_id=user_1_admin.id,
            action_type=expected_action_action,
            user_id=user_2.id,
        ).first()
        assert admin_action.created_at == now
        assert admin_action.report_id == report_id


class TestUserManagerServiceUserCreation:
    def test_it_raises_exception_if_provided_username_is_invalid(
        self, app: Flask
    ) -> None:
        user_manager_service = UserManagerService(username='.admin')
        with pytest.raises(
            UserCreationException,
            match=(
                'username: only alphanumeric characters and '
                'the underscore character "_" allowed\n'
            ),
        ):
            user_manager_service.create(email=random_email())

    def test_it_raises_exception_if_a_user_exists_with_same_username(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)
        with pytest.raises(
            UserCreationException,
            match='sorry, that username is already taken',
        ):
            user_manager_service.create(email=random_email())

    def test_it_raises_exception_if_provided_email_is_invalid(
        self, app: Flask
    ) -> None:
        user_manager_service = UserManagerService(username=random_string())
        with pytest.raises(
            UserCreationException, match='valid email must be provided'
        ):
            user_manager_service.create(email=random_string())

    def test_it_raises_exception_if_a_user_exists_with_same_email(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=random_string())
        with pytest.raises(
            UserCreationException,
            match='This user already exists. No action done.',
        ):
            user_manager_service.create(email=user_1.email)

    def test_it_creates_user_with_provided_password(self, app: Flask) -> None:
        username = random_string()
        email = random_email()
        password = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, user_password = user_manager_service.create(email, password)

        assert new_user
        assert new_user.username == username
        assert new_user.email == email
        assert bcrypt.check_password_hash(new_user.password, password)
        assert user_password == password

    def test_it_creates_user_when_password_is_not_provided(
        self, app: Flask
    ) -> None:
        username = random_string()
        email = random_email()
        user_manager_service = UserManagerService(username=username)

        new_user, user_password = user_manager_service.create(email)

        assert new_user
        assert new_user.username == username
        assert new_user.email == email
        assert bcrypt.check_password_hash(new_user.password, user_password)

    def test_it_creates_when_registration_is_not_enabled(
        self,
        app_with_3_users_max: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
    ) -> None:
        username = random_string()
        email = random_email()
        user_manager_service = UserManagerService(username=username)

        new_user, user_password = user_manager_service.create(email)

        assert new_user
        assert new_user.username == username
        assert new_user.email == email
        assert bcrypt.check_password_hash(new_user.password, user_password)

    def test_created_user_is_inactive(self, app: Flask) -> None:
        username = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, _ = user_manager_service.create(email=random_email())

        assert new_user
        assert new_user.is_active is False
        assert new_user.confirmation_token is not None

    def test_created_user_has_no_admin_rights(self, app: Flask) -> None:
        username = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, _ = user_manager_service.create(email=random_email())

        assert new_user
        assert new_user.admin is False

    def test_created_user_does_not_accept_privacy_policy(
        self, app: Flask
    ) -> None:
        username = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, _ = user_manager_service.create(email=random_email())

        assert new_user
        assert new_user.accepted_policy_date is None

    def test_created_user_timezone_is_europe_paris(self, app: Flask) -> None:
        username = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, _ = user_manager_service.create(email=random_email())

        assert new_user
        assert new_user.timezone == 'Europe/Paris'

    def test_created_user_date_format_is_MM_dd_yyyy(  # noqa
        self, app: Flask
    ) -> None:
        username = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, _ = user_manager_service.create(email=random_email())

        assert new_user
        assert new_user.date_format == 'MM/dd/yyyy'

    def test_created_user_language_is_en(self, app: Flask) -> None:
        username = random_string()
        user_manager_service = UserManagerService(username=username)

        new_user, _ = user_manager_service.create(email=random_email())

        assert new_user
        assert new_user.language == 'en'

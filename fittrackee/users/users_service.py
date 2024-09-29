import secrets
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy import func

from fittrackee import db
from fittrackee.administration.models import AdminAction
from fittrackee.users.constants import USER_DATE_FORMAT, USER_TIMEZONE
from fittrackee.users.exceptions import (
    InvalidEmailException,
    MissingAdminIdException,
    MissingReportIdException,
    UserAlreadySuspendedException,
    UserControlsException,
    UserCreationException,
    UserNotFoundException,
)
from fittrackee.users.models import User
from fittrackee.users.utils.controls import is_valid_email, register_controls


class UserManagerService:
    def __init__(self, username: str, admin_user_id: Optional[int] = None):
        self.username = username
        self.admin_user_id = admin_user_id

    def _get_user(self) -> User:
        user = User.query.filter_by(username=self.username).first()
        if not user:
            raise UserNotFoundException()
        return user

    @staticmethod
    def _update_active_status(user: User, active_status: bool) -> None:
        user.is_active = active_status
        if active_status:
            user.confirmation_token = None

    @staticmethod
    def _reset_user_password(user: User) -> str:
        new_password = secrets.token_urlsafe(30)
        user.password = user.generate_password_hash(new_password)
        return new_password

    @staticmethod
    def _update_user_email(
        user: User, new_email: str, with_confirmation: bool
    ) -> None:
        if not is_valid_email(new_email):
            raise InvalidEmailException('valid email must be provided')
        if user.email == new_email:
            raise InvalidEmailException(
                'new email must be different than current email'
            )
        if with_confirmation:
            user.email_to_confirm = new_email
            user.confirmation_token = secrets.token_urlsafe(30)
        else:
            user.email = new_email

    def update(
        self,
        is_admin: Optional[bool] = None,
        activate: Optional[bool] = None,
        reset_password: bool = False,
        new_email: Optional[str] = None,
        with_confirmation: bool = True,
        suspended: Optional[bool] = None,
        report_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Tuple[User, bool, Optional[str], Optional[AdminAction]]:
        user_updated = False
        new_password = None
        admin_action = None
        user = self._get_user()
        if suspended is not None:
            if self.admin_user_id is None:
                raise MissingAdminIdException()
            if report_id is None:
                raise MissingReportIdException()

        if is_admin is not None:
            user.admin = is_admin
            if is_admin:
                activate = True
            user_updated = True

        if activate is not None:
            self._update_active_status(user, activate)
            user_updated = True

        if reset_password:
            new_password = self._reset_user_password(user)
            user_updated = True

        if new_email is not None:
            self._update_user_email(user, new_email, with_confirmation)
            user_updated = True

        now = datetime.utcnow()
        if suspended is True:
            if user.suspended_at:
                raise UserAlreadySuspendedException(
                    f"user '{user.username}' already suspended"
                )
            user.suspended_at = now
            user.admin = False
            user_updated = True
        if suspended is False:
            user.suspended_at = None
            user_updated = True
        if self.admin_user_id and suspended is not None:
            admin_action = AdminAction(
                admin_user_id=self.admin_user_id,
                action_type=(
                    "user_suspension" if suspended else "user_unsuspension"
                ),
                created_at=now,
                report_id=report_id,
                reason=reason,
                user_id=user.id,
            )
            db.session.add(admin_action)

        db.session.commit()
        return user, user_updated, new_password, admin_action

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        check_email: bool = False,
    ) -> Tuple[Optional[User], Optional[str]]:
        if not password:
            password = secrets.token_urlsafe(30)

        ret = register_controls(self.username, email, password)

        if ret != '':
            raise UserControlsException(ret)

        user = User.query.filter(
            func.lower(User.username) == func.lower(self.username)
        ).first()
        if user:
            raise UserCreationException(
                'sorry, that username is already taken'
            )

        # if a user exists with same email address, no error is returned
        # since a user has to confirm his email to activate his account
        user = User.query.filter(
            func.lower(User.email) == func.lower(email)
        ).first()
        if user:
            if check_email:
                raise UserCreationException(
                    'This user already exists. No action done.'
                )
            return None, None

        new_user = User(username=self.username, email=email, password=password)
        new_user.timezone = USER_TIMEZONE
        new_user.date_format = USER_DATE_FORMAT
        new_user.confirmation_token = secrets.token_urlsafe(30)
        db.session.add(new_user)
        db.session.flush()

        return new_user, password

    def create(
        self,
        email: str,
        password: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[str]]:
        try:
            new_user, password = self.create_user(
                email, password, check_email=True
            )
            if new_user:
                new_user.language = 'en'
                db.session.commit()
        except UserControlsException as e:
            raise UserCreationException(str(e))
        return new_user, password

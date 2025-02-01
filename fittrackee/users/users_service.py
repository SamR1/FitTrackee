import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import func

from fittrackee import db
from fittrackee.reports.models import ReportAction
from fittrackee.users.constants import (
    ADMINISTRATOR_NOTIFICATION_TYPES,
    MODERATOR_NOTIFICATION_TYPES,
    USER_DATE_FORMAT,
    USER_TIMEZONE,
)
from fittrackee.users.exceptions import (
    InvalidEmailException,
    InvalidUserRole,
    MissingAdminIdException,
    MissingReportIdException,
    OwnerException,
    UserAlreadyReactivatedException,
    UserAlreadySuspendedException,
    UserControlsException,
    UserCreationException,
    UserNotFoundException,
)
from fittrackee.users.models import (
    Notification,
    User,
)
from fittrackee.users.roles import UserRole
from fittrackee.users.utils.controls import is_valid_email, register_controls


class UserManagerService:
    def __init__(self, username: str, moderator_id: Optional[int] = None):
        self.username = username
        self.moderator_id = moderator_id

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
            raise InvalidEmailException("valid email must be provided")
        if user.email == new_email:
            raise InvalidEmailException(
                "new email must be different than current email"
            )
        if with_confirmation:
            user.email_to_confirm = new_email
            user.confirmation_token = secrets.token_urlsafe(30)
        else:
            user.email = new_email

    def update(
        self,
        role: Optional[str] = None,
        activate: Optional[bool] = None,
        reset_password: bool = False,
        new_email: Optional[str] = None,
        with_confirmation: bool = True,
        suspended: Optional[bool] = None,
        report_id: Optional[int] = None,
        reason: Optional[str] = None,
        raise_error_on_owner: bool = False,
    ) -> Tuple[User, bool, Optional[str], Optional[ReportAction]]:
        user_updated = False
        new_password = None
        report_action = None
        user = self._get_user()

        if user.role == UserRole.OWNER.value and raise_error_on_owner:
            raise OwnerException("user with owner rights can not be modified")

        if suspended is not None:
            if self.moderator_id is None:
                raise MissingAdminIdException()
            if report_id is None:
                raise MissingReportIdException()

        if role is not None:
            if role not in UserRole.db_choices():
                raise InvalidUserRole()
            user.role = UserRole[role.upper()].value
            if user.role >= UserRole.MODERATOR.value:
                activate = True
            if user.role < UserRole.MODERATOR.value:
                db.session.query(Notification).filter(
                    Notification.to_user_id == user.id,
                    Notification.event_type.in_(MODERATOR_NOTIFICATION_TYPES),
                ).delete()
            if user.role < UserRole.ADMIN.value:
                db.session.query(Notification).filter(
                    Notification.to_user_id == user.id,
                    Notification.event_type.in_(
                        ADMINISTRATOR_NOTIFICATION_TYPES
                    ),
                ).delete()
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

        now = datetime.now(timezone.utc)
        if suspended is True:
            if user.suspended_at:
                raise UserAlreadySuspendedException()
            user.suspended_at = now
            user.role = UserRole.USER.value
            user_updated = True
        if suspended is False:
            if user.suspended_at is None:
                raise UserAlreadyReactivatedException()
            user.suspended_at = None
            user_updated = True
        if self.moderator_id and report_id and suspended is not None:
            report_action = ReportAction(
                moderator_id=self.moderator_id,
                action_type=(
                    "user_suspension" if suspended else "user_unsuspension"
                ),
                created_at=now,
                report_id=report_id,
                reason=reason,
                user_id=user.id,
            )
            db.session.add(report_action)

        db.session.commit()
        return user, user_updated, new_password, report_action

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        check_email: bool = False,
        role: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[str]]:
        if not password:
            password = secrets.token_urlsafe(30)

        ret = register_controls(self.username, email, password)

        if ret != "":
            raise UserControlsException(ret)

        user = User.query.filter(
            func.lower(User.username) == func.lower(self.username)
        ).first()
        if user:
            raise UserCreationException(
                "sorry, that username is already taken"
            )

        # if a user exists with same email address, no error is returned
        # since a user has to confirm his email to activate his account
        user = User.query.filter(
            func.lower(User.email) == func.lower(email)
        ).first()
        if user:
            if check_email:
                raise UserCreationException(
                    "This user already exists. No action done."
                )
            return None, None

        new_user = User(username=self.username, email=email, password=password)
        new_user.timezone = USER_TIMEZONE
        new_user.date_format = USER_DATE_FORMAT
        new_user.confirmation_token = secrets.token_urlsafe(30)

        if role is not None:
            if role not in UserRole.db_choices():
                raise InvalidUserRole()
            new_user.role = UserRole[role.upper()].value

        db.session.add(new_user)
        db.session.flush()

        return new_user, password

    def create(
        self,
        email: str,
        password: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Tuple[Optional[User], Optional[str]]:
        try:
            new_user, password = self.create_user(
                email, password, check_email=True, role=role
            )
            if new_user:
                new_user.language = "en"
                db.session.commit()
        except UserControlsException as e:
            raise UserCreationException(str(e)) from e
        return new_user, password

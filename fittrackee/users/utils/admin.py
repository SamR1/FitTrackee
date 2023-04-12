import secrets
from typing import Optional, Tuple

from sqlalchemy import func

from fittrackee import db

from ..exceptions import (
    InvalidEmailException,
    UserControlsException,
    UserCreationException,
    UserNotFoundException,
)
from ..models import User
from ..utils.controls import is_valid_email, register_controls


class UserManagerService:
    def __init__(self, username: str):
        self.username = username

    def _get_user(self) -> User:
        user = User.query.filter_by(username=self.username).first()
        if not user:
            raise UserNotFoundException()
        return user

    def _update_admin_rights(self, user: User, is_admin: bool) -> None:
        user.admin = is_admin
        if is_admin:
            self._activate_user(user)

    @staticmethod
    def _activate_user(user: User) -> None:
        user.is_active = True
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
                'new email must be different than curent email'
            )
        if with_confirmation:
            user.email_to_confirm = new_email
            user.confirmation_token = secrets.token_urlsafe(30)
        else:
            user.email = new_email

    def update(
        self,
        is_admin: Optional[bool] = None,
        activate: bool = False,
        reset_password: bool = False,
        new_email: Optional[str] = None,
        with_confirmation: bool = True,
    ) -> Tuple[User, bool, Optional[str]]:
        user_updated = False
        new_password = None
        user = self._get_user()

        if is_admin is not None:
            self._update_admin_rights(user, is_admin)
            user_updated = True

        if activate:
            self._activate_user(user)
            user_updated = True

        if reset_password:
            new_password = self._reset_user_password(user)
            user_updated = True

        if new_email is not None:
            self._update_user_email(user, new_email, with_confirmation)
            user_updated = True

        db.session.commit()
        return user, user_updated, new_password

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
        new_user.timezone = 'Europe/Paris'
        new_user.date_format = 'MM/dd/yyyy'
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

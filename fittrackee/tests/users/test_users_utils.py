import time
from calendar import timegm
from datetime import datetime, timedelta
from typing import Dict, Optional
from unittest.mock import Mock, patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask

from fittrackee import bcrypt, db
from fittrackee.users.exceptions import (
    InvalidEmailException,
    UserCreationException,
    UserNotFoundException,
)
from fittrackee.users.models import BlacklistedToken, User
from fittrackee.users.utils.admin import UserManagerService
from fittrackee.users.utils.controls import (
    check_password,
    check_username,
    is_valid_email,
    register_controls,
)
from fittrackee.users.utils.token import (
    clean_blacklisted_tokens,
    decode_user_token,
    get_user_token,
)

from ..utils import random_email, random_int, random_string


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

        user_manager_service.update(is_admin=True)

        assert user_1_admin.admin is True

    def test_it_activates_account_if_user_is_inactive(
        self, app: Flask, inactive_user: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=inactive_user.username
        )

        user_manager_service.update(is_admin=True)

        assert inactive_user.admin is True
        assert inactive_user.is_active is True
        assert inactive_user.confirmation_token is None

    def test_it_activates_given_user_account(
        self, app: Flask, inactive_user: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=inactive_user.username
        )

        user_manager_service.update(activate=True)

        assert inactive_user.is_active is True

    def test_it_empties_confirmation_token(
        self, app: Flask, inactive_user: User
    ) -> None:
        user_manager_service = UserManagerService(
            username=inactive_user.username
        )

        user_manager_service.update(activate=True)

        assert inactive_user.confirmation_token is None

    def test_it_does_not_raise_error_if_user_account_already_activated(
        self, app: Flask, user_1: User
    ) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        user_manager_service.update(activate=True)

        assert user_1.is_active is True

    def test_it_resets_user_password(self, app: Flask, user_1: User) -> None:
        previous_password = user_1.password
        user_manager_service = UserManagerService(username=user_1.username)

        user_manager_service.update(reset_password=True)

        assert user_1.password != previous_password

    def test_new_password_is_encrypted(self, app: Flask, user_1: User) -> None:
        user_manager_service = UserManagerService(username=user_1.username)

        _, _, new_password = user_manager_service.update(reset_password=True)

        assert bcrypt.check_password_hash(user_1.password, new_password)

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

        user_manager_service.update(new_email=new_email)

        assert user_1.email == current_email
        assert user_1.email_to_confirm == new_email
        assert user_1.confirmation_token is not None

    def test_it_updates_user_email(self, app: Flask, user_1: User) -> None:
        new_email = random_email()
        user_manager_service = UserManagerService(username=user_1.username)

        user_manager_service.update(
            new_email=new_email, with_confirmation=False
        )

        assert user_1.email == new_email
        assert user_1.email_to_confirm is None
        assert user_1.confirmation_token is None


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


class TestIsValidEmail:
    @pytest.mark.parametrize(
        ('input_email',),
        [
            (None,),
            ('',),
            ('foo',),
            ('foo@',),
            ('@foo.fr',),
            ('foo@foo',),
            ('.',),
            ('./',),
        ],
    )
    def test_it_returns_false_if_email_is_invalid(
        self, input_email: str
    ) -> None:
        assert is_valid_email(input_email) is False

    @pytest.mark.parametrize(
        ('input_email',),
        [
            ('admin@example.com',),
            ('admin@test.example.com',),
            ('admin.site@test.example.com',),
            ('admin-site@test-example.com',),
        ],
    )
    def test_it_returns_true_if_email_is_valid(self, input_email: str) -> None:
        assert is_valid_email(input_email) is True


class TestCheckPasswords:
    @pytest.mark.parametrize(
        ('input_password_length',),
        [
            (0,),
            (3,),
            (7,),
        ],
    )
    def test_it_returns_error_message_string_if_password_length_is_below_8_characters(  # noqa
        self, input_password_length: int
    ) -> None:
        password = random_string(input_password_length)
        assert check_password(password) == (
            'password: 8 characters required\n'
        )

    @pytest.mark.parametrize(
        ('input_password_length',),
        [
            (8,),
            (10,),
        ],
    )
    def test_it_returns_empty_string_when_password_length_exceeds_7_characters(
        self, input_password_length: int
    ) -> None:
        password = random_string(input_password_length)
        assert check_password(password) == ''


class TestIsUsernameValid:
    @pytest.mark.parametrize(
        ('input_username_length',),
        [
            (2,),
            (31,),
        ],
    )
    def test_it_returns_error_message_when_username_length_is_invalid(
        self, input_username_length: int
    ) -> None:
        assert (
            check_username(
                username=random_string(31),
            )
            == 'username: 3 to 30 characters required\n'
        )

    @pytest.mark.parametrize(
        ('input_invalid_character',),
        [
            ('.',),
            ('/',),
            ('$',),
        ],
    )
    def test_it_returns_error_message_when_username_has_invalid_character(
        self, input_invalid_character: str
    ) -> None:
        username = random_string() + input_invalid_character
        assert check_username(username=username) == (
            'username: only alphanumeric characters and the '
            'underscore character "_" allowed\n'
        )

    def test_it_returns_empty_string_when_username_is_valid(self) -> None:
        assert check_username(username=random_string()) == ''

    def test_it_returns_multiple_errors(self) -> None:
        username = random_string(31) + '.'
        assert check_username(username=username) == (
            'username: 3 to 30 characters required\n'
            'username: only alphanumeric characters and the underscore '
            'character "_" allowed\n'
        )


class TestRegisterControls:
    module_path = 'fittrackee.users.utils.controls.'
    valid_username = random_string()
    valid_email = f'{random_string()}@example.com'
    valid_password = random_string()

    def test_it_calls_all_validators(self) -> None:
        with (
            patch(self.module_path + 'check_password') as check_passwords_mock,
            patch(self.module_path + 'check_username') as check_username_mock,
            patch(self.module_path + 'is_valid_email') as is_valid_email_mock,
        ):
            register_controls(
                self.valid_username,
                self.valid_email,
                self.valid_password,
            )

        check_passwords_mock.assert_called_once_with(self.valid_password)
        check_username_mock.assert_called_once_with(self.valid_username)
        is_valid_email_mock.assert_called_once_with(self.valid_email)

    def test_it_returns_empty_string_when_inputs_are_valid(self) -> None:
        assert (
            register_controls(
                self.valid_username,
                self.valid_email,
                self.valid_password,
            )
            == ''
        )

    def test_it_returns_multiple_errors_when_inputs_are_invalid(self) -> None:
        invalid_username = random_string(31)
        assert register_controls(
            username=invalid_username,
            email=invalid_username,
            password=random_string(8),
        ) == (
            'username: 3 to 30 characters required\n'
            'email: valid email must be provided\n'
        )


class TestGetUserToken:
    @staticmethod
    def decode_token(app: Flask, token: str) -> Dict:
        return jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=['HS256'],
        )

    def test_token_is_encoded_with_hs256(self, app: Flask) -> None:
        token = get_user_token(user_id=1)

        decoded_token = self.decode_token(app, token)
        assert list(decoded_token.keys()) == ['exp', 'iat', 'sub']

    @pytest.mark.parametrize('input_password_reset', [True, False])
    def test_token_contains_user_id(
        self, app: Flask, input_password_reset: bool
    ) -> None:
        user_id = 1
        token = get_user_token(
            user_id=user_id, password_reset=input_password_reset
        )

        decoded_token = self.decode_token(app, token)
        assert decoded_token['sub'] == str(user_id)

    @pytest.mark.parametrize('input_password_reset', [True, False])
    def test_token_contains_timestamp_of_when_it_is_issued(
        self, app: Flask, input_password_reset: bool
    ) -> None:
        user_id = 1
        iat = datetime.utcnow()
        with patch('fittrackee.users.utils.token.datetime') as datetime_mock:
            datetime_mock.utcnow = Mock(return_value=iat)

            token = get_user_token(
                user_id=user_id, password_reset=input_password_reset
            )

            decoded_token = self.decode_token(app, token)
            assert decoded_token['iat'] == timegm(iat.utctimetuple())

    def test_token_contains_timestamp_of_when_it_expired(
        self, app: Flask
    ) -> None:
        user_id = 1
        iat = datetime.utcnow()
        expiration = timedelta(
            days=app.config['TOKEN_EXPIRATION_DAYS'],
            seconds=app.config['TOKEN_EXPIRATION_SECONDS'],
        )
        with patch('fittrackee.users.utils.token.datetime') as datetime_mock:
            datetime_mock.utcnow = Mock(return_value=iat)

            token = get_user_token(user_id=user_id)

            decoded_token = self.decode_token(app, token)
            assert decoded_token['exp'] == timegm(
                (iat + expiration).utctimetuple()
            )

    def test_password_token_contains_timestamp_of_when_it_expired(
        self, app: Flask
    ) -> None:
        user_id = 1
        iat = datetime.utcnow()
        expiration = timedelta(
            days=0.0,
            seconds=app.config['PASSWORD_TOKEN_EXPIRATION_SECONDS'],
        )
        with patch('fittrackee.users.utils.token.datetime') as datetime_mock:
            datetime_mock.utcnow = Mock(return_value=iat)

            token = get_user_token(user_id=user_id, password_reset=True)

            decoded_token = self.decode_token(app, token)
            assert decoded_token['exp'] == timegm(
                (iat + expiration).utctimetuple()
            )


class TestDecodeUserToken:
    @staticmethod
    def generate_token(user_id: int, now: datetime) -> str:
        with patch('fittrackee.users.utils.token.datetime') as datetime_mock:
            datetime_mock.utcnow = Mock(return_value=now)
            token = get_user_token(user_id)
        return token

    def test_it_raises_error_when_token_is_invalid(self, app: Flask) -> None:
        with pytest.raises(jwt.exceptions.DecodeError):
            decode_user_token(random_string())

    def test_it_raises_error_when_token_body_is_invalid(
        self, app: Flask
    ) -> None:
        token = self.generate_token(user_id=1, now=datetime.utcnow())
        header, body, signature = token.split('.')
        modified_token = f'{header}.{random_string()}.{signature}'
        with pytest.raises(
            jwt.exceptions.InvalidSignatureError,
            match='Signature verification failed',
        ):
            decode_user_token(modified_token)

    def test_it_raises_error_when_secret_key_is_invalid(
        self, app: Flask
    ) -> None:
        now = datetime.utcnow()
        token = jwt.encode(
            {
                'exp': now + timedelta(minutes=1),
                'iat': now,
                'sub': 1,
            },
            random_string(),
            algorithm='HS256',
        )
        with pytest.raises(
            jwt.exceptions.InvalidSignatureError,
            match='Signature verification failed',
        ):
            decode_user_token(token)

    def test_it_raises_error_when_algorithm_is_not_hs256(
        self, app: Flask
    ) -> None:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        now = datetime.utcnow()
        token = jwt.encode(
            {
                'exp': now + timedelta(minutes=1),
                'iat': now,
                'sub': 1,
            },
            private_key.decode(),
            algorithm="RS256",
        )
        with pytest.raises(jwt.exceptions.InvalidAlgorithmError):
            decode_user_token(token)

    def test_it_raises_error_when_token_is_expired(self, app: Flask) -> None:
        now = datetime.utcnow() - timedelta(minutes=10)
        token = self.generate_token(user_id=1, now=now)
        with pytest.raises(
            jwt.exceptions.ExpiredSignatureError, match='Signature has expired'
        ):
            decode_user_token(token)

    def test_it_returns_user_id(self, app: Flask) -> None:
        expected_user_id = 1
        token = self.generate_token(
            user_id=expected_user_id, now=datetime.utcnow()
        )

        user_id = decode_user_token(token)

        assert user_id == expected_user_id


class TestBlacklistedTokensCleanup:
    @staticmethod
    def blacklisted_token(expiration_days: Optional[int] = None) -> str:
        token = get_user_token(user_id=random_int())
        blacklisted_token = BlacklistedToken(token=token)
        if expiration_days is not None:
            blacklisted_token.expired_at = int(time.time()) - (
                expiration_days * 86400
            )
        db.session.add(blacklisted_token)
        db.session.commit()
        return token

    def test_it_returns_0_as_count_when_no_blacklisted_token_deleted(
        self, app: Flask, user_1: User
    ) -> None:
        count = clean_blacklisted_tokens(days=30)

        assert count == 0

    def test_it_does_not_delete_blacklisted_token_when_not_expired(
        self, app: Flask, user_1: User
    ) -> None:
        token = self.blacklisted_token()

        clean_blacklisted_tokens(days=10)

        existing_token = BlacklistedToken.query.filter_by(token=token).first()
        assert existing_token is not None

    def test_it_deletes_blacklisted_token_when_expired_more_then_provided_days(
        self, app: Flask, user_1: User
    ) -> None:
        token = self.blacklisted_token(expiration_days=40)

        clean_blacklisted_tokens(days=30)

        existing_token = BlacklistedToken.query.filter_by(token=token).first()
        assert existing_token is None

    def test_it_does_not_delete_blacklisted_token_when_expired_below_provided_days(  # noqa
        self, app: Flask, user_1: User
    ) -> None:
        token = self.blacklisted_token(expiration_days=30)

        clean_blacklisted_tokens(days=40)

        existing_token = BlacklistedToken.query.filter_by(token=token).first()
        assert existing_token is not None

    def test_it_returns_deleted_rows_count(
        self, app: Flask, user_1: User
    ) -> None:
        self.blacklisted_token()
        for _ in range(3):
            self.blacklisted_token(expiration_days=30)

        count = clean_blacklisted_tokens(
            days=app.config['TOKEN_EXPIRATION_DAYS']
        )

        assert count == 3

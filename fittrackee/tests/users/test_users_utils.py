import time
from calendar import timegm
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask
from time_machine import travel

from fittrackee import db
from fittrackee.users.models import BlacklistedToken, User
from fittrackee.users.utils.controls import (
    check_password,
    check_username,
    is_valid_email,
    register_controls,
)
from fittrackee.users.utils.tokens import (
    clean_blacklisted_tokens,
    decode_user_token,
    get_user_token,
)

from ..utils import random_int, random_string


class TestIsValidEmail:
    @pytest.mark.parametrize(
        ("input_email",),
        [
            (None,),
            ("",),
            ("foo",),
            ("foo@",),
            ("@foo.fr",),
            ("foo@foo",),
            (".",),
            ("./",),
        ],
    )
    def test_it_returns_false_if_email_is_invalid(
        self, input_email: str
    ) -> None:
        assert is_valid_email(input_email) is False

    @pytest.mark.parametrize(
        ("input_email",),
        [
            ("admin@example.com",),
            ("admin@test.example.com",),
            ("admin.site@test.example.com",),
            ("admin-site@test-example.com",),
        ],
    )
    def test_it_returns_true_if_email_is_valid(self, input_email: str) -> None:
        assert is_valid_email(input_email) is True


class TestCheckPasswords:
    @pytest.mark.parametrize(
        ("input_password_length",),
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
            "password: 8 characters required\n"
        )

    @pytest.mark.parametrize(
        ("input_password_length",),
        [
            (8,),
            (10,),
        ],
    )
    def test_it_returns_empty_string_when_password_length_exceeds_7_characters(
        self, input_password_length: int
    ) -> None:
        password = random_string(input_password_length)
        assert check_password(password) == ""


class TestIsUsernameValid:
    @pytest.mark.parametrize(
        ("input_username_length",),
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
            == "username: 3 to 30 characters required\n"
        )

    @pytest.mark.parametrize(
        ("input_invalid_character",),
        [
            (".",),
            ("/",),
            ("$",),
        ],
    )
    def test_it_returns_error_message_when_username_has_invalid_character(
        self, input_invalid_character: str
    ) -> None:
        username = random_string() + input_invalid_character
        assert check_username(username=username) == (
            "username: only alphanumeric characters and the "
            'underscore character "_" allowed\n'
        )

    def test_it_returns_empty_string_when_username_is_valid(self) -> None:
        assert check_username(username=random_string()) == ""

    def test_it_returns_multiple_errors(self) -> None:
        username = random_string(31) + "."
        assert check_username(username=username) == (
            "username: 3 to 30 characters required\n"
            "username: only alphanumeric characters and the underscore "
            'character "_" allowed\n'
        )


class TestRegisterControls:
    module_path = "fittrackee.users.utils.controls."
    valid_username = random_string()
    valid_email = f"{random_string()}@example.com"
    valid_password = random_string()

    def test_it_calls_all_validators(self) -> None:
        with (
            patch(self.module_path + "check_password") as check_passwords_mock,
            patch(self.module_path + "check_username") as check_username_mock,
            patch(self.module_path + "is_valid_email") as is_valid_email_mock,
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
            == ""
        )

    def test_it_returns_multiple_errors_when_inputs_are_invalid(self) -> None:
        invalid_username = random_string(31)
        assert register_controls(
            username=invalid_username,
            email=invalid_username,
            password=random_string(8),
        ) == (
            "username: 3 to 30 characters required\n"
            "email: valid email must be provided\n"
        )


class TestGetUserToken:
    @staticmethod
    def decode_token(app: Flask, token: str) -> Dict:
        return jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )

    def test_token_is_encoded_with_hs256(self, app: Flask) -> None:
        token = get_user_token(user_id=1)

        decoded_token = self.decode_token(app, token)
        assert list(decoded_token.keys()) == ["exp", "iat", "sub"]

    @pytest.mark.parametrize("input_password_reset", [True, False])
    def test_token_contains_user_id(
        self, app: Flask, input_password_reset: bool
    ) -> None:
        user_id = 1
        token = get_user_token(
            user_id=user_id, password_reset=input_password_reset
        )

        decoded_token = self.decode_token(app, token)
        assert decoded_token["sub"] == str(user_id)

    @pytest.mark.parametrize("input_password_reset", [True, False])
    def test_token_contains_timestamp_of_when_it_is_issued(
        self, app: Flask, input_password_reset: bool
    ) -> None:
        user_id = 1
        iat = datetime.now(timezone.utc)
        with travel(iat, tick=False):
            token = get_user_token(
                user_id=user_id, password_reset=input_password_reset
            )

            decoded_token = self.decode_token(app, token)
            assert decoded_token["iat"] == timegm(iat.utctimetuple())

    def test_token_contains_timestamp_of_when_it_expired(
        self, app: Flask
    ) -> None:
        user_id = 1
        iat = datetime.now(timezone.utc)
        expiration = timedelta(
            days=app.config["TOKEN_EXPIRATION_DAYS"],
            seconds=app.config["TOKEN_EXPIRATION_SECONDS"],
        )
        with travel(iat, tick=False):
            token = get_user_token(user_id=user_id)

            decoded_token = self.decode_token(app, token)
            assert decoded_token["exp"] == timegm(
                (iat + expiration).utctimetuple()
            )

    def test_password_token_contains_timestamp_of_when_it_expired(
        self, app: Flask
    ) -> None:
        user_id = 1
        iat = datetime.now(timezone.utc)
        expiration = timedelta(
            days=0.0,
            seconds=app.config["PASSWORD_TOKEN_EXPIRATION_SECONDS"],
        )
        with travel(iat, tick=False):
            token = get_user_token(user_id=user_id, password_reset=True)

            decoded_token = self.decode_token(app, token)
            assert decoded_token["exp"] == timegm(
                (iat + expiration).utctimetuple()
            )


class TestDecodeUserToken:
    @staticmethod
    def generate_token(user_id: int, now: datetime) -> str:
        with travel(now, tick=False):
            token = get_user_token(user_id)
        return token

    def test_it_raises_error_when_token_is_invalid(self, app: Flask) -> None:
        with pytest.raises(jwt.exceptions.DecodeError):
            decode_user_token(random_string())

    def test_it_raises_error_when_token_body_is_invalid(
        self, app: Flask
    ) -> None:
        token = self.generate_token(user_id=1, now=datetime.now(timezone.utc))
        header, body, signature = token.split(".")
        modified_token = f"{header}.{random_string()}.{signature}"
        with pytest.raises(
            jwt.exceptions.InvalidSignatureError,
            match="Signature verification failed",
        ):
            decode_user_token(modified_token)

    def test_it_raises_error_when_secret_key_is_invalid(
        self, app: Flask
    ) -> None:
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "exp": now + timedelta(minutes=1),
                "iat": now,
                "sub": 1,
            },
            random_string(),
            algorithm="HS256",
        )
        with pytest.raises(
            jwt.exceptions.InvalidSignatureError,
            match="Signature verification failed",
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
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "exp": now + timedelta(minutes=1),
                "iat": now,
                "sub": 1,
            },
            private_key.decode(),
            algorithm="RS256",
        )
        with pytest.raises(jwt.exceptions.InvalidAlgorithmError):
            decode_user_token(token)

    def test_it_raises_error_when_token_is_expired(self, app: Flask) -> None:
        now = datetime.now(timezone.utc) - timedelta(minutes=10)
        token = self.generate_token(user_id=1, now=now)
        with pytest.raises(
            jwt.exceptions.ExpiredSignatureError, match="Signature has expired"
        ):
            decode_user_token(token)

    def test_it_returns_user_id(self, app: Flask) -> None:
        expected_user_id = 1
        token = self.generate_token(
            user_id=expected_user_id, now=datetime.now(timezone.utc)
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
            days=app.config["TOKEN_EXPIRATION_DAYS"]
        )

        assert count == 3

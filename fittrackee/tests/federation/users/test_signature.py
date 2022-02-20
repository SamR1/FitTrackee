import base64
from datetime import datetime, timedelta
from typing import Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Flask

from fittrackee.federation.exceptions import InvalidSignatureException
from fittrackee.federation.models import Actor
from fittrackee.federation.signature import (
    VALID_DATE_DELTA,
    VALID_DATE_FORMAT,
    SignatureVerification,
)

from ...utils import generate_response, random_string


class SignatureVerificationTestCase:
    @staticmethod
    def get_date_string(date: Optional[datetime] = None) -> str:
        date = date if date else datetime.utcnow()
        return date.strftime(VALID_DATE_FORMAT)

    @staticmethod
    def random_signature() -> str:
        return str(base64.b64encode(random_string().encode()))

    def generate_headers(
        self,
        key_id: Optional[str] = None,
        signature: Optional[str] = None,
        date_str: Optional[str] = None,  # overrides date
        date: Optional[datetime] = None,
        host: Optional[str] = None,
    ) -> Dict:
        key_id = key_id if key_id else random_string()
        signature = signature if signature else self.random_signature()
        signature_headers = (
            f'keyId="{key_id}",headers="(request-target) host date",'
            f'signature="' + signature + '"'
        )
        if date_str is None:
            date_str = self.get_date_string(date)
        return {
            'Host': host if host else random_string(),
            'Date': date_str,
            'Signature': signature_headers,
            'Content-Type': 'application/ld+json',
        }

    def generate_valid_headers(
        self, host: str, actor: Actor, date_str: Optional[str] = None
    ) -> Dict:
        if date_str is None:
            now = datetime.utcnow()
            date_str = now.strftime(VALID_DATE_FORMAT)
        signed_string = (
            f'(request-target): post /inbox\nhost: {host}\n'
            f'date: {date_str}'
        )
        key = RSA.import_key(actor.private_key)
        key_signer = pkcs1_15.new(key)
        encoded_string = signed_string.encode('utf-8')
        h = SHA256.new(encoded_string)
        signature = base64.b64encode(key_signer.sign(h))
        return self.generate_headers(
            key_id=actor.activitypub_id,
            signature=signature.decode(),
            date_str=date_str,
            host=host,
        )

    @staticmethod
    def get_request_mock(headers: Optional[Dict] = None) -> MagicMock:
        request_mock = MagicMock()
        request_mock.headers = headers if headers else {}
        request_mock.path = '/inbox'
        return request_mock


class TestSignatureVerificationInstantiation(SignatureVerificationTestCase):
    def test_it_raises_error_if_headers_are_empty(self) -> None:
        request_with_empty_headers = self.get_request_mock()

        with pytest.raises(InvalidSignatureException):
            SignatureVerification.get_signature(request_with_empty_headers)

    @pytest.mark.parametrize(
        'input_description,input_signature_headers',
        [
            (
                'missing keyId',
                'headers="(request-target) host date",'
                f'signature="{random_string()}"',
            ),
            (
                'missing headers',
                f'keyId="{random_string()}", signature="{random_string()}"',
            ),
            (
                'missing signature',
                f'keyId="{random_string()}",'
                'headers="(request-target) host date"',
            ),
        ],
    )
    def test_it_raises_error_if_a_signature_key_is_missing(
        self, input_description: str, input_signature_headers: str
    ) -> None:
        request_with_empty_headers = self.get_request_mock(
            headers={
                'Host': random_string(),
                'Date': self.get_date_string(),
                'Signature': input_signature_headers,
            }
        )

        with pytest.raises(InvalidSignatureException):
            SignatureVerification.get_signature(request_with_empty_headers)

    def test_it_instantiates_signature_verification(self) -> None:
        key_id = random_string()
        signature = self.random_signature()
        signature_headers = (
            f'keyId="{key_id}",headers="(request-target) host date",'
            f'signature="' + signature + '"'
        )
        date_str = self.get_date_string()
        valid_request_mock = self.get_request_mock(
            headers={
                'Host': random_string(),
                'Date': date_str,
                'Signature': signature_headers,
            }
        )

        sig_verification = SignatureVerification.get_signature(
            valid_request_mock
        )

        assert sig_verification.request == valid_request_mock
        assert sig_verification.date_str == date_str
        assert sig_verification.key_id == key_id
        assert sig_verification.headers == '(request-target) host date'
        assert sig_verification.signature == base64.b64decode(signature)


class TestSignatureDateVerification(SignatureVerificationTestCase):
    def test_it_returns_date_is_invalid_if_date_is_empty(self) -> None:
        headers = self.generate_headers(date_str='')
        request_mock = self.get_request_mock(headers=headers)

        sig_verification = SignatureVerification.get_signature(request_mock)

        assert sig_verification.is_date_invalid() is True

    def test_it_returns_date_is_invalid_if_date_format_is_invalid(
        self,
    ) -> None:
        date_str = datetime.utcnow().strftime('%d %b %Y %H:%M:%S')
        headers = self.generate_headers(date_str=date_str)
        request_mock = self.get_request_mock(headers=headers)

        sig_verification = SignatureVerification.get_signature(request_mock)

        assert sig_verification.is_date_invalid() is True

    def test_it_returns_date_is_invalid_if_delay_exceeds_limit(self) -> None:
        headers = self.generate_headers(
            date=datetime.utcnow() - timedelta(seconds=VALID_DATE_DELTA + 1)
        )
        request_mock = self.get_request_mock(headers=headers)

        sig_verification = SignatureVerification.get_signature(request_mock)

        assert sig_verification.is_date_invalid() is True

    def test_it_returns_date_is_valid_if_dela_is_below_limit(self) -> None:
        headers = self.generate_headers(
            date=datetime.utcnow() - timedelta(seconds=VALID_DATE_DELTA - 1)
        )
        request_mock = self.get_request_mock(headers=headers)

        sig_verification = SignatureVerification.get_signature(request_mock)

        assert sig_verification.is_date_invalid() is False


class TestGetActorPublicKey(SignatureVerificationTestCase):
    def test_it_calls_requests_with_key_id(self) -> None:
        key_id = random_string()
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(self.generate_headers(key_id=key_id))
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response()

            sig_verification.get_actor_public_key()

            requests_mock.assert_called_with(
                key_id, headers={'Accept': 'application/activity+json'}
            )

    def test_it_returns_none_if_requests_returns_error_status_code(
        self,
    ) -> None:
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(self.generate_headers())
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(status_code=404)

            public_key = sig_verification.get_actor_public_key()

            assert public_key is None

    def test_it_returns_none_if_requests_returns_invalid_actor_dict(
        self,
    ) -> None:
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(self.generate_headers())
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200, content={random_string(): random_string()}
            )

            public_key = sig_verification.get_actor_public_key()

            assert public_key is None

    def test_it_returns_public_key(self) -> None:
        public_key = random_string()
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(self.generate_headers())
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content={'publicKey': {'publicKeyPem': public_key}},
            )

            key = sig_verification.get_actor_public_key()

            assert key == public_key


class TestSignatureVerify(SignatureVerificationTestCase):
    def test_verify_raises_error_if_signature_is_invalid_due_to_keys_update(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        actor_1.generate_keys()
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                )
            )
        )
        # update actor keys
        actor_1.generate_keys()
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            with pytest.raises(InvalidSignatureException):
                sig_verification.verify()

    def test_verify_raises_error_if_header_date_is_invalid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        actor_1.generate_keys()
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                    date_str='',
                )
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            with pytest.raises(InvalidSignatureException):
                sig_verification.verify()

    def test_verify_raises_error_if_public_key_is_invalid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        actor_1.generate_keys()
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                )
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(status_code=404)

            with pytest.raises(InvalidSignatureException):
                sig_verification.verify()

    def test_verify_does_not_raise_error_if_signature_is_valid(
        self, app_with_federation: Flask, actor_1: Actor
    ) -> None:
        actor_1.generate_keys()
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                )
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            sig_verification.verify()

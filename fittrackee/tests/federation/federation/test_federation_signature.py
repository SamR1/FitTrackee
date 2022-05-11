import base64
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from fittrackee.federation.constants import AP_CTX
from fittrackee.federation.exceptions import InvalidSignatureException
from fittrackee.federation.models import Actor
from fittrackee.federation.signature import (
    VALID_DATE_DELTA,
    VALID_SIG_DATE_FORMAT,
    SignatureVerification,
    generate_digest,
    generate_signature,
    generate_signature_header,
)
from fittrackee.users.models import User

from ...utils import generate_response, get_date_string, random_string

TEST_ACTIVITY = {
    '@context': AP_CTX,
    'id': random_string(),
    'type': random_string(),
    'actor': random_string(),
    'object': random_string(),
}


class TestGenerateDigest:
    def test_it_returns_digest_with_default_algorithm(self) -> None:
        assert generate_digest(TEST_ACTIVITY).startswith('SHA-256=')

    def test_it_returns_digest_with_given_algorithm(self) -> None:
        assert generate_digest(TEST_ACTIVITY, 'rsa-sha512').startswith(
            'SHA-512='
        )


class SignatureVerificationTestCase:
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
        algorithm: Optional[str] = None,
        digest: Optional[str] = None,
    ) -> Dict:
        key_id = key_id if key_id else random_string()
        signature = signature if signature else self.random_signature()
        signature_headers = f'keyId="{key_id}",'
        if algorithm is not None:
            signature_headers += f'algorithm={algorithm},'
            digest = digest if digest else random_string()
        signature_headers += (
            'headers="(request-target) host date digest",signature="'
            + signature
            + '"'
        )
        signature_headers = (
            f'keyId="{key_id}",algorithm={algorithm},headers="(request-target)'
            f' host date digest",signature="' + signature + '"'
        )
        if date_str is None:
            date_str = get_date_string(
                date_format=VALID_SIG_DATE_FORMAT, date=date
            )
        headers = {
            'Host': host if host else random_string(),
            'Date': date_str,
            'Signature': signature_headers,
            'Content-Type': 'application/ld+json',
        }
        if digest:
            headers['Digest'] = digest
        return headers

    def generate_valid_headers(
        self,
        host: str,
        actor: Actor,
        activity: Dict,
        date_str: Optional[str] = None,
    ) -> Dict:
        if date_str is None:
            now = datetime.utcnow()
            date_str = now.strftime(VALID_SIG_DATE_FORMAT)
        digest = generate_digest(activity)
        signed_header = generate_signature_header(
            host, '/inbox', date_str, actor, digest
        )
        return self.generate_headers(
            key_id=actor.activitypub_id,
            signature=signed_header,
            date_str=date_str,
            host=host,
            algorithm='rsa-sha256',
            digest=digest,
        )

    @staticmethod
    def _generate_signature_header_without_digest(
        host: str, path: str, date_str: str, actor: Actor
    ) -> str:
        signed_string = (
            f'(request-target): post {path}\nhost: {host}\ndate: {date_str}'
        )
        signature = generate_signature(actor.private_key, signed_string)
        return (
            f'keyId="{actor.activitypub_id}#main-key",'
            'headers="(request-target) host date",'
            f'signature="' + signature.decode() + '"'
        )

    def generate_valid_headers_without_digest(
        self,
        host: str,
        actor: Actor,
        date_str: Optional[str] = None,
    ) -> Dict:
        if date_str is None:
            now = datetime.utcnow()
            date_str = now.strftime(VALID_SIG_DATE_FORMAT)
        signed_header = self._generate_signature_header_without_digest(
            host, '/inbox', date_str, actor
        )
        return self.generate_headers(
            key_id=actor.activitypub_id,
            signature=signed_header,
            date_str=date_str,
            host=host,
        )

    @staticmethod
    def get_request_mock(
        headers: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> MagicMock:
        request_mock = MagicMock()
        request_mock.headers = headers if headers else {}
        request_mock.path = '/inbox'
        request_mock.data = json.dumps(data if data else {}).encode()
        return request_mock

    @staticmethod
    def get_activity(actor: Optional[Actor] = None) -> Dict:
        return {
            '@context': AP_CTX,
            'id': random_string(),
            'type': random_string(),
            'actor': (
                random_string() if actor is None else actor.activitypub_id
            ),
            'object': random_string(),
        }


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
                'headers="(request-target) host date digest",'
                f'signature="{random_string()}"',
            ),
            (
                'missing headers',
                f'keyId="{random_string()}", signature="{random_string()}"',
            ),
            (
                'missing signature',
                f'keyId="{random_string()}",'
                'headers="(request-target) host date digest"',
            ),
        ],
    )
    def test_it_raises_error_if_a_signature_key_is_missing(
        self, input_description: str, input_signature_headers: str
    ) -> None:
        request_with_empty_headers = self.get_request_mock(
            headers={
                'Host': random_string(),
                'Date': get_date_string(date_format=VALID_SIG_DATE_FORMAT),
                'Signature': input_signature_headers,
            }
        )

        with pytest.raises(InvalidSignatureException):
            SignatureVerification.get_signature(request_with_empty_headers)

    def test_it_instantiates_signature_verification(self) -> None:
        key_id = random_string()
        signature = self.random_signature()
        algorithm = 'rsa-sha256'
        signature_headers = (
            f'keyId="{key_id}",algorithm={algorithm},'
            'headers="(request-target) host date digest",'
            f'signature="' + signature + '"'
        )
        date_str = get_date_string(date_format=VALID_SIG_DATE_FORMAT)
        activity = {'foo': 'bar'}
        digest = generate_digest(activity)
        valid_request_mock = self.get_request_mock(
            headers={
                'Host': random_string(),
                'Date': date_str,
                'Digest': digest,
                'Signature': signature_headers,
            }
        )

        sig_verification = SignatureVerification.get_signature(
            valid_request_mock
        )

        assert sig_verification.request == valid_request_mock
        assert sig_verification.date_str == date_str
        assert sig_verification.key_id == key_id
        assert sig_verification.headers == '(request-target) host date digest'
        assert sig_verification.signature == base64.b64decode(signature)
        assert sig_verification.algorithm == algorithm
        assert sig_verification.digest == digest


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


class TestSignatureDigestVerification(SignatureVerificationTestCase):
    @pytest.mark.parametrize(
        'input_description,input_digest',
        [
            (
                'invalid digest',
                random_string(),
            ),
            (
                'mismatched digest (different data)',
                generate_digest({"foo": "bar"}),
            ),
            (
                'mismatched digest (different algo)',
                generate_digest(TEST_ACTIVITY, algorithm='rsa-sha512'),
            ),
        ],
    )
    def test_verify_raises_error_if_http_digest_is_invalid(
        self,
        input_description: str,
        input_digest: str,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    date_str=datetime.utcnow().strftime(VALID_SIG_DATE_FORMAT),
                    algorithm='rsa-sha256',
                    digest=input_digest,
                ),
                data=TEST_ACTIVITY,
            )
        )

        with pytest.raises(
            InvalidSignatureException, match='invalid HTTP digest'
        ):
            sig_verification.verify_digest()

    @pytest.mark.parametrize(
        'input_description,input_algorithm',
        [('SHA256', 'rsa-sha256'), ('SHA512', 'rsa-sha512')],
    )
    def test_verify_do_not_raise_error_if_http_digest_is_valid(
        self,
        input_description: str,
        input_algorithm: str,
        app_with_federation: Flask,
        user_1: User,
    ) -> None:
        activity = self.get_activity(actor=user_1.actor)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    date_str=datetime.utcnow().strftime(VALID_SIG_DATE_FORMAT),
                    algorithm=input_algorithm,
                    digest=generate_digest(activity, input_algorithm),
                ),
                data=activity,
            )
        )

        sig_verification.verify_digest()


class TestSignatureVerify(SignatureVerificationTestCase):
    @pytest.mark.disable_autouse_generate_keys
    def test_it_raises_error_if_header_actor_is_different_from_activity_actor(
        self, app_with_federation: Flask, user_1: User, user_2: User
    ) -> None:
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=user_1.actor,
                    date_str=datetime.utcnow().strftime(VALID_SIG_DATE_FORMAT),
                    activity=self.get_activity(actor=user_2.actor),
                )
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=user_1.actor.serialize(),
            )

            with pytest.raises(
                InvalidSignatureException, match='invalid actor'
            ):
                sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_raises_error_if_header_date_is_invalid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        activity = self.get_activity(actor=actor_1)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                    date_str='',
                    activity=self.get_activity(actor=actor_1),
                ),
                data=activity,
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            with pytest.raises(
                InvalidSignatureException, match='invalid date header'
            ):
                sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_raises_error_if_public_key_is_invalid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        activity = self.get_activity(actor=actor_1)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                    activity=activity,
                ),
                data=activity,
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(status_code=404)

            with pytest.raises(
                InvalidSignatureException, match='invalid public key'
            ):
                sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_raises_error_if_algorithm_is_not_supported(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        algorithm = random_string()
        activity = self.get_activity(actor=actor_1)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    key_id=actor_1.activitypub_id,
                    date_str=datetime.utcnow().strftime(VALID_SIG_DATE_FORMAT),
                    algorithm=algorithm,
                    digest=generate_digest(activity),
                ),
                data=activity,
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            with pytest.raises(
                InvalidSignatureException, match='unsupported algorithm'
            ):
                sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_raises_error_if_http_digest_is_invalid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    key_id=actor_1.activitypub_id,
                    date_str=datetime.utcnow().strftime(VALID_SIG_DATE_FORMAT),
                    algorithm='rsa-sha256',
                    digest=random_string(),
                ),
                data=self.get_activity(actor=actor_1),
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            with pytest.raises(
                InvalidSignatureException, match='invalid HTTP digest'
            ):
                sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_raises_error_if_signature_is_invalid_due_to_keys_update(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        activity = self.get_activity(actor=actor_1)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                    activity=activity,
                ),
                data=activity,
            )
        )
        # update actor keys
        actor_1.generate_keys()
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            with pytest.raises(
                InvalidSignatureException, match='verification failed'
            ):
                sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_does_not_raise_error_if_signature_is_valid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        activity = self.get_activity(actor=actor_1)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers(
                    host=app_with_federation.config['AP_DOMAIN'],
                    actor=actor_1,
                    activity=activity,
                ),
                data=activity,
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            sig_verification.verify()

    @pytest.mark.disable_autouse_generate_keys
    def test_verify_does_not_raise_error_if_signature_without_digest_is_valid(
        self, app_with_federation: Flask, user_1: User
    ) -> None:
        actor_1 = user_1.actor
        activity = self.get_activity(actor=actor_1)
        sig_verification = SignatureVerification.get_signature(
            self.get_request_mock(
                self.generate_valid_headers_without_digest(
                    host=app_with_federation.config['AP_DOMAIN'], actor=actor_1
                ),
                data=activity,
            )
        )
        with patch.object(requests, 'get') as requests_mock:
            requests_mock.return_value = generate_response(
                status_code=200,
                content=actor_1.serialize(),
            )

            sig_verification.verify()

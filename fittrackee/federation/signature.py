"""
inspired by bookwyrm signatures.py
https://github.com/bookwyrm-social/bookwyrm
"""
import base64
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional

import requests
from Crypto.Hash import SHA256  # nosec B413
from Crypto.PublicKey import RSA  # nosec B413
from Crypto.Signature import pkcs1_15  # nosec B413
from flask import Request

from fittrackee import appLog

from .exceptions import InvalidSignatureException
from .models import Actor

VALID_DATE_DELTA = 30  # in seconds
VALID_SIG_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
VALID_SIG_KEYS = ['keyId', 'headers', 'signature']
SUPPORTED_ALGORITHMS = {
    'rsa-sha256': {'algorithm': 'SHA-256', 'hash_function': hashlib.sha256},
    'rsa-sha512': {'algorithm': 'SHA-512', 'hash_function': hashlib.sha512},
}
DEFAULT_ALGORITHM = 'rsa-sha256'


def generate_digest(activity: Dict, algorithm: Optional[str] = None) -> str:
    algorithm_dict = SUPPORTED_ALGORITHMS[
        DEFAULT_ALGORITHM if algorithm is None else algorithm
    ]
    digest = base64.b64encode(
        algorithm_dict['hash_function'](  # type: ignore
            json.dumps(activity).encode()
        ).digest()
    ).decode()
    return f"{algorithm_dict['algorithm']}={digest}"


def generate_signature(private_key: str, signed_string: str) -> bytes:
    key = RSA.import_key(private_key)
    key_signer = pkcs1_15.new(key)
    encoded_string = signed_string.encode('utf-8')
    h = SHA256.new(encoded_string)
    return base64.b64encode(key_signer.sign(h))


def generate_signature_header(
    host: str, path: str, date_str: str, actor: Actor, digest: str
) -> str:
    signed_string = (
        f'(request-target): post {path}\nhost: {host}\ndate: {date_str}\n'
        f'digest: {digest}'
    )
    signature = generate_signature(actor.private_key, signed_string)
    return (
        f'keyId="{actor.activitypub_id}#main-key",'
        f'algorithm={DEFAULT_ALGORITHM},'
        'headers="(request-target) host date digest",'
        f'signature="' + signature.decode() + '"'
    )


class SignatureVerification:
    def __init__(self, request: Request, signature_dict: Dict):
        self.request = request
        self.host = request.headers.get('Host', 'undefined')
        self.date_str = request.headers.get('Date')
        self.key_id = signature_dict['keyId']
        self.headers = signature_dict['headers']
        self.signature = base64.b64decode(signature_dict['signature'])
        self.algorithm = signature_dict.get('algorithm', DEFAULT_ALGORITHM)
        self.digest = request.headers.get('Digest')

    @classmethod
    def get_signature(cls, request: Request) -> 'SignatureVerification':
        signature_dict = {}
        host = request.headers.get('Host', 'undefined')
        try:
            header_signature = request.headers['Signature'].split(',')
            for part in header_signature:
                key, value = part.split('=', 1)
                signature_dict[key] = value.strip('"')
        except Exception as e:
            appLog.error(f'Invalid signature headers: {e} (host: {host}).')
            raise InvalidSignatureException()

        keys_list = list(signature_dict.keys())
        if not all(key in keys_list for key in VALID_SIG_KEYS):
            appLog.error(
                'Invalid signature headers: missing keys, expected: '
                f'{VALID_SIG_KEYS}, got: {keys_list} '
                f'(host: {host}).'
            )
            raise InvalidSignatureException()

        return cls(request, signature_dict)

    def get_actor_public_key(self) -> Optional[str]:
        response = requests.get(
            self.key_id,
            headers={'Accept': 'application/activity+json'},
        )
        if response.status_code >= 400:
            return None
        try:
            public_key = response.json()['publicKey']['publicKeyPem']
        except Exception:
            return None
        return public_key

    def is_date_invalid(self) -> bool:
        if not self.date_str:
            return True
        try:
            date = datetime.strptime(self.date_str, VALID_SIG_DATE_FORMAT)
        except ValueError:
            return True
        delta = datetime.utcnow() - date
        return delta.total_seconds() > VALID_DATE_DELTA

    def log_and_raise_error(self, error: str) -> None:
        appLog.error(f'Invalid signature: {error} (host: {self.host}).')
        raise InvalidSignatureException(error)

    def verify_digest(self) -> None:
        if self.algorithm not in SUPPORTED_ALGORITHMS.keys():
            self.log_and_raise_error('unsupported algorithm')
        expected_algorithm = SUPPORTED_ALGORITHMS[self.algorithm]['algorithm']
        hash_function = SUPPORTED_ALGORITHMS[self.algorithm]['hash_function']

        try:
            if not self.digest:
                raise Exception('No digest')
            algorithm, digest = self.digest.split('=', 1)
            if algorithm != expected_algorithm:
                raise Exception('Algorithm mismatch')
            expected = hash_function(  # type: ignore
                self.request.data
            ).digest()
            if base64.b64decode(digest) != expected:
                raise Exception()
        except Exception:
            self.log_and_raise_error('invalid HTTP digest')

    def header_actor_is_payload_actor(self) -> bool:
        activity = json.loads(self.request.data.decode())
        return self.key_id.replace('#main-key', '') == activity.get('actor')

    def verify(self) -> None:
        if not self.header_actor_is_payload_actor():
            self.log_and_raise_error('invalid actor')

        public_key = self.get_actor_public_key()
        if not public_key:
            self.log_and_raise_error('invalid public key')

        if self.is_date_invalid():
            self.log_and_raise_error('invalid date header')

        comparison = []
        for headers_part in self.headers.split(' '):
            if headers_part == '(request-target)':
                comparison.append(
                    '(request-target): post %s' % self.request.path
                )
            else:
                if headers_part == 'digest':
                    self.verify_digest()
                comparison.append(
                    "%s: %s"
                    % (
                        headers_part,
                        self.request.headers[headers_part.capitalize()],
                    )
                )
        comparison_string: str = '\n'.join(comparison)

        signer = pkcs1_15.new(RSA.import_key(public_key))  # type: ignore
        digest = SHA256.new()
        digest.update(comparison_string.encode())
        try:
            signer.verify(digest, self.signature)
        except ValueError:
            self.log_and_raise_error('verification failed')

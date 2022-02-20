import base64
from datetime import datetime
from typing import Dict, Optional

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from flask import Request

from fittrackee import appLog

from .exceptions import InvalidSignatureException

VALID_DATE_DELTA = 30  # in seconds
VALID_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
VALID_SIG_KEYS = ['keyId', 'headers', 'signature']


class SignatureVerification:
    def __init__(self, request: Request, signature_dict: Dict):
        self.request = request
        self.host = request.headers.get('Host', 'undefined')
        self.date_str = request.headers.get('Date')
        self.key_id = signature_dict['keyId']
        self.headers = signature_dict['headers']
        self.signature = base64.b64decode(signature_dict['signature'])

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

        if list(signature_dict.keys()) != VALID_SIG_KEYS:
            appLog.error(
                f'Invalid signature headers: invalid keys (host: {host}).'
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
            date = datetime.strptime(self.date_str, VALID_DATE_FORMAT)
        except ValueError:
            return True
        delta = datetime.utcnow() - date
        return delta.total_seconds() > VALID_DATE_DELTA

    def verify(self) -> None:
        public_key = self.get_actor_public_key()
        if not public_key:
            appLog.error(
                f'Invalid signature: invalid public key (host: {self.host}).'
            )
            raise InvalidSignatureException()

        if self.is_date_invalid():
            appLog.error(
                f'Invalid signature: invalid date header (host: {self.host}).'
            )
            raise InvalidSignatureException()

        comparison = []
        for headers_part in self.headers.split(' '):
            if headers_part == '(request-target)':
                comparison.append(
                    '(request-target): post %s' % self.request.path
                )
            else:
                comparison.append(
                    "%s: %s"
                    % (
                        headers_part,
                        self.request.headers[headers_part.capitalize()],
                    )
                )
        comparison_string: str = '\n'.join(comparison)

        signer = pkcs1_15.new(RSA.import_key(public_key))
        digest = SHA256.new()
        digest.update(comparison_string.encode())
        try:
            signer.verify(digest, self.signature)
        except ValueError:
            appLog.error(f'Invalid signature (host: {self.host}).')
            raise InvalidSignatureException()

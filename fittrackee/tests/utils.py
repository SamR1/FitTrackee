import random
import string
from json import loads
from typing import Dict, Optional
from uuid import uuid4

from flask import json as flask_json

from fittrackee.workouts.utils.short_id import encode_uuid


def random_string(
    length: Optional[int] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
) -> str:
    if length is None:
        length = 10
    random_str = ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )
    return (
        f'{"" if prefix is None else prefix}'
        f'{random_str}'
        f'{"" if suffix is None else suffix}'
    )


def random_domain() -> str:
    return random_string(prefix='https://', suffix='.com')


def random_email() -> str:
    return random_string(suffix='@example.com')


def random_short_id() -> str:
    return encode_uuid(uuid4())


def jsonify_dict(data: Dict) -> Dict:
    return loads(flask_json.dumps(data))


TEST_OAUTH_CLIENT_METADATA = {
    'client_name': random_string(),
    'client_uri': random_domain(),
    'redirect_uris': [random_domain()],
    'scope': 'read write',
}

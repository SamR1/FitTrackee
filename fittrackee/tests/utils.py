import random
import string
from json import loads
from typing import Dict, Optional

from flask import json as flask_json


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


def random_email() -> str:
    return random_string(suffix='@example.com')


def jsonify_dict(data: Dict) -> Dict:
    return loads(flask_json.dumps(data))

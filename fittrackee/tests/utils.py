import random
import string
from datetime import datetime
from json import dumps, loads
from typing import Dict, Optional, Union
from uuid import uuid4

from flask import json as flask_json
from requests import Response

from fittrackee import db
from fittrackee.users.models import FollowRequest, User
from fittrackee.utils import encode_uuid


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
    return random_string(suffix='.social')


def get_date_string(
    date_format: str,
    date: Optional[datetime] = None,
) -> str:
    date = date if date else datetime.utcnow()
    return date.strftime(date_format)


def random_email() -> str:
    return random_string(suffix='@example.com')


def random_int(min_value: int = 0, max_value: int = 999999) -> int:
    return random.randint(min_value, max_value)


def random_short_id() -> str:
    return encode_uuid(uuid4())


def generate_response(
    content: Optional[Union[str, Dict]] = None,
    status_code: Optional[int] = None,
) -> Response:
    content = content if content else {}
    response = Response()
    response._content = (
        dumps(content).encode()
        if isinstance(content, dict)
        else content.encode()
    )
    response.status_code = status_code if status_code else 200
    return response


def generate_follow_request(follower: User, followed: User) -> FollowRequest:
    follow_request = FollowRequest(
        follower_user_id=follower.id, followed_user_id=followed.id
    )
    db.session.add(follow_request)
    db.session.commit()
    return follow_request


def jsonify_dict(data: Dict) -> Dict:
    return loads(flask_json.dumps(data))


TEST_OAUTH_CLIENT_METADATA = {
    'client_name': random_string(),
    'client_uri': random_domain(),
    'redirect_uris': [random_domain()],
    'scope': 'profile:read workouts:read',
}

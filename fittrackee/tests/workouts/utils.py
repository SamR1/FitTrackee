import json
from io import BytesIO
from typing import Tuple
from uuid import uuid4

from fittrackee.workouts.utils_id import encode_uuid
from flask import Flask


def get_random_short_id() -> str:
    return encode_uuid(uuid4())


def post_an_workout(app: Flask, gpx_file: str) -> Tuple[str, str]:
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    token = json.loads(resp_login.data.decode())['auth_token']
    response = client.post(
        '/api/workouts',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data='{"sport_id": 1}',
        ),
        headers=dict(
            content_type='multipart/form-data', Authorization=f'Bearer {token}'
        ),
    )
    data = json.loads(response.data.decode())
    return token, data['data']['workouts'][0]['id']

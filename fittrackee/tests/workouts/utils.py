import json
from io import BytesIO
from typing import Optional, Tuple

from flask import Flask


def post_a_workout(
    app: Flask,
    gpx_file: str,
    notes: Optional[str] = None,
    description: Optional[str] = None,
) -> Tuple[str, str]:
    client = app.test_client()
    resp_login = client.post(
        '/api/auth/login',
        data=json.dumps(dict(email='test@test.com', password='12345678')),
        content_type='application/json',
    )
    token = json.loads(resp_login.data.decode())['auth_token']
    workout_data = '{"sport_id": 1'
    if notes is not None:
        workout_data += f', "notes": "{notes}"'
    if description is not None:
        workout_data += f', "description": "{description}"'
    workout_data += '}'
    response = client.post(
        '/api/workouts',
        data=dict(
            file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
            data=workout_data,
        ),
        headers=dict(
            content_type='multipart/form-data', Authorization=f'Bearer {token}'
        ),
    )
    data = json.loads(response.data.decode())
    return token, data['data']['workouts'][0]['id']

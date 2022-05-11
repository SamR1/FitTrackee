import json
from io import BytesIO
from typing import Optional, Tuple

from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel


def post_a_workout(
    app: Flask,
    gpx_file: str,
    notes: Optional[str] = None,
    workout_visibility: Optional[PrivacyLevel] = None,
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
    if workout_visibility is not None:
        workout_data += f', "workout_visibility": "{workout_visibility.value}"'
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

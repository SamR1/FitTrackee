import json
from io import BytesIO
from typing import Optional, Tuple

from flask import Flask

from fittrackee import db
from fittrackee.administration.models import AdminAction
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.models import Workout


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


def add_follower(user: User, follower: User) -> None:
    follower.send_follow_request_to(user)
    user.approves_follow_request_from(follower)


class WorkoutMixin:
    @staticmethod
    def create_admin_workout_suspension_action(
        admin: User, user: User, workout: Workout
    ) -> AdminAction:
        admin_action = AdminAction(
            action_type="workout_suspension",
            admin_user_id=admin.id,
            workout_id=workout.id,
            user_id=user.id,
        )
        db.session.add(admin_action)
        return admin_action

import json
import os

import pytest
from flask import Flask

from fittrackee.files import get_absolute_file_path
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ..test_case_mixins import ApiTestCaseMixin
from .utils import get_random_short_id, post_a_workout


def get_gpx_filepath(workout_id: int) -> str:
    workout = Workout.query.filter_by(id=workout_id).first()
    return workout.gpx


class TestDeleteWorkoutWithGpx(ApiTestCaseMixin):
    def test_it_deletes_workout_with_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        assert response.status_code == 204

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                PrivacyLevel.FOLLOWERS,
                403,
            ),
            ('workout visibility: public', PrivacyLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_followed_user_user(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)

        _, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=input_workout_visibility
        )
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email=user_2.email, password='87654321')),
            content_type='application/json',
        )

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                PrivacyLevel.FOLLOWERS,
                404,
            ),
            ('workout visibility: public', PrivacyLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_different_user(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=input_workout_visibility
        )
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email=user_2.email, password='87654321')),
            content_type='application/json',
        )

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE),
            (
                'workout visibility: followers_only',
                PrivacyLevel.FOLLOWERS,
            ),
            ('workout visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_401_when_no_authenticated(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=input_workout_visibility
        )
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
        )

        assert response.status_code == 401

    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.delete(
            f'/api/workouts/{get_random_short_id()}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']

    def test_it_returns_500_when_deleting_a_workout_with_gpx_invalid_file(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()
        gpx_filepath = get_gpx_filepath(1)
        gpx_filepath = get_absolute_file_path(gpx_filepath)
        os.remove(gpx_filepath)

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'error, please try again or contact the administrator'
            in data['message']
        )


class TestDeleteWorkoutWithoutGpx(ApiTestCaseMixin):
    def test_it_deletes_a_workout_wo_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        assert response.status_code == 204

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                PrivacyLevel.FOLLOWERS,
                403,
            ),
            ('workout visibility: public', PrivacyLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_followed_user_user(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email=user_2.email, password='87654321')),
            content_type='application/json',
        )
        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                PrivacyLevel.FOLLOWERS,
                404,
            ),
            ('workout visibility: public', PrivacyLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_different_user(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email=user_2.email, password='87654321')),
            content_type='application/json',
        )
        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE),
            (
                'workout visibility: followers_only',
                PrivacyLevel.FOLLOWERS,
            ),
            ('workout visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_401_when_no_authenticated(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
        )

        assert response.status_code == 401

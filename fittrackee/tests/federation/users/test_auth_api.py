import json

import pytest
from flask import Flask

from fittrackee.tests.mixins import ApiTestCaseMixin
from fittrackee.users.models import User
from fittrackee.visibility_levels import VisibilityLevel


def assert_actor_is_created(app: Flask) -> None:
    client = app.test_client()
    username = 'justatest'

    client.post(
        '/api/auth/register',
        data=json.dumps(
            dict(
                username=username,
                email='test@test.com',
                password='12345678',
                password_conf='12345678',
                accepted_policy=True,
            )
        ),
        content_type='application/json',
    )

    user = User.query.filter_by(username=username).first()
    assert user.actor.preferred_username == username
    assert user.actor.public_key is not None
    assert user.actor.private_key is not None


class TestUserRegistration:
    def test_it_creates_actor_on_user_registration(
        self, app_with_federation: Flask
    ) -> None:
        assert_actor_is_created(app=app_with_federation)

    def test_local_user_can_register_if_remote_user_exists_with_same_username(
        self, app_with_federation: Flask, remote_user: User
    ) -> None:
        client = app_with_federation.test_client()

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username=remote_user.username,
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678',
                    accepted_policy=True,
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200
        created_user = User.query.filter(
            User.username == remote_user.username,
            User.is_remote == False,  # noqa
        ).first()
        assert created_user.id != remote_user.id


class TestUserPreferencesUpdate(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        'input_map_visibility,input_analysis_visibility,'
        'input_workout_visibility,expected_map_visibility,'
        'expected_analysis_visibility',
        [
            (
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
                VisibilityLevel.PUBLIC,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
            ),
            (
                VisibilityLevel.PRIVATE,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS_AND_REMOTE,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_it_updates_user_preferences_with_remote_level(
        self,
        app_with_federation: Flask,
        user_1: User,
        input_map_visibility: VisibilityLevel,
        input_analysis_visibility: VisibilityLevel,
        input_workout_visibility: VisibilityLevel,
        expected_map_visibility: VisibilityLevel,
        expected_analysis_visibility: VisibilityLevel,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_federation, user_1.email
        )

        response = client.post(
            '/api/auth/profile/edit/preferences',
            content_type='application/json',
            data=json.dumps(
                dict(
                    timezone='America/New_York',
                    weekm=True,
                    language='fr',
                    imperial_units=True,
                    display_ascent=True,
                    date_format='MM/dd/yyyy',
                    start_elevation_at_zero=False,
                    use_raw_gpx_speed=True,
                    manually_approves_followers=False,
                    hide_profile_in_users_directory=False,
                    use_dark_mode=True,
                    map_visibility=input_map_visibility.value,
                    analysis_visibility=input_analysis_visibility.value,
                    workouts_visibility=input_workout_visibility.value,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['map_visibility'] == expected_map_visibility.value
        assert (
            data['data']['analysis_visibility']
            == expected_analysis_visibility.value
        )
        assert (
            data['data']['workouts_visibility']
            == input_workout_visibility.value
        )

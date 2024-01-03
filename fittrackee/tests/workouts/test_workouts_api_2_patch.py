import json
from datetime import datetime
from typing import Dict
from uuid import uuid4

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict
from .utils import post_a_workout


def assert_workout_data_with_gpx(
    data: Dict, sport_id: int, user: User
) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['workouts'][0]['workout_date']
    )
    assert data['data']['workouts'][0]['user'] == jsonify_dict(
        user.serialize()
    )
    assert '0:04:10' == data['data']['workouts'][0]['duration']
    assert data['data']['workouts'][0]['ascent'] == 0.4
    assert data['data']['workouts'][0]['ave_speed'] == 4.61
    assert data['data']['workouts'][0]['descent'] == 23.4
    assert data['data']['workouts'][0]['distance'] == 0.32
    assert data['data']['workouts'][0]['max_alt'] == 998.0
    assert data['data']['workouts'][0]['max_speed'] == 5.12
    assert data['data']['workouts'][0]['min_alt'] == 975.0
    assert data['data']['workouts'][0]['moving'] == '0:04:10'
    assert data['data']['workouts'][0]['pauses'] is None
    assert data['data']['workouts'][0]['with_gpx'] is True

    records = data['data']['workouts'][0]['records']
    assert len(records) == 5
    assert records[0]['sport_id'] == sport_id
    assert records[0]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[0]['record_type'] == 'MS'
    assert records[0]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == 5.12
    assert records[1]['sport_id'] == sport_id
    assert records[1]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[1]['record_type'] == 'LD'
    assert records[1]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == '0:04:10'
    assert records[2]['sport_id'] == sport_id
    assert records[2]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[2]['record_type'] == 'HA'
    assert records[2]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['sport_id'] == sport_id
    assert records[3]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[3]['record_type'] == 'FD'
    assert records[3]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 0.32
    assert records[4]['sport_id'] == sport_id
    assert records[4]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[4]['record_type'] == 'AS'
    assert records[4]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[4]['value'] == 4.61


class TestEditWorkoutWithGpx(ApiTestCaseMixin):
    def test_it_updates_title_for_a_workout_with_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title="Workout test")),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert sport_2_running.id == data['data']['workouts'][0]['sport_id']
        assert data['data']['workouts'][0]['title'] == 'Workout test'
        assert_workout_data_with_gpx(data, sport_2_running.id, user_1)

    @pytest.mark.parametrize(
        'input_description,input_notes',
        [
            ('empty notes', ''),
            ('short notes', 'test workout'),
            ('notes with special characters', 'test \nworkout'),
        ],
    )
    def test_it_adds_notes_to_a_workout_with_gpx(
        self,
        app: Flask,
        input_description: str,
        input_notes: str,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(notes=input_notes)),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == input_notes

    def test_it_empties_workout_notes(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(
            app, gpx_file, notes=uuid4().hex
        )
        client = app.test_client()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(notes='')),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == ''

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title='Workout test')),
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title="Workout test")),
            headers=dict(Authorization=f'Bearer {auth_token}'),
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

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title="Workout test")),
        )

        assert response.status_code == 401

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=PrivacyLevel.PRIVATE
        )
        client = app.test_client()
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title="Workout test")),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        self.assert_403(response)

    def test_it_updates_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2)),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert sport_2_running.id == data['data']['workouts'][0]['sport_id']
        assert data['data']['workouts'][0]['title'] == 'just a workout'
        assert_workout_data_with_gpx(data, sport_2_running.id, user_1)

    def test_it_returns_400_if_payload_is_empty(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        self.assert_400(response)

    def test_it_raises_500_if_sport_does_not_exist(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2)),
            headers=dict(Authorization=f'Bearer {token}'),
        )

        self.assert_500(response)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            data=dict(),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestEditWorkoutWithoutGpx(ApiTestCaseMixin):
    def test_it_updates_a_workout_wo_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-15 15:05',
                    distance=8,
                    title='Workout test',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            data['data']['workouts'][0]['workout_date']
            == 'Tue, 15 May 2018 15:05:00 GMT'
        )
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert data['data']['workouts'][0]['sport_id'] == sport_2_running.id
        assert data['data']['workouts'][0]['duration'] == '1:00:00'
        assert data['data']['workouts'][0]['title'] == 'Workout test'
        assert data['data']['workouts'][0]['ascent'] is None
        assert data['data']['workouts'][0]['ave_speed'] == 8.0
        assert data['data']['workouts'][0]['descent'] is None
        assert data['data']['workouts'][0]['distance'] == 8.0
        assert data['data']['workouts'][0]['max_alt'] is None
        assert data['data']['workouts'][0]['max_speed'] == 8.0
        assert data['data']['workouts'][0]['min_alt'] is None
        assert data['data']['workouts'][0]['moving'] == '1:00:00'
        assert data['data']['workouts'][0]['pauses'] is None
        assert data['data']['workouts'][0]['with_gpx'] is False
        assert data['data']['workouts'][0]['map'] is None
        assert data['data']['workouts'][0]['weather_start'] is None
        assert data['data']['workouts'][0]['weather_end'] is None
        assert data['data']['workouts'][0]['notes'] is None

        records = data['data']['workouts'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == sport_2_running.id
        assert records[0]['workout_id'] == workout_short_id
        assert records[0]['record_type'] == 'MS'
        assert records[0]['workout_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[0]['value'] == 8.0
        assert records[1]['sport_id'] == sport_2_running.id
        assert records[1]['workout_id'] == workout_short_id
        assert records[1]['record_type'] == 'LD'
        assert records[1]['workout_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == sport_2_running.id
        assert records[2]['workout_id'] == workout_short_id
        assert records[2]['record_type'] == 'FD'
        assert records[2]['workout_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[2]['value'] == 8.0
        assert records[3]['sport_id'] == sport_2_running.id
        assert records[3]['workout_id'] == workout_short_id
        assert records[3]['record_type'] == 'AS'
        assert records[3]['workout_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[3]['value'] == 8.0

    @pytest.mark.parametrize(
        'input_description,input_notes',
        [
            ('empty notes', ''),
            ('short notes', 'test workout'),
            ('notes with special characters', 'test \nworkout'),
        ],
    )
    def test_it_adds_notes_to_a_workout_wo_gpx(
        self,
        app: Flask,
        input_description: str,
        input_notes: str,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(notes=input_notes)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == input_notes

    def test_it_empties_workout_notes(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        workout_cycling_user_1.notes = uuid4().hex
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(notes='')),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == ''

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
    def test_returns_403_when_editing_a_workout_wo_gpx_from_followed_user(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_2.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-15 15:05',
                    distance=8,
                    title='Workout test',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
    def test_returns_403_when_editing_a_workout_wo_gpx_from_different_user(
        self,
        input_desc: str,
        input_workout_visibility: PrivacyLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_2.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-15 15:05',
                    distance=8,
                    title='Workout test',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
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

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-15 15:05',
                    distance=8,
                    title='Workout test',
                )
            ),
        )

        assert response.status_code == 401

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-15 15:05',
                    distance=8,
                    title='Workout test',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_updates_a_workout_wo_gpx_with_timezone(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-15 15:05',
                    distance=8,
                    title='Workout test',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            data['data']['workouts'][0]['workout_date']
            == 'Tue, 15 May 2018 13:05:00 GMT'
        )
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1_paris.serialize()
        )
        assert data['data']['workouts'][0]['sport_id'] == sport_2_running.id
        assert data['data']['workouts'][0]['duration'] == '1:00:00'
        assert data['data']['workouts'][0]['title'] == 'Workout test'
        assert data['data']['workouts'][0]['ascent'] is None
        assert data['data']['workouts'][0]['ave_speed'] == 8.0
        assert data['data']['workouts'][0]['descent'] is None
        assert data['data']['workouts'][0]['distance'] == 8.0
        assert data['data']['workouts'][0]['max_alt'] is None
        assert data['data']['workouts'][0]['max_speed'] == 8.0
        assert data['data']['workouts'][0]['min_alt'] is None
        assert data['data']['workouts'][0]['moving'] == '1:00:00'
        assert data['data']['workouts'][0]['pauses'] is None
        assert data['data']['workouts'][0]['with_gpx'] is False

        records = data['data']['workouts'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == sport_2_running.id
        assert records[0]['workout_id'] == workout_short_id
        assert records[0]['record_type'] == 'MS'
        assert records[0]['workout_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[0]['value'] == 8.0
        assert records[1]['sport_id'] == sport_2_running.id
        assert records[1]['workout_id'] == workout_short_id
        assert records[1]['record_type'] == 'LD'
        assert records[1]['workout_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == sport_2_running.id
        assert records[2]['workout_id'] == workout_short_id
        assert records[2]['record_type'] == 'FD'
        assert records[2]['workout_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[2]['value'] == 8.0
        assert records[3]['sport_id'] == sport_2_running.id
        assert records[3]['workout_id'] == workout_short_id
        assert records[3]['record_type'] == 'AS'
        assert records[3]['workout_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[3]['value'] == 8.0

    def test_it_updates_only_sport_and_distance_a_workout_wo_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, distance=20)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            data['data']['workouts'][0]['workout_date']
            == 'Mon, 01 Jan 2018 00:00:00 GMT'
        )
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert data['data']['workouts'][0]['sport_id'] == sport_2_running.id
        assert data['data']['workouts'][0]['duration'] == '1:00:00'
        assert data['data']['workouts'][0]['title'] is None
        assert data['data']['workouts'][0]['ascent'] is None
        assert data['data']['workouts'][0]['ave_speed'] == 20.0
        assert data['data']['workouts'][0]['descent'] is None
        assert data['data']['workouts'][0]['distance'] == 20.0
        assert data['data']['workouts'][0]['max_alt'] is None
        assert data['data']['workouts'][0]['max_speed'] == 20.0
        assert data['data']['workouts'][0]['min_alt'] is None
        assert data['data']['workouts'][0]['moving'] == '1:00:00'
        assert data['data']['workouts'][0]['pauses'] is None
        assert data['data']['workouts'][0]['with_gpx'] is False

        records = data['data']['workouts'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == sport_2_running.id
        assert records[0]['workout_id'] == workout_short_id
        assert records[0]['record_type'] == 'MS'
        assert records[0]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[0]['value'] == 20.0
        assert records[1]['sport_id'] == sport_2_running.id
        assert records[1]['workout_id'] == workout_short_id
        assert records[1]['record_type'] == 'LD'
        assert records[1]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == sport_2_running.id
        assert records[2]['workout_id'] == workout_short_id
        assert records[2]['record_type'] == 'FD'
        assert records[2]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[2]['value'] == 20.0
        assert records[3]['sport_id'] == sport_2_running.id
        assert records[3]['workout_id'] == workout_short_id
        assert records[3]['record_type'] == 'AS'
        assert records[3]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[3]['value'] == 20.0

    def test_it_updates_ascent_and_descent_values(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        ascent = 10
        descent = 0

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(ascent=ascent, descent=descent)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['ascent'] == ascent
        assert data['data']['workouts'][0]['descent'] == descent

        records = data['data']['workouts'][0]['records']
        assert len(records) == 5
        assert records[0]['sport_id'] == sport_1_cycling.id
        assert records[0]['workout_id'] == workout_short_id
        assert records[0]['record_type'] == 'HA'
        assert records[0]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[0]['value'] == ascent
        assert records[1]['sport_id'] == sport_1_cycling.id
        assert records[1]['workout_id'] == workout_short_id
        assert records[1]['record_type'] == 'MS'
        assert records[1]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[1]['value'] == 10.0
        assert records[2]['sport_id'] == sport_1_cycling.id
        assert records[2]['workout_id'] == workout_short_id
        assert records[2]['record_type'] == 'LD'
        assert records[2]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[2]['value'] == '1:00:00'
        assert records[3]['sport_id'] == sport_1_cycling.id
        assert records[3]['workout_id'] == workout_short_id
        assert records[3]['record_type'] == 'FD'
        assert records[3]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[3]['value'] == 10.0
        assert records[4]['sport_id'] == sport_1_cycling.id
        assert records[4]['workout_id'] == workout_short_id
        assert records[4]['record_type'] == 'AS'
        assert records[4]['workout_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[4]['value'] == 10.0

    def test_it_empties_ascent_and_descent_values(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        workout_cycling_user_1.ascent = 100
        workout_cycling_user_1.descent = 150

        response = client.patch(
            f'/api/workouts/{workout_short_id}',
            content_type='application/json',
            data=json.dumps(dict(ascent=None, descent=None)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['ascent'] is None
        assert data['data']['workouts'][0]['descent'] is None
        records = data['data']['workouts'][0]['records']
        assert len(records) == 4
        assert 'HA' not in [record['record_type'] for record in records]

    def test_it_returns_400_if_payload_is_empty(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_500_if_date_format_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='15/2018',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response)

    def test_it_returns_404_if_edited_workout_does_not_exists(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f'/api/workouts/{self.random_short_id()}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    @pytest.mark.parametrize(
        'input_ascent, input_descent',
        [
            (100, None),
            (None, 150),
            (100, -10),
            (-100, 150),
            (100, 'O'),
            ('O', 150),
        ],
    )
    def test_it_returns_400_if_ascent_or_descent_are_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_ascent: int,
        input_descent: int,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    ascent=input_ascent,
                    descent=input_descent,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'input_key',
        ['ascent', 'descent'],
    )
    def test_it_returns_400_if_only_one_value_ascent_or_descent_is_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_key: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps({input_key: 100}),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)


class TestUpdateVisibility(ApiTestCaseMixin):
    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_updates_workout_visibility_for_workout_without_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_description: str,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(workout_visibility=input_workout_visibility.value)
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_visibility.value
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_does_not_update_map_visibility_for_workout_without_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_description: str,
        input_map_visibility: PrivacyLevel,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(dict(map_visibility=input_map_visibility.value)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == workout_cycling_user_1.map_visibility.value
        )

    @pytest.mark.parametrize(
        'input_description,input_workout_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_updates_workout_visibility_for_workout_with_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_description: str,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(
                dict(workout_visibility=input_workout_visibility.value)
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_visibility.value
        )

    @pytest.mark.parametrize(
        'input_description,input_map_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_updates_map_visibility_for_workout_with_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_description: str,
        input_map_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_map_visibility
        workout_cycling_user_1.gpx = 'file.gpx'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(dict(map_visibility=input_map_visibility.value)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == input_map_visibility.value
        )
        assert (
            workout_cycling_user_1.map_visibility.value
            == input_map_visibility.value
        )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_updates_valid_map_visibility_for_workout_with_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        workout_cycling_user_1.gpx = 'file.gpx'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            content_type='application/json',
            data=json.dumps(dict(map_visibility=input_map_visibility.value)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == input_workout_visibility.value
        )
        assert (
            workout_cycling_user_1.map_visibility.value
            == input_workout_visibility.value
        )

import json
import os
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from sqlalchemy.dialects.postgresql import insert

from fittrackee import VERSION, db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Sport,
    Workout,
)

from ..mixins import ApiTestCaseMixin, CallArgsMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


def assert_workout_data_with_gpx(data: Dict) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['workouts'][0]['workout_date']
    )
    assert 'test' == data['data']['workouts'][0]['user']
    assert 1 == data['data']['workouts'][0]['sport_id']
    assert '0:04:10' == data['data']['workouts'][0]['duration']
    assert data['data']['workouts'][0]['ascent'] == 0.4
    assert data['data']['workouts'][0]['ave_speed'] == 4.61
    assert data['data']['workouts'][0]['descent'] == 23.4
    assert data['data']['workouts'][0]['description'] is None
    assert data['data']['workouts'][0]['distance'] == 0.32
    assert data['data']['workouts'][0]['max_alt'] == 998.0
    assert data['data']['workouts'][0]['max_speed'] == 5.12
    assert data['data']['workouts'][0]['min_alt'] == 975.0
    assert data['data']['workouts'][0]['moving'] == '0:04:10'
    assert data['data']['workouts'][0]['pauses'] is None
    assert data['data']['workouts'][0]['with_gpx'] is True
    assert data['data']['workouts'][0]['map'] is not None
    assert data['data']['workouts'][0]['weather_start'] is None
    assert data['data']['workouts'][0]['weather_end'] is None
    assert data['data']['workouts'][0]['notes'] is None
    assert len(data['data']['workouts'][0]['segments']) == 1

    segment = data['data']['workouts'][0]['segments'][0]
    assert segment['workout_id'] == data['data']['workouts'][0]['id']
    assert segment['segment_id'] == 0
    assert segment['duration'] == '0:04:10'
    assert segment['ascent'] == 0.4
    assert segment['ave_speed'] == 4.61
    assert segment['descent'] == 23.4
    assert segment['distance'] == 0.32
    assert segment['max_alt'] == 998.0
    assert segment['max_speed'] == 5.12
    assert segment['min_alt'] == 975.0
    assert segment['moving'] == '0:04:10'
    assert segment['pauses'] is None

    records = data['data']['workouts'][0]['records']
    assert len(records) == 5
    assert records[0]['sport_id'] == 1
    assert records[0]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[0]['record_type'] == 'MS'
    assert records[0]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == 5.12
    assert records[1]['sport_id'] == 1
    assert records[1]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[1]['record_type'] == 'LD'
    assert records[1]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == '0:04:10'
    assert records[2]['sport_id'] == 1
    assert records[2]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[2]['record_type'] == 'HA'
    assert records[2]['value'] == 0.4
    assert records[2]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['sport_id'] == 1
    assert records[3]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[3]['record_type'] == 'FD'
    assert records[3]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 0.32
    assert records[4]['sport_id'] == 1
    assert records[4]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[4]['record_type'] == 'AS'
    assert records[4]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[4]['value'] == 4.61


def assert_workout_data_with_gpx_segments(data: Dict) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['workouts'][0]['workout_date']
    )
    assert 'test' == data['data']['workouts'][0]['user']
    assert 1 == data['data']['workouts'][0]['sport_id']
    assert '0:04:10' == data['data']['workouts'][0]['duration']
    assert data['data']['workouts'][0]['ascent'] == 0.4
    assert data['data']['workouts'][0]['ave_speed'] == 4.59
    assert data['data']['workouts'][0]['descent'] == 23.4
    assert data['data']['workouts'][0]['description'] is None
    assert data['data']['workouts'][0]['distance'] == 0.3
    assert data['data']['workouts'][0]['max_alt'] == 998.0
    assert data['data']['workouts'][0]['max_speed'] == 5.25
    assert data['data']['workouts'][0]['min_alt'] == 975.0
    assert data['data']['workouts'][0]['moving'] == '0:03:55'
    assert data['data']['workouts'][0]['pauses'] == '0:00:15'
    assert data['data']['workouts'][0]['with_gpx'] is True
    assert data['data']['workouts'][0]['map'] is not None
    assert data['data']['workouts'][0]['weather_start'] is None
    assert data['data']['workouts'][0]['weather_end'] is None
    assert data['data']['workouts'][0]['notes'] is None
    assert len(data['data']['workouts'][0]['segments']) == 2

    segment = data['data']['workouts'][0]['segments'][0]
    assert segment['workout_id'] == data['data']['workouts'][0]['id']
    assert segment['segment_id'] == 0
    assert segment['duration'] == '0:01:30'
    assert segment['ascent'] is None
    assert segment['ave_speed'] == 4.53
    assert segment['descent'] == 11.0
    assert segment['distance'] == 0.113
    assert segment['max_alt'] == 998.0
    assert segment['max_speed'] == 5.25
    assert segment['min_alt'] == 987.0
    assert segment['moving'] == '0:01:30'
    assert segment['pauses'] is None

    segment = data['data']['workouts'][0]['segments'][1]
    assert segment['workout_id'] == data['data']['workouts'][0]['id']
    assert segment['segment_id'] == 1
    assert segment['duration'] == '0:02:25'
    assert segment['ascent'] == 0.4
    assert segment['ave_speed'] == 4.62
    assert segment['descent'] == 12.4
    assert segment['distance'] == 0.186
    assert segment['max_alt'] == 987.0
    assert segment['max_speed'] == 5.12
    assert segment['min_alt'] == 975.0
    assert segment['moving'] == '0:02:25'
    assert segment['pauses'] is None

    records = data['data']['workouts'][0]['records']
    assert len(records) == 5
    assert records[0]['sport_id'] == 1
    assert records[0]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[0]['record_type'] == 'MS'
    assert records[0]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == 5.25
    assert records[1]['sport_id'] == 1
    assert records[1]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[1]['record_type'] == 'LD'
    assert records[1]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == '0:03:55'
    assert records[2]['sport_id'] == 1
    assert records[2]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[2]['record_type'] == 'HA'
    assert records[2]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['sport_id'] == 1
    assert records[3]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[3]['record_type'] == 'FD'
    assert records[3]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 0.3
    assert records[4]['sport_id'] == 1
    assert records[4]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[4]['record_type'] == 'AS'
    assert records[4]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[4]['value'] == 4.59


def assert_workout_data_wo_gpx(data: Dict) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        data['data']['workouts'][0]['workout_date']
        == 'Tue, 15 May 2018 14:05:00 GMT'
    )
    assert data['data']['workouts'][0]['user'] == 'test'
    assert data['data']['workouts'][0]['sport_id'] == 1
    assert data['data']['workouts'][0]['duration'] == '1:00:00'
    assert (
        data['data']['workouts'][0]['title']
        == 'Cycling (Sport) - 2018-05-15 14:05:00'
    )
    assert data['data']['workouts'][0]['ascent'] is None
    assert data['data']['workouts'][0]['ave_speed'] == 10.0
    assert data['data']['workouts'][0]['descent'] is None
    assert data['data']['workouts'][0]['description'] is None
    assert data['data']['workouts'][0]['distance'] == 10.0
    assert data['data']['workouts'][0]['max_alt'] is None
    assert data['data']['workouts'][0]['max_speed'] == 10.0
    assert data['data']['workouts'][0]['min_alt'] is None
    assert data['data']['workouts'][0]['moving'] == '1:00:00'
    assert data['data']['workouts'][0]['pauses'] is None
    assert data['data']['workouts'][0]['with_gpx'] is False
    assert data['data']['workouts'][0]['map'] is None
    assert data['data']['workouts'][0]['weather_start'] is None
    assert data['data']['workouts'][0]['weather_end'] is None
    assert data['data']['workouts'][0]['notes'] is None

    assert len(data['data']['workouts'][0]['segments']) == 0

    records = data['data']['workouts'][0]['records']
    assert len(records) == 4
    assert records[0]['sport_id'] == 1
    assert records[0]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[0]['record_type'] == 'MS'
    assert records[0]['workout_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[0]['value'] == 10.0
    assert records[1]['sport_id'] == 1
    assert records[1]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[1]['record_type'] == 'LD'
    assert records[1]['workout_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[1]['value'] == '1:00:00'
    assert records[2]['sport_id'] == 1
    assert records[2]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[2]['record_type'] == 'FD'
    assert records[2]['workout_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[2]['value'] == 10.0
    assert records[3]['sport_id'] == 1
    assert records[3]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[3]['record_type'] == 'AS'
    assert records[3]['workout_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[3]['value'] == 10.0


def assert_files_are_deleted(
    app: Flask, user: User, expected_count: Optional[int] = 0
) -> None:
    upload_directory = os.path.join(
        app.config["UPLOAD_FOLDER"], f"workouts/{user.id}"
    )
    assert (
        len(
            [
                name
                for name in os.listdir(upload_directory)
                if os.path.isfile(os.path.join(upload_directory, name))
            ]
        )
        == expected_count
    )


class TestPostWorkoutWithGpx(ApiTestCaseMixin, CallArgsMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_401(response)

    def test_it_adds_a_workout_with_gpx_file(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'just a workout' == data['data']['workouts'][0]['title']
        assert_workout_data_with_gpx(data)

    def test_it_adds_a_workout_with_gpx_file_and_title_exceeding_limits(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_w_title_exceeding_limit: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_w_title_exceeding_limit)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            len(data['data']['workouts'][0]['title']) == TITLE_MAX_CHARACTERS
        )
        assert_workout_data_with_gpx(data)

    def test_it_adds_a_workout_with_gpx_file_raw_speed(
        self,
        app: Flask,
        user_1_raw_speed: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_raw_speed.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        # max speed should be slightly higher than that tested in
        # assert_workout_data_with_gpx
        assert data['data']['workouts'][0]['max_speed'] == pytest.approx(5.25)

    def test_it_returns_ha_record_when_a_workout_without_gpx_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        records = data['data']['workouts'][0]['records']
        assert len(records) == 1
        assert records[0]['sport_id'] == 1
        assert records[0]['workout_id'] == data['data']['workouts'][0]['id']
        assert records[0]['record_type'] == 'HA'
        assert records[0]['value'] == 0.4
        assert records[0]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'

    def test_it_creates_workout_with_expecting_gpx_path(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        expected_suffix = self.random_string()

        with patch('secrets.token_urlsafe', return_value=expected_suffix):
            client.post(
                '/api/workouts',
                data=dict(
                    file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        workout = Workout.query.first()
        assert (
            workout.gpx
            == f"workouts/1/2018-03-13_12-44-45_1_{expected_suffix}.gpx"
        )

    def test_it_creates_workout_with_expecting_map_path(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        expected_suffix = self.random_string()

        with patch('secrets.token_urlsafe', return_value=expected_suffix):
            client.post(
                '/api/workouts',
                data=dict(
                    file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        workout = Workout.query.first()
        assert (
            workout.map
            == f"workouts/1/2018-03-13_12-44-45_1_{expected_suffix}.png"
        )

    def test_it_adds_a_workout_with_gpx_without_name(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_wo_name: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_name)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            f'{sport_1_cycling.label} - 2018-03-13 12:44:45'
            == data['data']['workouts'][0]['title']
        )
        assert_workout_data_with_gpx(data)

    def test_it_adds_a_workout_with_provided_title(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        title = "some title"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=f'{{"sport_id": 1, "title": "{title}"}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['title'] == title

    def test_it_adds_a_workout_with_gpx_without_name_timezone(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_wo_name: str,
    ) -> None:
        user_1.timezone = 'Europe/Paris'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_name)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            f'{sport_1_cycling.label} - 2018-03-13 13:44:45'
            == data['data']['workouts'][0]['title']
        )
        assert_workout_data_with_gpx(data)

    @pytest.mark.parametrize('input_user_timezone', [None, 'Europe/Paris'])
    def test_it_adds_a_workout_with_gpx_with_offset(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_with_offset: str,
        input_user_timezone: Optional[str],
    ) -> None:
        user_1.timezone = input_user_timezone
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_with_offset)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert_workout_data_with_gpx(data)

    def test_it_adds_a_workout_without_elevation(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_without_elevation: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_without_elevation)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        workout = data['data']['workouts'][0]
        assert workout['duration'] == '0:04:10'
        assert workout['ascent'] is None
        assert workout['ave_speed'] == 4.57
        assert workout['descent'] is None
        assert workout['distance'] == 0.317
        assert workout['max_alt'] is None
        assert workout['max_speed'] == 5.1
        assert workout['min_alt'] is None
        assert workout['with_gpx'] is True

    def test_it_returns_400_when_quotes_are_not_escaped_in_notes(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{{"sport_id": 1, "notes": "test "workout""}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'input_description,input_notes',
        [
            ('empty notes', ''),
            ('short notes', 'test workout'),
            ('notes with special characters', "test \n'workout'©"),
        ],
    )
    def test_it_adds_a_workout_with_gpx_notes(
        self,
        input_description: str,
        input_notes: str,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=f'{{"sport_id": 1, "notes": "{input_notes}"}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == input_notes

    def test_it_adds_a_workout_with_gpx_notes_exceeding_limit(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        notes = self.random_string(length=NOTES_MAX_CHARACTERS + 1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=f'{{"sport_id": 1, "notes": "{notes}"}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == notes[:-1]

    def test_it_returns_400_when_quotes_are_not_escaped_in_description(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{{"sport_id": 1, "description": "test "workout""}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'input_test_description,input_description,expected_description',
        [
            ('empty description', '', None),
            ('short description', 'test workout', 'test workout'),
            (
                'description with special characters',
                "test \n'workout'©",
                "test \n'workout'©",
            ),
        ],
    )
    def test_it_adds_a_workout_with_gpx_and_description(
        self,
        input_test_description: str,
        input_description: str,
        expected_description: str,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": 1, "description": "{input_description}"}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['description'] == expected_description
        )

    def test_it_adds_a_workout_with_gpx_and_description_exceeding_limit(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        description = self.random_string(length=DESCRIPTION_MAX_CHARACTERS + 1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=f'{{"sport_id": 1, "description": "{description}"}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['description'] == description[:-1]

    def test_it_adds_a_workout_with_description_from_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_with_description: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_with_description)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['description']
            == "this is workout description"
        )

    def test_it_adds_a_workout_with_empty_gpx_description(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_with_empty_description: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_with_empty_description)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['description'] is None

    def test_it_overrides_gpx_description_when_description_is_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_with_description: str,
    ) -> None:
        description = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_with_description)),
                    'example.gpx',
                ),
                data=f'{{"sport_id": 1, "description": "{description}"}}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['description'] == description

    def test_it_adds_a_workout_with_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        equipment_bike_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": 1, "equipment_ids":'
                    f' ["{equipment_bike_user_1.short_id}"]}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        workout = Workout.query.first()
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_bike_user_1.total_distance == workout.distance
        assert equipment_bike_user_1.total_duration == workout.duration
        assert equipment_bike_user_1.total_moving == workout.moving

    def test_it_adds_a_workout_with_default_sport_equipments_when_no_equipment_ids_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        equipment_bike_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        workout = Workout.query.first()
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_bike_user_1.total_distance == workout.distance
        assert equipment_bike_user_1.total_duration == workout.duration
        assert equipment_bike_user_1.total_moving == workout.moving

    def test_it_does_not_add_default_sport_equipments_when_equipment_ids_is_empty_list(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        equipment_bike_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1, "equipment_ids": []}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == []
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

    def test_it_returns_400_when_multiple_equipments_are_provided(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        gpx_file: str,
        equipment_shoes_user_1: Equipment,
        equipment_another_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": {sport_2_running.id}, "equipment_ids":'
                    f' ["{equipment_shoes_user_1.short_id}",'
                    f' "{equipment_another_shoes_user_1.short_id}"]}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response, "only one equipment can be added")

    def test_it_returns_error_when_equipment_is_invalid_for_given_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_shoes_user_1: Equipment,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": 1, "equipment_ids":'
                    f' ["{equipment_shoes_user_1.short_id}"]}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_shoes_user_1.short_id
        assert data["message"] == (
            f"invalid equipment id {equipment_shoes_user_1.short_id} "
            f"for sport {sport_1_cycling.label}"
        )
        assert data["status"] == "invalid"

    def test_it_returns_error_when_equipment_is_inactive_for_given_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        gpx_file: str,
    ) -> None:
        equipment_bike_user_1.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": 1, "equipment_ids":'
                    f' ["{equipment_bike_user_1.short_id}"]}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_bike_user_1.short_id
        assert data["message"] == (
            f"equipment with id {equipment_bike_user_1.short_id} is inactive"
        )
        assert data["status"] == "inactive"

    def test_it_does_not_add_inactive_default_equipment_when_no_equipment_ids_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        gpx_file: str,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        equipment_bike_user_1.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == []
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

    def test_it_calls_configured_tile_server_for_static_map_when_default_static_map_to_false(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        static_map_get_mock: Mock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        call_args = self.get_args(static_map_get_mock.call_args)
        assert (
            app.config['TILE_SERVER']['URL']
            .replace('{s}.', '')
            .replace('/{z}/{x}/{y}.png', '')
            in call_args[0]
        )

    def test_it_calls_static_map_with_fittrackee_user_agent_when_default_static_map_to_false(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        static_map_get_mock: Mock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        call_kwargs = self.get_kwargs(static_map_get_mock.call_args)

        assert call_kwargs['headers'] == {
            'User-Agent': f'FitTrackee v{VERSION}'
        }

    def test_it_calls_default_tile_server_for_static_map_when_default_static_map_to_true(  # noqa
        self,
        app_default_static_map: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        static_map_get_mock: Mock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_default_static_map, user_1.email
        )
        client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        call_args = self.get_args(static_map_get_mock.call_args)
        assert (
            app_default_static_map.config['TILE_SERVER']['URL']
            .replace('{s}.', '')
            .replace('/{z}/{x}/{y}.png', '')
            not in call_args[0]
        )

    def test_it_calls_static_map_with_fittrackee_user_agent_when_default_static_map_to_true(  # noqa
        self,
        app_default_static_map: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        static_map_get_mock: Mock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_default_static_map, user_1.email
        )
        client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        call_kwargs = self.get_kwargs(static_map_get_mock.call_args)

        assert call_kwargs['headers'] == {
            'User-Agent': f'FitTrackee v{VERSION}'
        }

    def test_it_returns_500_if_gpx_file_has_not_tracks(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_wo_track: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_track)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = self.assert_500(response, 'no tracks in gpx file')
        assert 'data' not in data

    def test_it_returns_500_if_gpx_has_invalid_xml(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_invalid_xml: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_invalid_xml)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = self.assert_500(response, 'gpx file is invalid')
        assert 'data' not in data

    def test_it_returns_500_if_gpx_has_no_time(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_without_time: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_without_time)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = self.assert_500(response, '<time> is missing in gpx file')
        assert 'data' not in data

    def test_it_returns_400_if_workout_gpx_has_invalid_extension(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.png'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response, 'file extension not allowed', 'fail')

    def test_it_returns_400_if_sport_id_is_not_provided(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'), data='{}'
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response)

    def test_it_returns_500_if_sport_id_does_not_exists(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 2}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_500(response, 'Sport id: 2 does not exist')

    def test_returns_400_if_no_gpx_file_is_provided(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(data='{}'),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        self.assert_400(response, 'no file part', 'fail')

    def test_it_returns_error_if_file_size_exceeds_limit(
        self,
        app_with_max_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_file_size, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = self.assert_413(
            response,
            match=(
                r'Error during workout upload, '
                r'file size \((.*)\) exceeds 1.0KB.'
            ),
        )
        assert 'data' not in data

    def test_it_cleans_uploaded_file_on_gpx_processing_error(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            'fittrackee.workouts.utils.workouts.generate_map',
            side_effect=Exception(),
        ):
            client.post(
                '/api/workouts',
                data=dict(
                    file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        assert_files_are_deleted(app, user_1)

    def test_it_deletes_only_errored_file(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        with patch(
            'fittrackee.workouts.utils.workouts.generate_map',
            side_effect=Exception(),
        ):
            client.post(
                '/api/workouts',
                data=dict(
                    file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                    data='{"sport_id": 2}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        assert_files_are_deleted(app, user_1, expected_count=2)
        upload_directory = os.path.join(app.config["UPLOAD_FOLDER"])
        workout = Workout.query.first()
        os.path.exists(os.path.join(upload_directory, workout.gpx))
        os.path.exists(os.path.join(upload_directory, workout.map))

    def test_it_cleans_uploaded_file_and_static_map_on_segments_creation_error(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            'fittrackee.workouts.utils.workouts.create_segment',
            side_effect=ValueError(),
        ):
            client.post(
                '/api/workouts',
                data=dict(
                    file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        assert_files_are_deleted(app, user_1)

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
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

        response = client.post(
            '/api/workouts',
            data=dict(),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {access_token}',
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPostWorkoutWithoutGpx(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(content_type='multipart/form-data'),
        )

        self.assert_401(response)

    def test_it_adds_a_workout_without_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
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

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert_workout_data_wo_gpx(data)

    def test_it_adds_a_workout_without_gpx_and_title(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        title = self.random_string()

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    title=title,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['title'] == title

    def test_it_adds_a_workout_without_gpx_and_title_exceeding_limit(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        title = self.random_string(length=TITLE_MAX_CHARACTERS + 1)

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    title=title,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['title']
            == title[:TITLE_MAX_CHARACTERS]
        )

    @pytest.mark.parametrize(
        'input_ascent, input_descent',
        [
            (100, 150),
            (0, 150),
            (100, 0),
        ],
    )
    def test_it_adds_workout_with_ascent_and_descent_when_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        input_ascent: int,
        input_descent: int,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    ascent=input_ascent,
                    descent=input_descent,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['ascent'] == input_ascent
        assert data['data']['workouts'][0]['descent'] == input_descent

    def test_it_adds_workout_with_low_value_for_distance(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=1200,
                    workout_date='2023-07-26 12:00',
                    distance=0.001,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['ave_speed'] == 0
        assert data['data']['workouts'][0]['distance'] == 0.001
        assert data['data']['workouts'][0]['duration'] == '0:20:00'
        assert data['data']['workouts'][0]['max_speed'] == 0

    @pytest.mark.parametrize(
        'description,input_data',
        [
            (
                "'sport_id' is missing",
                {
                    "duration": 3600,
                    "workout_date": '2018-05-15 14:05',
                    "distance": 10,
                },
            ),
            (
                "'duration' is missing",
                {
                    "sport_id": 1,
                    "workout_date": '2018-05-15 14:05',
                    "distance": 10,
                },
            ),
            (
                "'workout_date' is missing",
                {"sport_id": 1, "duration": 3600, "distance": 10},
            ),
            (
                "'distance' is missing",
                {
                    "sport_id": 1,
                    "duration": 3600,
                    "workout_date": '2018-05-15 14:05',
                },
            ),
        ],
    )
    def test_it_returns_400_if_key_is_missing(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        description: str,
        input_data: Dict,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(input_data),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'description,input_data',
        [
            ("only ascent", {"ascent": 100}),
            ("only descent", {"descent": 150}),
        ],
    )
    def test_it_returns_400_when_ascent_or_descent_are_missing(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        description: str,
        input_data: Dict,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                {
                    'sport_id': 1,
                    'duration': 3600,
                    'workout_date': '2018-05-15 14:05',
                    'distance': 10,
                    **input_data,
                }
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    @pytest.mark.parametrize(
        'description,input_data',
        [
            ("ascent is below 0", {"ascent": -100, "descent": 100}),
            ("descent is below 0", {"ascent": 150, "descent": -100}),
            ("ascent is None", {"ascent": None, "descent": 100}),
            ("descent is None", {"ascent": 150, "descent": None}),
            ("ascent is invalid", {"ascent": "a", "descent": 100}),
            ("descent is invalid", {"ascent": 150, "descent": "b"}),
        ],
    )
    def test_it_returns_400_when_ascent_or_descent_are_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        description: str,
        input_data: Dict,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                {
                    'sport_id': 1,
                    'duration': 3600,
                    'workout_date': '2018-05-15 14:05',
                    'distance': 10,
                    **input_data,
                }
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_500_if_workout_date_format_is_invalid(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
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

        self.assert_500(response, 'Error during workout save.', status='fail')

    @pytest.mark.parametrize('input_distance', [0, '', None])
    def test_it_returns_400_when_distance_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        input_distance: Any,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=input_distance,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    @pytest.mark.parametrize('input_duration', [0, '', None])
    def test_it_returns_400_when_duration_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        input_duration: Any,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=input_duration,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_adds_a_workout_with_notes(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        notes = "test"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    notes=notes,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == notes

    def test_it_adds_a_workout_with_notes_exceeding_length_limit(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        notes = self.random_string(length=NOTES_MAX_CHARACTERS + 1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    notes=notes,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == notes[:-1]

    def test_it_adds_a_workout_with_description(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        description = "test"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    description=description,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['description'] == description

    def test_it_adds_a_workout_with_description_exceeding_length_limit(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        description = self.random_string(length=DESCRIPTION_MAX_CHARACTERS + 1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    description=description,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['description'] == description[:-1]

    def test_it_adds_a_workout_with_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [
                    equipment_bike_user_1.short_id,
                ],
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_bike_user_1.total_distance == 10
        assert equipment_bike_user_1.total_duration == timedelta(seconds=3600)
        assert equipment_bike_user_1.total_moving == timedelta(seconds=3600)

    def test_it_adds_a_workout_with_default_sport_equipments_when_no_equipment_ids_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_bike_user_1.total_distance == 10
        assert equipment_bike_user_1.total_duration == timedelta(seconds=3600)
        assert equipment_bike_user_1.total_moving == timedelta(seconds=3600)

    def test_it_does_not_add_default_sport_equipments_when_equipment_ids_is_empty_list(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [],
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == []
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

    def test_it_returns_error_when_equipment_is_invalid_for_given_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                ],
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_shoes_user_1.short_id
        assert data["message"] == (
            f"invalid equipment id {equipment_shoes_user_1.short_id} "
            f"for sport {sport_1_cycling.label}"
        )
        assert data["status"] == "invalid"

    def test_it_returns_error_when_equipment_is_inactive_for_given_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
    ) -> None:
        equipment_bike_user_1.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
                "equipment_ids": [equipment_bike_user_1.short_id],
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert data["equipment_id"] == equipment_bike_user_1.short_id
        assert data["message"] == (
            f"equipment with id {equipment_bike_user_1.short_id} is inactive"
        )
        assert data["status"] == "inactive"

    def test_it_does_not_add_inactive_default_equipment_when_no_equipment_ids_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        equipment_bike_user_1.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            json={
                "sport_id": sport_1_cycling.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 10,
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['equipments'] == []
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

    def test_it_returns_400_when_multiple_equipments_are_provided(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        equipment_shoes_user_1: Equipment,
        equipment_another_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            json={
                "sport_id": sport_2_running.id,
                "duration": 3600,
                "workout_date": "2018-05-15 14:05",
                "distance": 5,
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                    equipment_another_shoes_user_1.short_id,
                ],
            },
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, "only one equipment can be added")

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
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

        response = client.post(
            '/api/workouts/no_gpx',
            data=dict(),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {access_token}',
            ),
        )

        self.assert_response_scope(response, can_access)


class TestPostWorkoutWithZipArchive(ApiTestCaseMixin):
    def test_it_adds_workouts_with_zip_archive(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

            data = json.loads(response.data.decode())
            assert response.status_code == 201
            assert 'created' in data['status']
            assert len(data['data']['workouts']) == 3
            assert 'creation_date' in data['data']['workouts'][0]
            assert (
                'Tue, 13 Mar 2018 12:44:45 GMT'
                == data['data']['workouts'][0]['workout_date']
            )
            assert 'test' == data['data']['workouts'][0]['user']
            assert 1 == data['data']['workouts'][0]['sport_id']
            assert '0:04:10' == data['data']['workouts'][0]['duration']
            assert data['data']['workouts'][0]['ascent'] == 0.4
            assert data['data']['workouts'][0]['ave_speed'] == 4.61
            assert data['data']['workouts'][0]['descent'] == 23.4
            assert data['data']['workouts'][0]['description'] is None
            assert data['data']['workouts'][0]['distance'] == 0.32
            assert data['data']['workouts'][0]['max_alt'] == 998.0
            assert data['data']['workouts'][0]['max_speed'] == 5.12
            assert data['data']['workouts'][0]['min_alt'] == 975.0
            assert data['data']['workouts'][0]['moving'] == '0:04:10'
            assert data['data']['workouts'][0]['pauses'] is None
            assert data['data']['workouts'][0]['with_gpx'] is True
            assert data['data']['workouts'][0]['map'] is not None
            assert data['data']['workouts'][0]['weather_start'] is None
            assert data['data']['workouts'][0]['weather_end'] is None
            assert data['data']['workouts'][0]['notes'] is None
            assert len(data['data']['workouts'][0]['segments']) == 1

            segment = data['data']['workouts'][0]['segments'][0]
            assert segment['workout_id'] == data['data']['workouts'][0]['id']
            assert segment['segment_id'] == 0
            assert segment['duration'] == '0:04:10'
            assert segment['ascent'] == 0.4
            assert segment['ave_speed'] == 4.61
            assert segment['descent'] == 23.4
            assert segment['distance'] == 0.32
            assert segment['max_alt'] == 998.0
            assert segment['max_speed'] == 5.12
            assert segment['min_alt'] == 975.0
            assert segment['moving'] == '0:04:10'
            assert segment['pauses'] is None

    def test_it_returns_400_if_folder_is_present_in_zip_archive(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        file_path = os.path.join(
            app.root_path, 'tests/files/gpx_test_folder.zip'
        )
        # 'gpx_test_folder.zip' contains 3 gpx files (same data) and 1 non-gpx
        # file in a folder
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test_folder.zip'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

            data = self.assert_400(response, error_message=None, status='fail')
            assert len(data['data']['workouts']) == 0

    def test_it_returns_500_if_one_file_in_zip_archive_is_invalid(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        file_path = os.path.join(
            app.root_path, 'tests/files/gpx_test_incorrect.zip'
        )
        # 'gpx_test_incorrect.zip' contains 2 gpx files, one is incorrect
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test_incorrect.zip'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

            data = self.assert_500(response, 'no tracks in gpx file')
            assert 'data' not in data

    def test_it_returns_400_when_files_in_archive_exceed_limit(
        self,
        app_with_max_workouts: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        file_path = os.path.join(
            app_with_max_workouts.root_path, 'tests/files/gpx_test.zip'
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_workouts, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

            self.assert_400(
                response,
                'the number of files in the archive exceeds the limit',
                'fail',
            )

    def test_it_returns_error_if_archive_size_exceeds_limit(
        self,
        app_with_max_zip_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        file_path = os.path.join(
            app_with_max_zip_file_size.root_path, 'tests/files/gpx_test.zip'
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_zip_file_size, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

            data = self.assert_413(
                response,
                'Error during workout upload, '
                'file size (2.5KB) exceeds 1.0KB.',
            )
            assert 'data' not in data

    def test_it_returns_error_if_a_file_from_archive_size_exceeds_limit(
        self,
        app_with_max_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        file_path = os.path.join(
            app_with_max_file_size.root_path, 'tests/files/gpx_test.zip'
        )
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_file_size, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

            data = self.assert_400(
                response,
                'at least one file in zip archive exceeds size limit, '
                'please check the archive',
                'fail',
            )
            assert 'data' not in data

    def test_it_cleans_uploaded_file_on_error(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with (
            open(file_path, 'rb') as zip_file,
            patch(
                'fittrackee.workouts.utils.workouts.generate_map',
                side_effect=Exception(),
            ),
        ):
            client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        assert_files_are_deleted(app, user_1)

    def test_it_adds_a_workouts_with_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        equipment_bike_user_1: Equipment,
    ) -> None:
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'),
                    data=(
                        f'{{"sport_id": 1, "equipment_ids":'
                        f' ["{equipment_bike_user_1.short_id}"]}}'
                    ),
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 3
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert data['data']['workouts'][1]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert data['data']['workouts'][2]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert equipment_bike_user_1.total_workouts == 3
        assert float(equipment_bike_user_1.total_distance) == 0.96
        assert equipment_bike_user_1.total_duration == timedelta(seconds=750)
        assert equipment_bike_user_1.total_moving == timedelta(seconds=750)

    def test_it_adds_a_workout_with_default_sport_equipments_when_no_equipment_ids_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        equipment_bike_user_1: Equipment,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 3
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert data['data']['workouts'][1]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]
        assert data['data']['workouts'][2]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]


class TestPostAndGetWorkoutWithGpx(ApiTestCaseMixin):
    def workout_assertion(
        self, app: Flask, user_1: User, gpx_file: str, with_segments: bool
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'just a workout' == data['data']['workouts'][0]['title']
        if with_segments:
            assert_workout_data_with_gpx_segments(data)
        else:
            assert_workout_data_with_gpx(data)
        map_id = data['data']['workouts'][0]['map']
        workout_short_id = data['data']['workouts'][0]['id']

        response = client.get(
            f'/api/workouts/{workout_short_id}/gpx',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert '' in data['message']
        assert len(data['data']['gpx']) != ''

        response = client.get(
            f'/api/workouts/{workout_short_id}/gpx/segment/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert '' in data['message']
        assert len(data['data']['gpx']) != ''

        response = client.get(
            f'/api/workouts/map/{map_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        assert response.status_code == 200

    def test_it_gets_a_workout_created_with_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        return self.workout_assertion(app, user_1, gpx_file, False)

    def test_it_gets_a_workout_created_with_gpx_with_segments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_with_segments: str,
    ) -> None:
        return self.workout_assertion(
            app, user_1, gpx_file_with_segments, True
        )

    def test_it_gets_chart_data_for_a_workout_created_with_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['message'] == ''
        assert len(data['data']['chart_data']) == gpx_file.count("</trkpt>")
        assert data['data']['chart_data'][0] == {
            'distance': 0.0,
            'duration': 0,
            'elevation': 998.0,
            'latitude': 44.68095,
            'longitude': 6.07367,
            'speed': 3.21,
            'time': 'Tue, 13 Mar 2018 12:44:45 GMT',
        }

    def test_it_gets_chart_data_for_a_workout_created_with_gpx_without_elevation(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file_without_elevation: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_without_elevation)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['message'] == ''
        assert len(
            data['data']['chart_data']
        ) == gpx_file_without_elevation.count("</trkpt>")
        # no 'elevation' key in data
        assert data['data']['chart_data'][0] == {
            'distance': 0.0,
            'duration': 0,
            'latitude': 44.68095,
            'longitude': 6.07367,
            'speed': 3.21,
            'time': 'Tue, 13 Mar 2018 12:44:45 GMT',
        }

    def test_it_gets_segment_chart_data_for_a_workout_created_with_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data/segment/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['message'] == ''
        assert data['data']['chart_data'] != ''
        assert len(data['data']['chart_data']) == gpx_file.count("</trkpt>")
        assert data['data']['chart_data'][0] == {
            'distance': 0.0,
            'duration': 0,
            'elevation': 998.0,
            'latitude': 44.68095,
            'longitude': 6.07367,
            'speed': 3.21,
            'time': 'Tue, 13 Mar 2018 12:44:45 GMT',
        }

    def test_it_returns_403_on_getting_chart_data_if_workout_belongs_to_another_user(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_500_on_invalid_segment_id(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data/segment/0',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response, 'Incorrect segment id')

    def test_it_returns_404_if_segment_id_does_not_exist(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data/segment/999999',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404_with_message(
            response, 'No segment with id \'999999\''
        )
        assert 'data' not in data


class TestPostAndGetWorkoutWithoutGpx(ApiTestCaseMixin):
    def test_it_add_and_gets_a_workout_wo_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
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
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert_workout_data_wo_gpx(data)

    def test_it_adds_and_gets_a_workout_wo_gpx_notes(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-15 14:05',
                    distance=10,
                    notes="new test with notes",
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'new test with notes' == data['data']['workouts'][0]['notes']


class TestPostAndGetWorkoutUsingTimezones(ApiTestCaseMixin):
    def test_it_add_and_gets_a_workout_wo_gpx_with_timezone(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        user_1.timezone = 'Europe/Paris'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
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
        data = json.loads(response.data.decode())
        workout_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['workout_date']
            == 'Tue, 15 May 2018 12:05:00 GMT'
        )
        assert (
            data['data']['workouts'][0]['title']
            == f'{sport_1_cycling.label} - 2018-05-15 14:05:00'
        )

    def test_it_adds_and_gets_workouts_date_filter_with_timezone_new_york(
        self, app: Flask, user_1_full: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_full.email
        )

        client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-01-01 00:00',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        response = client.get(
            '/api/workouts?from=2018-01-01&to=2018-01-31',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Mon, 01 Jan 2018 05:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            f'{sport_1_cycling.label} - 2018-01-01 00:00:00'
            == data['data']['workouts'][0]['title']
        )

    def test_it_adds_and_gets_workouts_date_filter_with_timezone_paris(
        self,
        app: Flask,
        user_1_paris: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_paris.email
        )

        client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2017-31-12 23:59',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-01-01 00:00',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        workout_cycling_user_1.workout_date = datetime.strptime(
            '31/01/2018 21:59:59', '%d/%m/%Y %H:%M:%S'
        )
        workout_cycling_user_1.title = 'Test'

        client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-02-01 00:00',
                    distance=10,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        response = client.get(
            '/api/workouts?from=2018-01-01&to=2018-01-31',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert (
            'Wed, 31 Jan 2018 21:59:59 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert 'Test' == data['data']['workouts'][0]['title']
        assert (
            'Sun, 31 Dec 2017 23:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert (
            f'{sport_1_cycling.label} - 2018-01-01 00:00:00'
            == data['data']['workouts'][1]['title']
        )

import json
import os
from datetime import datetime
from io import BytesIO
from typing import Dict, Optional
from unittest.mock import Mock

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout
from fittrackee.workouts.utils.short_id import decode_short_id

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import jsonify_dict


def assert_workout_data_with_gpx(data: Dict, user: User) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['workouts'][0]['workout_date']
    )
    assert data['data']['workouts'][0]['user'] == jsonify_dict(
        user.serialize()
    )
    assert 1 == data['data']['workouts'][0]['sport_id']
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
    assert len(records) == 4
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
    assert records[2]['record_type'] == 'FD'
    assert records[2]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[2]['value'] == 0.32
    assert records[3]['sport_id'] == 1
    assert records[3]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[3]['record_type'] == 'AS'
    assert records[3]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 4.61


def assert_workout_data_with_gpx_segments(data: Dict, user: User) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['workouts'][0]['workout_date']
    )
    assert data['data']['workouts'][0]['user'] == jsonify_dict(
        user.serialize()
    )
    assert 1 == data['data']['workouts'][0]['sport_id']
    assert '0:04:10' == data['data']['workouts'][0]['duration']
    assert data['data']['workouts'][0]['ascent'] == 0.4
    assert data['data']['workouts'][0]['ave_speed'] == 4.59
    assert data['data']['workouts'][0]['descent'] == 23.4
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
    assert len(records) == 4
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
    assert records[2]['record_type'] == 'FD'
    assert records[2]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[2]['value'] == 0.3
    assert records[3]['sport_id'] == 1
    assert records[3]['workout_id'] == data['data']['workouts'][0]['id']
    assert records[3]['record_type'] == 'AS'
    assert records[3]['workout_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 4.59


def assert_workout_data_wo_gpx(data: Dict, user: User) -> None:
    assert 'creation_date' in data['data']['workouts'][0]
    assert (
        data['data']['workouts'][0]['workout_date']
        == 'Tue, 15 May 2018 14:05:00 GMT'
    )
    assert data['data']['workouts'][0]['user'] == jsonify_dict(
        user.serialize()
    )
    assert data['data']['workouts'][0]['sport_id'] == 1
    assert data['data']['workouts'][0]['duration'] == '1:00:00'
    assert (
        data['data']['workouts'][0]['title'] == 'Cycling - 2018-05-15 14:05:00'
    )
    assert data['data']['workouts'][0]['ascent'] is None
    assert data['data']['workouts'][0]['ave_speed'] == 10.0
    assert data['data']['workouts'][0]['descent'] is None
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


class TestPostWorkoutWithGpx(ApiTestCaseMixin, BaseTestMixin):
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'just a workout' == data['data']['workouts'][0]['title']
        assert_workout_data_with_gpx(data, user_1)

    def test_it_adds_a_workout_without_name(
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Cycling - 2018-03-13 12:44:45'
            == data['data']['workouts'][0]['title']
        )
        assert_workout_data_with_gpx(data, user_1)

    def test_it_adds_a_workout_when_user_has_specified_timezone(
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Cycling - 2018-03-13 13:44:45'
            == data['data']['workouts'][0]['title']
        )
        assert_workout_data_with_gpx(data, user_1)

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
        assert_workout_data_with_gpx(data, user_1)

    @pytest.mark.parametrize(
        'input_description,input_notes',
        [
            ('empty notes', ''),
            ('short notes', 'test workout'),
            ('notes with special characters', 'test \nworkout'),
        ],
    )
    def test_it_adds_a_workout_with_notes(
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['notes'] == input_notes

    @pytest.mark.parametrize(
        'input_desc,input_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_workout_is_created_with_user_privacy_parameters_when_no_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        input_desc: str,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.map_visibility = input_visibility
        user_1.workouts_visibility = input_visibility
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == user_1.map_visibility.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == user_1.workouts_visibility.value
        )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC),
            (PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_workout_is_created_with_provided_privacy_parameters(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": 1, "map_visibility": '
                    f'"{input_map_visibility.value}", '
                    f'"workout_visibility": '
                    f'"{input_workout_visibility.value}"}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == input_map_visibility.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_visibility.value
        )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_workout_is_created_with_valid_privacy_parameters_when_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        """
        when workout visibility is stricter, map visibility is initialised
        with workout visibility value
        """
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data=(
                    f'{{"sport_id": 1, "map_visibility": '
                    f'"{input_map_visibility.value}", '
                    f'"workout_visibility": '
                    f'"{input_workout_visibility.value}"}}'
                ),
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == input_workout_visibility.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_visibility.value
        )

    def test_it_calls_configured_tile_server_for_static_map(
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

    def test_it_calls_default_tile_server_for_static_map(
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

        data = self.assert_500(response, 'Error during gpx processing.')
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

        data = self.assert_500(response, 'Error during gpx file parsing.')
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

    def test_it_returns_500_if_sport_id_does_not_exist(
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

    def test_it_returns_error_when_file_size_exceeds_limit(
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert_workout_data_wo_gpx(data, user_1)

    def test_it_returns_400_if_workout_date_is_missing(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(dict(sport_id=1, duration=3600, distance=10)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_500_if_workout_format_is_invalid(
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

    def test_it_adds_workout_with_zero_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
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
                    duration=0,
                    workout_date='2018-05-14 14:05',
                    distance=0,
                    title='Workout test',
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            data['data']['workouts'][0]['workout_date']
            == 'Mon, 14 May 2018 14:05:00 GMT'
        )
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert data['data']['workouts'][0]['sport_id'] == 1
        assert data['data']['workouts'][0]['duration'] is None
        assert data['data']['workouts'][0]['title'] == 'Workout test'
        assert data['data']['workouts'][0]['ascent'] is None
        assert data['data']['workouts'][0]['ave_speed'] is None
        assert data['data']['workouts'][0]['descent'] is None
        assert data['data']['workouts'][0]['distance'] is None
        assert data['data']['workouts'][0]['max_alt'] is None
        assert data['data']['workouts'][0]['max_speed'] is None
        assert data['data']['workouts'][0]['min_alt'] is None
        assert data['data']['workouts'][0]['moving'] is None
        assert data['data']['workouts'][0]['pauses'] is None
        assert data['data']['workouts'][0]['with_gpx'] is False

        assert len(data['data']['workouts'][0]['segments']) == 0
        assert len(data['data']['workouts'][0]['records']) == 0

    @pytest.mark.parametrize(
        'input_desc,input_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_workout_is_created_with_user_privacy_parameters_when_no_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        input_desc: str,
        input_visibility: PrivacyLevel,
    ) -> None:
        user_1.map_visibility = input_visibility
        user_1.workouts_visibility = input_visibility
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

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == user_1.map_visibility.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == user_1.workouts_visibility.value
        )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC),
            (PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_workout_is_created_with_provided_privacy_parameters(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
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
                    map_visibility=input_map_visibility.value,
                    workout_visibility=input_workout_visibility.value,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == input_map_visibility.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_visibility.value
        )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_workout_is_created_with_valid_privacy_parameters_when_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        """
        when workout visibility is stricter, map visibility is initialised
        with workout visibility value
        """
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
                    map_visibility=input_map_visibility.value,
                    workout_visibility=input_workout_visibility.value,
                )
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['map_visibility']
            == input_workout_visibility.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_visibility.value
        )


class TestPostWorkoutWithZipArchive(ApiTestCaseMixin):
    def test_it_adds_workouts_with_zip_archive(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
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

            assert response.status_code == 201
            data = json.loads(response.data.decode())
            assert 'created' in data['status']
            assert len(data['data']['workouts']) == 3
            assert 'just a workout' == data['data']['workouts'][0]['title']
            assert_workout_data_with_gpx(data, user_1)

    def test_it_returns_400_if_folder_is_present_in_zip_archive(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        # 'gpx_test_folder.zip' contains 3 gpx files (same data) and 1 non-gpx
        # file in a folder
        file_path = os.path.join(
            app.root_path, 'tests/files/gpx_test_folder.zip'
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
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
        # 'gpx_test_incorrect.zip' contains 2 gpx files, one is incorrect
        file_path = os.path.join(
            app.root_path, 'tests/files/gpx_test_incorrect.zip'
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
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

            data = self.assert_500(response, 'Error during gpx processing.')
            assert 'data' not in data

    def test_it_imports_only_max_number_of_files(
        self,
        app_with_max_workouts: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(
            app_with_max_workouts.root_path, 'tests/files/gpx_test.zip'
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_workouts, user_1.email
        )
        with open(file_path, 'rb') as zip_file:
            client, auth_token = self.get_test_client_and_auth_token(
                app_with_max_workouts, user_1.email
            )

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

            response = client.get(
                '/api/workouts',
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

            data = json.loads(response.data.decode())
            assert len(data['data']['workouts']) == 2

    def test_it_returns_error_if_archive_size_exceeds_limit(
        self,
        app_with_max_zip_file_size: Flask,
        user_1: User,
        sport_1_cycling: Sport,
    ) -> None:
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        file_path = os.path.join(
            app_with_max_zip_file_size.root_path, 'tests/files/gpx_test.zip'
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_zip_file_size, user_1.email
        )
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

    @pytest.mark.parametrize(
        'input_desc,input_visibility',
        [
            ('private', PrivacyLevel.PRIVATE),
            ('followers_only', PrivacyLevel.FOLLOWERS),
            ('public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_workouts_are_created_with_user_privacy_parameters_when_no_provided(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        input_desc: str,
        input_visibility: PrivacyLevel,
    ) -> None:
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        user_1.map_visibility = input_visibility
        user_1.workouts_visibility = input_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with open(file_path, 'rb') as zip_file:
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

            assert response.status_code == 201
            data = json.loads(response.data.decode())
            assert 'created' in data['status']
            assert len(data['data']['workouts']) == 3
            for n in range(3):
                assert (
                    data['data']['workouts'][n]['map_visibility']
                    == user_1.map_visibility.value
                )
                assert (
                    data['data']['workouts'][n]['workout_visibility']
                    == user_1.workouts_visibility.value
                )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PUBLIC),
            (PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_workouts_are_created_with_provided_privacy_parameters(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with open(file_path, 'rb') as zip_file:
            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'),
                    data=(
                        f'{{"sport_id": 1, "map_visibility": '
                        f'"{input_map_visibility.value}", '
                        f'"workout_visibility": '
                        f'"{input_workout_visibility.value}"}}'
                    ),
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 3
        for n in range(3):
            assert (
                data['data']['workouts'][n]['map_visibility']
                == input_map_visibility.value
            )
            assert (
                data['data']['workouts'][n]['workout_visibility']
                == input_workout_visibility.value
            )

    @pytest.mark.parametrize(
        'input_map_visibility,input_workout_visibility',
        [
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.PRIVATE),
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_workouts_are_created_with_valid_privacy_parameters_when_provided(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        input_map_visibility: PrivacyLevel,
        input_workout_visibility: PrivacyLevel,
    ) -> None:
        """
        when workout visibility is stricter, map visibility is initialised
        with workout visibility value
        """
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with open(file_path, 'rb') as zip_file:
            response = client.post(
                '/api/workouts',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'),
                    data=(
                        f'{{"sport_id": 1, "map_visibility": '
                        f'"{input_map_visibility.value}", '
                        f'"workout_visibility": '
                        f'"{input_workout_visibility.value}"}}'
                    ),
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization=f'Bearer {auth_token}',
                ),
            )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert 'created' in data['status']
        assert len(data['data']['workouts']) == 3
        for n in range(3):
            assert (
                data['data']['workouts'][n]['map_visibility']
                == input_workout_visibility.value
            )
            assert (
                data['data']['workouts'][n]['workout_visibility']
                == input_workout_visibility.value
            )


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
            assert_workout_data_with_gpx_segments(data, user_1)
        else:
            assert_workout_data_with_gpx(data, user_1)
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

        # error case in the same test to avoid generate a new map file
        workout_uuid = decode_short_id(workout_short_id)
        workout = Workout.query.filter_by(uuid=workout_uuid).first()
        workout.map = 'incorrect path'

        assert response.status_code == 200
        assert 'success' in data['status']
        assert '' in data['message']
        assert len(data['data']['gpx']) != ''

        response = client.get(
            f'/api/workouts/map/{map_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_500(response)

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
        assert data['data']['chart_data'] != ''

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

    def test_it_returns_404_on_getting_chart_data_if_workout_belongs_to_another_user(  # noqa
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

        self.assert_404(response)

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
        assert_workout_data_wo_gpx(data, user_1)

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
            == 'Cycling - 2018-05-15 14:05:00'
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
            'Cycling - 2018-01-01 00:00:00'
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
            'Cycling - 2018-01-01 00:00:00'
            == data['data']['workouts'][1]['title']
        )

import json
import os
from datetime import datetime
from io import BytesIO

from fittrackee.activities.models import Activity
from fittrackee.activities.utils_id import decode_short_id


def assert_activity_data_with_gpx(data):
    assert 'creation_date' in data['data']['activities'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['activities'][0]['activity_date']
    )
    assert 'test' == data['data']['activities'][0]['user']
    assert 1 == data['data']['activities'][0]['sport_id']
    assert '0:04:10' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] == 0.4
    assert data['data']['activities'][0]['ave_speed'] == 4.61
    assert data['data']['activities'][0]['descent'] == 23.4
    assert data['data']['activities'][0]['distance'] == 0.32
    assert data['data']['activities'][0]['max_alt'] == 998.0
    assert data['data']['activities'][0]['max_speed'] == 5.12
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:04:10'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is True
    assert data['data']['activities'][0]['map'] is not None
    assert data['data']['activities'][0]['weather_start'] is None
    assert data['data']['activities'][0]['weather_end'] is None
    assert data['data']['activities'][0]['notes'] is None
    assert len(data['data']['activities'][0]['segments']) == 1

    segment = data['data']['activities'][0]['segments'][0]
    assert segment['activity_id'] == data['data']['activities'][0]['id']
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

    records = data['data']['activities'][0]['records']
    assert len(records) == 4
    assert records[0]['sport_id'] == 1
    assert records[0]['activity_id'] == data['data']['activities'][0]['id']
    assert records[0]['record_type'] == 'MS'
    assert records[0]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == 5.12
    assert records[1]['sport_id'] == 1
    assert records[1]['activity_id'] == data['data']['activities'][0]['id']
    assert records[1]['record_type'] == 'LD'
    assert records[1]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == '0:04:10'
    assert records[2]['sport_id'] == 1
    assert records[2]['activity_id'] == data['data']['activities'][0]['id']
    assert records[2]['record_type'] == 'FD'
    assert records[2]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[2]['value'] == 0.32
    assert records[3]['sport_id'] == 1
    assert records[3]['activity_id'] == data['data']['activities'][0]['id']
    assert records[3]['record_type'] == 'AS'
    assert records[3]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 4.61


def assert_activity_data_with_gpx_segments(data):
    assert 'creation_date' in data['data']['activities'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['activities'][0]['activity_date']
    )
    assert 'test' == data['data']['activities'][0]['user']
    assert 1 == data['data']['activities'][0]['sport_id']
    assert '0:04:10' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] == 0.4
    assert data['data']['activities'][0]['ave_speed'] == 4.59
    assert data['data']['activities'][0]['descent'] == 23.4
    assert data['data']['activities'][0]['distance'] == 0.3
    assert data['data']['activities'][0]['max_alt'] == 998.0
    assert (
        data['data']['activities'][0]['max_speed'] is None
    )  # not enough points
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:03:55'
    assert data['data']['activities'][0]['pauses'] == '0:00:15'
    assert data['data']['activities'][0]['with_gpx'] is True
    assert data['data']['activities'][0]['map'] is not None
    assert data['data']['activities'][0]['weather_start'] is None
    assert data['data']['activities'][0]['weather_end'] is None
    assert data['data']['activities'][0]['notes'] is None
    assert len(data['data']['activities'][0]['segments']) == 2

    segment = data['data']['activities'][0]['segments'][0]
    assert segment['activity_id'] == data['data']['activities'][0]['id']
    assert segment['segment_id'] == 0
    assert segment['duration'] == '0:01:30'
    assert segment['ascent'] is None
    assert segment['ave_speed'] == 4.53
    assert segment['descent'] == 11.0
    assert segment['distance'] == 0.113
    assert segment['max_alt'] == 998.0
    assert segment['max_speed'] is None
    assert segment['min_alt'] == 987.0
    assert segment['moving'] == '0:01:30'
    assert segment['pauses'] is None

    segment = data['data']['activities'][0]['segments'][1]
    assert segment['activity_id'] == data['data']['activities'][0]['id']
    assert segment['segment_id'] == 1
    assert segment['duration'] == '0:02:25'
    assert segment['ascent'] == 0.4
    assert segment['ave_speed'] == 4.62
    assert segment['descent'] == 12.4
    assert segment['distance'] == 0.186
    assert segment['max_alt'] == 987.0
    assert segment['max_speed'] is None
    assert segment['min_alt'] == 975.0
    assert segment['moving'] == '0:02:25'
    assert segment['pauses'] is None

    records = data['data']['activities'][0]['records']
    assert len(records) == 3
    assert records[0]['sport_id'] == 1
    assert records[0]['activity_id'] == data['data']['activities'][0]['id']
    assert records[0]['record_type'] == 'LD'
    assert records[0]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == '0:03:55'
    assert records[1]['sport_id'] == 1
    assert records[1]['activity_id'] == data['data']['activities'][0]['id']
    assert records[1]['record_type'] == 'FD'
    assert records[1]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == 0.3
    assert records[2]['sport_id'] == 1
    assert records[2]['activity_id'] == data['data']['activities'][0]['id']
    assert records[2]['record_type'] == 'AS'
    assert records[2]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[2]['value'] == 4.59


def assert_activity_data_wo_gpx(data):
    assert 'creation_date' in data['data']['activities'][0]
    assert (
        data['data']['activities'][0]['activity_date']
        == 'Tue, 15 May 2018 14:05:00 GMT'
    )
    assert data['data']['activities'][0]['user'] == 'test'
    assert data['data']['activities'][0]['sport_id'] == 1
    assert data['data']['activities'][0]['duration'] == '1:00:00'
    assert (
        data['data']['activities'][0]['title']
        == 'Cycling - 2018-05-15 14:05:00'
    )
    assert data['data']['activities'][0]['ascent'] is None
    assert data['data']['activities'][0]['ave_speed'] == 10.0
    assert data['data']['activities'][0]['descent'] is None
    assert data['data']['activities'][0]['distance'] == 10.0
    assert data['data']['activities'][0]['max_alt'] is None
    assert data['data']['activities'][0]['max_speed'] == 10.0
    assert data['data']['activities'][0]['min_alt'] is None
    assert data['data']['activities'][0]['moving'] == '1:00:00'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is False
    assert data['data']['activities'][0]['map'] is None
    assert data['data']['activities'][0]['weather_start'] is None
    assert data['data']['activities'][0]['weather_end'] is None
    assert data['data']['activities'][0]['notes'] is None

    assert len(data['data']['activities'][0]['segments']) == 0

    records = data['data']['activities'][0]['records']
    assert len(records) == 4
    assert records[0]['sport_id'] == 1
    assert records[0]['activity_id'] == data['data']['activities'][0]['id']
    assert records[0]['record_type'] == 'MS'
    assert records[0]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[0]['value'] == 10.0
    assert records[1]['sport_id'] == 1
    assert records[1]['activity_id'] == data['data']['activities'][0]['id']
    assert records[1]['record_type'] == 'LD'
    assert records[1]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[1]['value'] == '1:00:00'
    assert records[2]['sport_id'] == 1
    assert records[2]['activity_id'] == data['data']['activities'][0]['id']
    assert records[2]['record_type'] == 'FD'
    assert records[2]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[2]['value'] == 10.0
    assert records[3]['sport_id'] == 1
    assert records[3]['activity_id'] == data['data']['activities'][0]['id']
    assert records[3]['record_type'] == 'AS'
    assert records[3]['activity_date'] == 'Tue, 15 May 2018 14:05:00 GMT'
    assert records[3]['value'] == 10.0


class TestPostActivityWithGpx:
    def test_it_adds_an_activity_with_gpx_file(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'just an activity' == data['data']['activities'][0]['title']
        assert_activity_data_with_gpx(data)

    def test_it_adds_an_activity_with_gpx_without_name(
        self, app, user_1, sport_1_cycling, gpx_file_wo_name
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_name)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert (
            'Cycling - 2018-03-13 12:44:45'
            == data['data']['activities'][0]['title']
        )
        assert_activity_data_with_gpx(data)

    def test_it_adds_an_activity_with_gpx_without_name_timezone(
        self, app, user_1, sport_1_cycling, gpx_file_wo_name
    ):
        user_1.timezone = 'Europe/Paris'
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_name)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert (
            'Cycling - 2018-03-13 13:44:45'
            == data['data']['activities'][0]['title']
        )
        assert_activity_data_with_gpx(data)

    def test_it_adds_get_an_activity_with_gpx_notes(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1, "notes": "test activity"}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'just an activity' == data['data']['activities'][0]['title']
        assert 'test activity' == data['data']['activities'][0]['notes']

    def test_it_returns_500_if_gpx_file_has_not_tracks(
        self, app, user_1, sport_1_cycling, gpx_file_wo_track
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file_wo_track)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'Error during gpx file parsing.' in data['message']
        assert 'data' not in data

    def test_it_returns_500_if_gpx_has_invalid_xml(
        self, app, user_1, sport_1_cycling, gpx_file_invalid_xml
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(
                    BytesIO(str.encode(gpx_file_invalid_xml)),
                    'example.gpx',
                ),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'Error during gpx file parsing.' in data['message']
        assert 'data' not in data

    def test_it_returns_400_if_activity_gpx_has_invalid_extension(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.png'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert data['status'] == 'fail'
        assert data['message'] == 'File extension not allowed.'

    def test_it_returns_400_if_sport_id_is_not_provided(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'), data='{}'
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid payload.'

    def test_it_returns_500_if_sport_id_does_not_exists(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 2}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert data['status'] == 'error'
        assert data['message'] == 'Sport id: 2 does not exist'

    def test_returns_400_if_no_gpx_file_is_provided(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(data='{}'),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert data['status'] == 'fail'
        assert data['message'] == 'No file part.'


class TestPostActivityWithoutGpx:
    def test_it_adds_an_activity_without_gpx(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert_activity_data_wo_gpx(data)

    def test_it_returns_400_if_activity_date_is_missing(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(dict(sport_id=1, duration=3600, distance=10)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'Invalid payload.' in data['message']

    def test_it_returns_500_if_activity_format_is_invalid(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='15/2018',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'fail' in data['status']
        assert 'Error during activity save.' in data['message']

    def test_it_adds_activity_with_zero_value(
        self, app, user_1, sport_1_cycling, sport_2_running
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=0,
                    activity_date='2018-05-14 14:05',
                    distance=0,
                    title='Activity test',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            data['data']['activities'][0]['activity_date']
            == 'Mon, 14 May 2018 14:05:00 GMT'
        )
        assert data['data']['activities'][0]['user'] == 'test'
        assert data['data']['activities'][0]['sport_id'] == 1
        assert data['data']['activities'][0]['duration'] is None
        assert data['data']['activities'][0]['title'] == 'Activity test'
        assert data['data']['activities'][0]['ascent'] is None
        assert data['data']['activities'][0]['ave_speed'] is None
        assert data['data']['activities'][0]['descent'] is None
        assert data['data']['activities'][0]['distance'] is None
        assert data['data']['activities'][0]['max_alt'] is None
        assert data['data']['activities'][0]['max_speed'] is None
        assert data['data']['activities'][0]['min_alt'] is None
        assert data['data']['activities'][0]['moving'] is None
        assert data['data']['activities'][0]['pauses'] is None
        assert data['data']['activities'][0]['with_gpx'] is False

        assert len(data['data']['activities'][0]['segments']) == 0
        assert len(data['data']['activities'][0]['records']) == 0


class TestPostActivityWithZipArchive:
    def test_it_adds_activities_with_zip_archive(
        self, app, user_1, sport_1_cycling
    ):
        file_path = os.path.join(app.root_path, 'tests/files/gpx_test.zip')
        # 'gpx_test.zip' contains 3 gpx files (same data) and 1 non-gpx file
        with open(file_path, 'rb') as zip_file:
            client = app.test_client()
            resp_login = client.post(
                '/api/auth/login',
                data=json.dumps(
                    dict(email='test@test.com', password='12345678')
                ),
                content_type='application/json',
            )

            response = client.post(
                '/api/activities',
                data=dict(
                    file=(zip_file, 'gpx_test.zip'), data='{"sport_id": 1}'
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization='Bearer '
                    + json.loads(resp_login.data.decode())['auth_token'],
                ),
            )

            data = json.loads(response.data.decode())
            assert response.status_code == 201
            assert 'created' in data['status']
            assert len(data['data']['activities']) == 3
            assert 'just an activity' == data['data']['activities'][0]['title']
            assert_activity_data_with_gpx(data)

    def test_it_returns_400_if_folder_is_present_in_zpi_archive(
        self, app, user_1, sport_1_cycling
    ):
        file_path = os.path.join(
            app.root_path, 'tests/files/gpx_test_folder.zip'
        )
        # 'gpx_test_folder.zip' contains 3 gpx files (same data) and 1 non-gpx
        # file in a folder
        with open(file_path, 'rb') as zip_file:
            client = app.test_client()
            resp_login = client.post(
                '/api/auth/login',
                data=json.dumps(
                    dict(email='test@test.com', password='12345678')
                ),
                content_type='application/json',
            )

            response = client.post(
                '/api/activities',
                data=dict(
                    file=(zip_file, 'gpx_test_folder.zip'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization='Bearer '
                    + json.loads(resp_login.data.decode())['auth_token'],
                ),
            )

            data = json.loads(response.data.decode())
            assert response.status_code == 400
            assert 'fail' in data['status']
            assert len(data['data']['activities']) == 0

    def test_it_returns_500_if_one_fle_in_zip_archive_is_invalid(
        self, app, user_1, sport_1_cycling
    ):
        file_path = os.path.join(
            app.root_path, 'tests/files/gpx_test_incorrect.zip'
        )
        # 'gpx_test_incorrect.zip' contains 2 gpx files, one is incorrect
        with open(file_path, 'rb') as zip_file:
            client = app.test_client()
            resp_login = client.post(
                '/api/auth/login',
                data=json.dumps(
                    dict(email='test@test.com', password='12345678')
                ),
                content_type='application/json',
            )

            response = client.post(
                '/api/activities',
                data=dict(
                    file=(zip_file, 'gpx_test_incorrect.zip'),
                    data='{"sport_id": 1}',
                ),
                headers=dict(
                    content_type='multipart/form-data',
                    Authorization='Bearer '
                    + json.loads(resp_login.data.decode())['auth_token'],
                ),
            )

            data = json.loads(response.data.decode())
            assert response.status_code == 500
            assert 'error' in data['status']
            assert 'Error during gpx file parsing.' in data['message']
            assert 'data' not in data


class TestPostAndGetActivityWithGpx:
    @staticmethod
    def activity_assertion(app, gpx_file, with_segments):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'just an activity' == data['data']['activities'][0]['title']
        if with_segments:
            assert_activity_data_with_gpx_segments(data)
        else:
            assert_activity_data_with_gpx(data)
        map_id = data['data']['activities'][0]['map']
        activity_short_id = data['data']['activities'][0]['id']

        response = client.get(
            f'/api/activities/{activity_short_id}/gpx',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert '' in data['message']
        assert len(data['data']['gpx']) != ''

        response = client.get(
            f'/api/activities/{activity_short_id}/gpx/segment/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert '' in data['message']
        assert len(data['data']['gpx']) != ''

        response = client.get(
            f'/api/activities/map/{map_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        assert response.status_code == 200

        # error case in the same test to avoid generate a new map file
        activity_uuid = decode_short_id(activity_short_id)
        activity = Activity.query.filter_by(uuid=activity_uuid).first()
        activity.map = 'incorrect path'

        assert response.status_code == 200
        assert 'success' in data['status']
        assert '' in data['message']
        assert len(data['data']['gpx']) != ''

        response = client.get(
            f'/api/activities/map/{map_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 500
        assert data['status'] == 'error'
        assert (
            data['message']
            == 'Error. Please try again or contact the administrator.'
        )

    def test_it_gets_an_activity_created_with_gpx(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        return self.activity_assertion(app, gpx_file, False)

    def test_it_gets_an_activity_created_with_gpx_with_segments(
        self, app, user_1, sport_1_cycling, gpx_file_with_segments
    ):
        return self.activity_assertion(app, gpx_file_with_segments, True)

    def test_it_gets_chart_data_for_an_activity_created_with_gpx(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['message'] == ''
        assert data['data']['chart_data'] != ''

    def test_it_gets_segment_chart_data_for_an_activity_created_with_gpx(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}/chart_data/segment/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert data['message'] == ''
        assert data['data']['chart_data'] != ''

    def test_it_returns_403_on_getting_chart_data_if_activity_belongs_to_another_user(  # noqa
        self, app, user_1, user_2, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']

        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='toto@toto.com', password='87654321')),
            content_type='application/json',
        )
        response = client.get(
            f'/api/activities/{activity_short_id}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'error' in data['status']
        assert data['message'] == 'You do not have permissions.'

    def test_it_returns_500_on_invalid_segment_id(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}/chart_data/segment/0',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert data['message'] == 'Incorrect segment id'
        assert 'data' not in data

    def test_it_returns_404_if_segment_id_does_not_exist(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}/chart_data/segment/999999',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert data['message'] == 'No segment with id \'999999\''
        assert 'data' not in data


class TestPostAndGetActivityWithoutGpx:
    def test_it_add_and_gets_an_activity_wo_gpx(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert_activity_data_wo_gpx(data)

    def test_it_adds_and_gets_an_activity_wo_gpx_notes(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-15 14:05',
                    distance=10,
                    notes="new test with notes",
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'new test with notes' == data['data']['activities'][0]['notes']


class TestPostAndGetActivityUsingTimezones:
    def test_it_add_and_gets_an_activity_wo_gpx_with_timezone(
        self, app, user_1, sport_1_cycling
    ):
        user_1.timezone = 'Europe/Paris'
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        activity_short_id = data['data']['activities'][0]['id']
        response = client.get(
            f'/api/activities/{activity_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert (
            data['data']['activities'][0]['activity_date']
            == 'Tue, 15 May 2018 12:05:00 GMT'
        )
        assert (
            data['data']['activities'][0]['title']
            == 'Cycling - 2018-05-15 14:05:00'
        )

    def test_it_adds_and_gets_activities_date_filter_with_timezone_new_york(
        self, app, user_1_full, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-01-01 00:00',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/activities?from=2018-01-01&to=2018-01-31',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert (
            'Mon, 01 Jan 2018 05:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Cycling - 2018-01-01 00:00:00'
            == data['data']['activities'][0]['title']
        )

    def test_it_adds_and_gets_activities_date_filter_with_timezone_paris(
        self, app, user_1_paris, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2017-31-12 23:59',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-01-01 00:00',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        activity_cycling_user_1.activity_date = datetime.strptime(
            '31/01/2018 21:59:59', '%d/%m/%Y %H:%M:%S'
        )
        activity_cycling_user_1.title = 'Test'

        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-02-01 00:00',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/activities?from=2018-01-01&to=2018-01-31',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 2
        assert (
            'Wed, 31 Jan 2018 21:59:59 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert 'Test' == data['data']['activities'][0]['title']
        assert (
            'Sun, 31 Dec 2017 23:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )
        assert (
            'Cycling - 2018-01-01 00:00:00'
            == data['data']['activities'][1]['title']
        )

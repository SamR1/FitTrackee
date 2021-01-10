import json

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout
from flask import Flask


class TestGetRecords:
    def test_it_gets_records_for_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][0]['workout_date']
        )
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert (
            workout_cycling_user_1.short_id
            == data['data']['records'][0]['workout_id']
        )
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 'value' in data['data']['records'][0]

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][1]['workout_date']
        )
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert (
            workout_cycling_user_1.short_id
            == data['data']['records'][1]['workout_id']
        )
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 'value' in data['data']['records'][1]

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][2]['workout_date']
        )
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert (
            workout_cycling_user_1.short_id
            == data['data']['records'][2]['workout_id']
        )
        assert 'LD' == data['data']['records'][2]['record_type']
        assert 'value' in data['data']['records'][2]

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert (
            workout_cycling_user_1.short_id
            == data['data']['records'][3]['workout_id']
        )
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 'value' in data['data']['records'][3]

    def test_it_gets_no_records_if_user_has_no_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 0

    def test_it_gets_no_records_if_workout_has_zero_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
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
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 0

    def test_it_gets_updated_records_after_workouts_post_and_patch(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-14 14:05',
                    distance=7,
                    title='Workout test 1',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_1_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_1_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_1_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert workout_1_short_id == data['data']['records'][3]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # Post workout with lower duration (same sport)
        # => 2 new records: Average speed and Max speed
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3000,
                    workout_date='2018-05-15 14:05',
                    distance=7,
                    title='Workout test 2',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_2_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 8.4 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_1_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 8.4 == data['data']['records'][3]['value']

        # Post workout with no new records
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3500,
                    workout_date='2018-05-16 14:05',
                    distance=6.5,
                    title='Workout test 3',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_3_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 8.4 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_1_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 8.4 == data['data']['records'][3]['value']

        # Edit last workout
        # 1 new record: Longest duration
        client.patch(
            f'/api/workouts/{workout_3_short_id}',
            content_type='application/json',
            data=json.dumps(dict(duration=4000)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 8.4 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_3_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 8.4 == data['data']['records'][3]['value']

        # delete workout 2 => AS and MS record update
        client.delete(
            f'/api/workouts/{workout_2_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_1_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_3_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert workout_1_short_id == data['data']['records'][3]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # add a workout with the same data as workout 1 except with a
        # later date => no change in record
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-20 14:05',
                    distance=7,
                    title='Workout test 4',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_4_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_1_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_3_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert workout_1_short_id == data['data']['records'][3]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # add a workout with the same data as workout 1 except with
        # an earlier date
        # => record update (workout 5 replace workout 1)

        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-14 08:05',
                    distance=7,
                    title='Workout test 5',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_5_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 08:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_5_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 08:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_5_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_3_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 08:05:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert workout_5_short_id == data['data']['records'][3]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # delete all workouts - no more records
        client.delete(
            f'/api/workouts/{workout_1_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.delete(
            f'/api/workouts/{workout_3_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.delete(
            f'/api/workouts/{workout_4_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.delete(
            f'/api/workouts/{workout_5_short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 0

    def test_it_gets_updated_records_after_sport_change(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    workout_date='2018-05-14 14:05',
                    distance=7,
                    title='Workout test 1',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_1_short_id = data['data']['workouts'][0]['id']
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    workout_date='2018-05-16 16:05',
                    distance=20,
                    title='Workout test 2',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_2_short_id = data['data']['workouts'][0]['id']
        client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3000,
                    workout_date='2018-05-17 17:05',
                    distance=3,
                    title='Workout test 3',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.post(
            '/api/workouts/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3000,
                    workout_date='2018-05-18 18:05',
                    distance=10,
                    title='Workout test 4',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())
        workout_4_short_id = data['data']['workouts'][0]['id']
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 8

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_1_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_1_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_1_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert workout_1_short_id == data['data']['records'][3]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][4]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][4]['user']
        assert sport_2_running.id == data['data']['records'][4]['sport_id']
        assert workout_2_short_id == data['data']['records'][4]['workout_id']
        assert 'AS' == data['data']['records'][4]['record_type']
        assert 20.0 == data['data']['records'][4]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][5]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][5]['user']
        assert sport_2_running.id == data['data']['records'][5]['sport_id']
        assert workout_2_short_id == data['data']['records'][5]['workout_id']
        assert 'FD' == data['data']['records'][5]['record_type']
        assert 20.0 == data['data']['records'][5]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][6]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][6]['user']
        assert sport_2_running.id == data['data']['records'][6]['sport_id']
        assert workout_2_short_id == data['data']['records'][6]['workout_id']
        assert 'LD' == data['data']['records'][6]['record_type']
        assert '1:00:00' == data['data']['records'][6]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][7]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][7]['user']
        assert sport_2_running.id == data['data']['records'][7]['sport_id']
        assert workout_2_short_id == data['data']['records'][7]['workout_id']
        assert 'MS' == data['data']['records'][7]['record_type']
        assert 20.0 == data['data']['records'][7]['value']

        client.patch(
            f'/api/workouts/{workout_2_short_id}',
            content_type='application/json',
            data=json.dumps(dict(sport_id=1)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        response = client.get(
            '/api/records',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['records']) == 8

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][0]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert sport_1_cycling.id == data['data']['records'][0]['sport_id']
        assert workout_2_short_id == data['data']['records'][0]['workout_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 20.0 == data['data']['records'][0]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][1]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert sport_1_cycling.id == data['data']['records'][1]['sport_id']
        assert workout_2_short_id == data['data']['records'][1]['workout_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 20.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert sport_1_cycling.id == data['data']['records'][2]['sport_id']
        assert workout_1_short_id == data['data']['records'][2]['workout_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][3]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert sport_1_cycling.id == data['data']['records'][3]['sport_id']
        assert workout_2_short_id == data['data']['records'][3]['workout_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 20.0 == data['data']['records'][3]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][4]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][4]['user']
        assert sport_2_running.id == data['data']['records'][4]['sport_id']
        assert workout_4_short_id == data['data']['records'][4]['workout_id']
        assert 'AS' == data['data']['records'][4]['record_type']
        assert 12.0 == data['data']['records'][4]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][5]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][5]['user']
        assert sport_2_running.id == data['data']['records'][5]['sport_id']
        assert workout_4_short_id == data['data']['records'][5]['workout_id']
        assert 'FD' == data['data']['records'][5]['record_type']
        assert 10.0 == data['data']['records'][5]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][6]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][6]['user']
        assert sport_2_running.id == data['data']['records'][6]['sport_id']
        assert workout_4_short_id == data['data']['records'][6]['workout_id']
        assert 'LD' == data['data']['records'][6]['record_type']
        assert '0:50:00' == data['data']['records'][6]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][7]['workout_date']
        )  # noqa
        assert 'test' == data['data']['records'][7]['user']
        assert sport_2_running.id == data['data']['records'][7]['sport_id']
        assert workout_4_short_id == data['data']['records'][7]['workout_id']
        assert 'MS' == data['data']['records'][7]['record_type']
        assert 12.0 == data['data']['records'][7]['value']

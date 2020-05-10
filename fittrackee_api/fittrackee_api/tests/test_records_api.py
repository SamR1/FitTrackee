import json


class TestGetRecords:
    def test_it_gets_records_for_authenticated_user(
        self,
        app,
        user_1,
        user_2,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
        activity_cycling_user_2,
    ):
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
            == data['data']['records'][0]['activity_date']
        )
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 1 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 'value' in data['data']['records'][0]

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][1]['activity_date']
        )
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 'value' in data['data']['records'][1]

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][2]['activity_date']
        )
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 1 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert 'value' in data['data']['records'][2]

        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 1 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 'value' in data['data']['records'][3]

    def test_it_gets_no_records_if_user_has_no_activity(
        self,
        app,
        user_1,
        user_2,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_2,
    ):
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

    def test_it_gets_no_records_if_activity_has_zero_value(
        self, app, user_1, sport_1_cycling, sport_2_running
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

    def test_it_gets_updated_records_after_activities_post_and_patch(
        self, app, user_1, sport_1_cycling
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
                    activity_date='2018-05-14 14:05',
                    distance=7,
                    title='Activity test 1',
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
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 1 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 1 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 1 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # Post activity with lower duration (same sport)
        # => 2 new records: Average speed and Max speed
        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3000,
                    activity_date='2018-05-15 14:05',
                    distance=7,
                    title='Activity test 2',
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
        assert len(data['data']['records']) == 4

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 8.4 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 1 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 8.4 == data['data']['records'][3]['value']

        # Post activity with no new records
        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3500,
                    activity_date='2018-05-16 14:05',
                    distance=6.5,
                    title='Activity test 3',
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
        assert len(data['data']['records']) == 4

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 8.4 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 1 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 8.4 == data['data']['records'][3]['value']

        # Edit last activity
        # 1 new record: Longest duration
        client.patch(
            '/api/activities/3',
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
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 8.4 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 3 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Tue, 15 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 8.4 == data['data']['records'][3]['value']

        # delete activity 2 => AS and MS record update
        client.delete(
            '/api/activities/2',
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
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 1 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 3 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 1 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # add an activity with the same data as activity 1 except with a
        # later date => no change in record
        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-20 14:05',
                    distance=7,
                    title='Activity test 4',
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
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 1 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 3 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 1 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # add an activity with the same data as activity 1 except with
        # an earlier date
        # => record update (activity 5 replace activity 1)

        client.post(
            '/api/activities/no_gpx',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-14 08:05',
                    distance=7,
                    title='Activity test 5',
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
        assert len(data['data']['records']) == 4

        assert (
            'Mon, 14 May 2018 08:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 5 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 08:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 5 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Wed, 16 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 3 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:06:40' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 08:05:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 5 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        # delete all activities - no more records
        client.delete(
            '/api/activities/1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.delete(
            '/api/activities/3',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.delete(
            '/api/activities/4',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        client.delete(
            '/api/activities/5',
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
        self, app, user_1, sport_1_cycling, sport_2_running
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
                    activity_date='2018-05-14 14:05',
                    distance=7,
                    title='Activity test 1',
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
                    sport_id=2,
                    duration=3600,
                    activity_date='2018-05-16 16:05',
                    distance=20,
                    title='Activity test 2',
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
                    duration=3000,
                    activity_date='2018-05-17 17:05',
                    distance=3,
                    title='Activity test 3',
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
                    sport_id=2,
                    duration=3000,
                    activity_date='2018-05-18 18:05',
                    distance=10,
                    title='Activity test 4',
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
        assert len(data['data']['records']) == 8

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 1 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 7.0 == data['data']['records'][0]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 1 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 7.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 1 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 1 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 7.0 == data['data']['records'][3]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][4]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][4]['user']
        assert 2 == data['data']['records'][4]['sport_id']
        assert 2 == data['data']['records'][4]['activity_id']
        assert 'AS' == data['data']['records'][4]['record_type']
        assert 20.0 == data['data']['records'][4]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][5]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][5]['user']
        assert 2 == data['data']['records'][5]['sport_id']
        assert 2 == data['data']['records'][5]['activity_id']
        assert 'FD' == data['data']['records'][5]['record_type']
        assert 20.0 == data['data']['records'][5]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][6]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][6]['user']
        assert 2 == data['data']['records'][6]['sport_id']
        assert 2 == data['data']['records'][6]['activity_id']
        assert 'LD' == data['data']['records'][6]['record_type']
        assert '1:00:00' == data['data']['records'][6]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][7]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][7]['user']
        assert 2 == data['data']['records'][7]['sport_id']
        assert 2 == data['data']['records'][7]['activity_id']
        assert 'MS' == data['data']['records'][7]['record_type']
        assert 20.0 == data['data']['records'][7]['value']

        client.patch(
            '/api/activities/2',
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
            == data['data']['records'][0]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][0]['user']
        assert 1 == data['data']['records'][0]['sport_id']
        assert 2 == data['data']['records'][0]['activity_id']
        assert 'AS' == data['data']['records'][0]['record_type']
        assert 20.0 == data['data']['records'][0]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][1]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][1]['user']
        assert 1 == data['data']['records'][1]['sport_id']
        assert 2 == data['data']['records'][1]['activity_id']
        assert 'FD' == data['data']['records'][1]['record_type']
        assert 20.0 == data['data']['records'][1]['value']

        assert (
            'Mon, 14 May 2018 14:05:00 GMT'
            == data['data']['records'][2]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][2]['user']
        assert 1 == data['data']['records'][2]['sport_id']
        assert 1 == data['data']['records'][2]['activity_id']
        assert 'LD' == data['data']['records'][2]['record_type']
        assert '1:00:00' == data['data']['records'][2]['value']

        assert (
            'Wed, 16 May 2018 16:05:00 GMT'
            == data['data']['records'][3]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][3]['user']
        assert 1 == data['data']['records'][3]['sport_id']
        assert 2 == data['data']['records'][3]['activity_id']
        assert 'MS' == data['data']['records'][3]['record_type']
        assert 20.0 == data['data']['records'][3]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][4]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][4]['user']
        assert 2 == data['data']['records'][4]['sport_id']
        assert 4 == data['data']['records'][4]['activity_id']
        assert 'AS' == data['data']['records'][4]['record_type']
        assert 12.0 == data['data']['records'][4]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][5]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][5]['user']
        assert 2 == data['data']['records'][5]['sport_id']
        assert 4 == data['data']['records'][5]['activity_id']
        assert 'FD' == data['data']['records'][5]['record_type']
        assert 10.0 == data['data']['records'][5]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][6]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][6]['user']
        assert 2 == data['data']['records'][6]['sport_id']
        assert 4 == data['data']['records'][6]['activity_id']
        assert 'LD' == data['data']['records'][6]['record_type']
        assert '0:50:00' == data['data']['records'][6]['value']

        assert (
            'Fri, 18 May 2018 18:05:00 GMT'
            == data['data']['records'][7]['activity_date']
        )  # noqa
        assert 'test' == data['data']['records'][7]['user']
        assert 2 == data['data']['records'][7]['sport_id']
        assert 4 == data['data']['records'][7]['activity_id']
        assert 'MS' == data['data']['records'][7]['record_type']
        assert 12.0 == data['data']['records'][7]['value']

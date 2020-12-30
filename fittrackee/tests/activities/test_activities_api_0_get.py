import json
from uuid import uuid4


class TestGetActivities:
    def test_it_gets_all_activities_for_authenticated_user(
        self,
        app,
        user_1,
        user_2,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
        activity_cycling_user_2,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 2
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert 'test' == data['data']['activities'][0]['user']
        assert 2 == data['data']['activities'][0]['sport_id']
        assert 12.0 == data['data']['activities'][0]['distance']
        assert '1:40:00' == data['data']['activities'][0]['duration']

        assert 'creation_date' in data['data']['activities'][1]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )
        assert 'test' == data['data']['activities'][1]['user']
        assert 1 == data['data']['activities'][1]['sport_id']
        assert 10.0 == data['data']['activities'][1]['distance']
        assert '1:00:00' == data['data']['activities'][1]['duration']

    def test_it_gets_no_activities_for_authenticated_user_with_no_activities(
        self,
        app,
        user_1,
        user_2,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='toto@toto.com', password='87654321')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 0

    def test_it_returns_401_if_user_is_not_authenticated(self, app):
        client = app.test_client()

        response = client.get('/api/activities')

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert 'error' in data['status']
        assert 'Provide a valid auth token.' in data['message']


class TestGetActivitiesWithPagination:
    def test_it_gets_activities_with_default_pagination(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 5
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert '0:50:00' == data['data']['activities'][0]['duration']
        assert 'creation_date' in data['data']['activities'][4]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['activities'][4]['activity_date']
        )
        assert '0:17:04' == data['data']['activities'][4]['duration']

    def test_it_gets_first_page(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?page=1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 5
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert '0:50:00' == data['data']['activities'][0]['duration']
        assert 'creation_date' in data['data']['activities'][4]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['activities'][4]['activity_date']
        )
        assert '0:17:04' == data['data']['activities'][4]['duration']

    def test_it_gets_second_page(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?page=2',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 2
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert '0:57:36' == data['data']['activities'][0]['duration']
        assert 'creation_date' in data['data']['activities'][1]
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )
        assert '0:17:04' == data['data']['activities'][1]['duration']

    def test_it_gets_empty_third_page(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?page=3',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 0

    def test_it_returns_error_on_invalid_page_value(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?page=A',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'Error. Please try again or contact the administrator.'
            in data['message']
        )

    def test_it_gets_5_activities_per_page(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?per_page=10',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 7
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['activities'][6]['activity_date']
        )

    def test_it_gets_3_activities_per_page(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?per_page=3',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 3
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['activities'][2]['activity_date']
        )


class TestGetActivitiesWithFilters:
    def test_it_gets_activities_with_date_filter(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?from=2018-02-01&to=2018-02-28',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 2
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert '0:10:00' == data['data']['activities'][0]['duration']
        assert 'creation_date' in data['data']['activities'][1]
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )
        assert '0:16:40' == data['data']['activities'][1]['duration']

    def test_it_gets_no_activities_with_date_filter(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?from=2018-03-01&to=2018-03-30',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 0

    def test_if_gets_activities_with_date_filter_from(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?from=2018-04-01',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 2
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )

    def test_it_gets_activities_with_date_filter_to(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?to=2017-12-31',
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
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )

    def test_it_gets_activities_with_ascending_order(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?order=asc',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 5
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['activities'][4]['activity_date']
        )

    def test_it_gets_activities_with_distance_filter(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?distance_from=5&distance_to=8',
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
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )

    def test_it_gets_activities_with_duration_filter(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?duration_from=00:52&duration_to=01:20',
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
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )

    def test_it_gets_activities_with_average_speed_filter(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?ave_speed_from=5&ave_speed_to=10',
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
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )

    def test_it_gets_activities_with_max_speed_filter(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
        activity_running_user_1,
    ):
        activity_cycling_user_1.max_speed = 25
        activity_running_user_1.max_speed = 11
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?max_speed_from=10&max_speed_to=20',
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
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )

    def test_it_gets_activities_with_sport_filter(
        self,
        app,
        user_1,
        sport_1_cycling,
        seven_activities_user_1,
        sport_2_running,
        activity_running_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?sport_id=2',
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
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )


class TestGetActivitiesWithFiltersAndPagination:
    def test_it_gets_page_2_with_date_filter(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?from=2017-01-01&page=2',
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
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )

    def test_it_get_page_2_with_date_filter_and_ascending_order(
        self, app, user_1, sport_1_cycling, seven_activities_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/activities?from=2017-01-01&page=2&order=asc',
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
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['activities'][1]['activity_date']
        )


class TestGetActivity:
    def test_it_gets_an_activity(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{activity_cycling_user_1.uuid.hex}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['activities'][0]['activity_date']
        )
        assert 'test' == data['data']['activities'][0]['user']
        assert 1 == data['data']['activities'][0]['sport_id']
        assert 10.0 == data['data']['activities'][0]['distance']
        assert '1:00:00' == data['data']['activities'][0]['duration']

    def test_it_returns_403_if_activity_belongs_to_a_different_user(
        self, app, user_1, user_2, sport_1_cycling, activity_cycling_user_2
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{activity_cycling_user_2.uuid.hex}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_it_returns_404_if_activity_does_not_exist(self, app, user_1):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{uuid4().hex}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['activities']) == 0

    def test_it_returns_404_on_getting_gpx_if_activity_does_not_exist(
        self, app, user_1
    ):
        random_uuid = uuid4().hex
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{random_uuid}/gpx',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'Activity not found (id: {random_uuid})' in data['message']
        assert data['data']['gpx'] == ''

    def test_it_returns_404_on_getting_chart_data_if_activity_does_not_exist(
        self, app, user_1
    ):
        random_uuid = uuid4().hex
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{random_uuid}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'Activity not found (id: {random_uuid})' in data['message']
        assert data['data']['chart_data'] == ''

    def test_it_returns_404_on_getting_gpx_if_activity_have_no_gpx(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        activity_uuid = activity_cycling_user_1.uuid.hex
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{activity_uuid}/gpx',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'error' in data['status']
        assert (
            f'No gpx file for this activity (id: {activity_uuid})'
            in data['message']
        )

    def test_it_returns_404_if_activity_have_no_chart_data(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        activity_uuid = activity_cycling_user_1.uuid.hex
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{activity_uuid}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'error' in data['status']
        assert (
            f'No gpx file for this activity (id: {activity_uuid})'
            in data['message']
        )

    def test_it_returns_500_on_getting_gpx_if_an_activity_has_invalid_gpx_pathname(  # noqa
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        activity_cycling_user_1.gpx = "some path"
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{activity_cycling_user_1.uuid.hex}/gpx',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'internal error' in data['message']
        assert 'data' not in data

    def test_it_returns_500_on_getting_chart_data_if_an_activity_has_invalid_gpx_pathname(  # noqa
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        activity_cycling_user_1.gpx = 'some path'
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/activities/{activity_cycling_user_1.uuid.hex}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert 'internal error' in data['message']
        assert 'data' not in data

    def test_it_returns_404_if_activity_has_no_map(self, app, user_1):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.get(
            f'/api/activities/map/{uuid4().hex}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 404
        assert 'error' in data['status']
        assert 'Map does not exist' in data['message']

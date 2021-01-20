import json
from uuid import uuid4

from flask import Flask

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from .utils import get_random_short_id


class TestGetWorkouts:
    def test_it_gets_all_workouts_for_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_2: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert 'test' == data['data']['workouts'][0]['user']
        assert 2 == data['data']['workouts'][0]['sport_id']
        assert 12.0 == data['data']['workouts'][0]['distance']
        assert '1:40:00' == data['data']['workouts'][0]['duration']

        assert 'creation_date' in data['data']['workouts'][1]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert 'test' == data['data']['workouts'][1]['user']
        assert 1 == data['data']['workouts'][1]['sport_id']
        assert 10.0 == data['data']['workouts'][1]['distance']
        assert '1:00:00' == data['data']['workouts'][1]['duration']

    def test_it_gets_no_workouts_for_authenticated_user_with_no_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='toto@toto.com', password='87654321')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 0

    def test_it_returns_401_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get('/api/workouts')

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert 'error' in data['status']
        assert 'Provide a valid auth token.' in data['message']


class TestGetWorkoutsWithPagination:
    def test_it_gets_workouts_with_default_pagination(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:50:00' == data['data']['workouts'][0]['duration']
        assert 'creation_date' in data['data']['workouts'][4]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )
        assert '0:17:04' == data['data']['workouts'][4]['duration']

    def test_it_gets_first_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?page=1',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:50:00' == data['data']['workouts'][0]['duration']
        assert 'creation_date' in data['data']['workouts'][4]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )
        assert '0:17:04' == data['data']['workouts'][4]['duration']

    def test_it_gets_second_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?page=2',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:57:36' == data['data']['workouts'][0]['duration']
        assert 'creation_date' in data['data']['workouts'][1]
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert '0:17:04' == data['data']['workouts'][1]['duration']

    def test_it_gets_empty_third_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?page=3',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 0

    def test_it_returns_error_on_invalid_page_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?page=A',
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

    def test_it_gets_5_workouts_per_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?per_page=10',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 7
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['workouts'][6]['workout_date']
        )

    def test_it_gets_3_workouts_per_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?per_page=3',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 3
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][2]['workout_date']
        )


class TestGetWorkoutsWithFilters:
    def test_it_gets_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?from=2018-02-01&to=2018-02-28',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:10:00' == data['data']['workouts'][0]['duration']
        assert 'creation_date' in data['data']['workouts'][1]
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert '0:16:40' == data['data']['workouts'][1]['duration']

    def test_it_gets_no_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?from=2018-03-01&to=2018-03-30',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 0

    def test_if_gets_workouts_with_date_filter_from(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?from=2018-04-01',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )

    def test_it_gets_workouts_with_date_filter_to(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?to=2017-12-31',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )

    def test_it_gets_workouts_with_ascending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?order=asc',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )

    def test_it_gets_workouts_with_distance_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?distance_from=5&distance_to=8',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )

    def test_it_gets_workouts_with_duration_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?duration_from=00:52&duration_to=01:20',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )

    def test_it_gets_workouts_with_average_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?ave_speed_from=5&ave_speed_to=10',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )

    def test_it_gets_workouts_with_max_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.max_speed = 25
        workout_running_user_1.max_speed = 11
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?max_speed_from=10&max_speed_to=20',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )

    def test_it_gets_workouts_with_sport_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?sport_id=2',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )


class TestGetWorkoutsWithFiltersAndPagination:
    def test_it_gets_page_2_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?from=2017-01-01&page=2',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 20 Mar 2017 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )

    def test_it_get_page_2_with_date_filter_and_ascending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            '/api/workouts?from=2017-01-01&page=2&order=asc',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )


class TestGetWorkout:
    def test_it_gets_an_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert 'test' == data['data']['workouts'][0]['user']
        assert 1 == data['data']['workouts'][0]['sport_id']
        assert 10.0 == data['data']['workouts'][0]['distance']
        assert '1:00:00' == data['data']['workouts'][0]['duration']

    def test_it_returns_403_if_workout_belongs_to_a_different_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_2.short_id}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{get_random_short_id()}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_on_getting_gpx_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = get_random_short_id()
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{random_short_id}/gpx',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'Workout not found (id: {random_short_id})' in data['message']
        assert data['data']['gpx'] == ''

    def test_it_returns_404_on_getting_chart_data_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = get_random_short_id()
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{random_short_id}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'Workout not found (id: {random_short_id})' in data['message']
        assert data['data']['chart_data'] == ''

    def test_it_returns_404_on_getting_gpx_if_workout_have_no_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{workout_short_id}/gpx',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert (
            f'No gpx file for this workout (id: {workout_short_id})'
            in data['message']
        )

    def test_it_returns_404_if_workout_have_no_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_short_id = workout_cycling_user_1.short_id
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert (
            f'No gpx file for this workout (id: {workout_short_id})'
            in data['message']
        )

    def test_it_returns_500_on_getting_gpx_if_an_workout_has_invalid_gpx_pathname(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_1.short_id}/gpx',
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
        assert 'data' not in data

    def test_it_returns_500_on_getting_chart_data_if_an_workout_has_invalid_gpx_pathname(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = 'some path'
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_1.short_id}/chart_data',
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
        assert 'data' not in data

    def test_it_returns_404_if_workout_has_no_map(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.get(
            f'/api/workouts/map/{uuid4().hex}',
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'Map does not exist' in data['message']

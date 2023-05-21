import json
from datetime import timedelta
from typing import List
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestGetWorkouts(ApiTestCaseMixin):
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert 2 == data['data']['workouts'][0]['sport_id']
        assert 12.0 == data['data']['workouts'][0]['distance']
        assert '1:40:00' == data['data']['workouts'][0]['duration']

        assert 'creation_date' in data['data']['workouts'][1]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert data['data']['workouts'][1]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert 1 == data['data']['workouts'][1]['sport_id']
        assert 10.0 == data['data']['workouts'][1]['distance']
        assert '1:00:00' == data['data']['workouts'][1]['duration']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            '/api/workouts',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 0,
            'total': 0,
        }

    def test_it_returns_401_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get('/api/workouts')

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert 'error' in data['status']
        assert 'provide a valid auth token' in data['message']

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
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

        response = client.get(
            '/api/workouts',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetWorkoutsWithPagination(ApiTestCaseMixin):
    def test_it_gets_workouts_with_default_pagination(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_first_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?page=1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_second_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_empty_third_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?page=3',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 3,
            'pages': 2,
            'total': 7,
        }

    def test_it_returns_error_on_invalid_page_value(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?page=A',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'error, please try again or contact the administrator'
            in data['message']
        )

    @patch('fittrackee.workouts.workouts.MAX_WORKOUTS_PER_PAGE', 6)
    def test_it_gets_max_workouts_per_page_if_per_page_exceeds_max(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?per_page=10',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 6
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][5]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    @patch('fittrackee.workouts.workouts.MAX_WORKOUTS_PER_PAGE', 6)
    def test_it_gets_given_number_of_workouts_per_page(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?per_page=3',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
            'Fri, 23 Feb 2018 10:00:00 GMT'
            == data['data']['workouts'][2]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 3,
            'total': 7,
        }


class TestGetWorkoutsWithOrder(ApiTestCaseMixin):
    def test_it_gets_workouts_with_default_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_workouts_with_ascending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
            'Fri, 23 Feb 2018 10:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_workouts_with_descending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }


class TestGetWorkoutsWithOrderBy(ApiTestCaseMixin):
    def test_it_gets_workouts_ordered_by_workout_date(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?order_by=workout_date',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][4]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_workouts_ordered_by_distance(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?order_by=distance',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert 10 == data['data']['workouts'][0]['distance']
        assert 8 == data['data']['workouts'][4]['distance']
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_workouts_ordered_by_moving_time(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        seven_workouts_user_1[6].duration = seven_workouts_user_1[
            6
        ].moving + timedelta(seconds=1000)
        db.session.commit()

        response = client.get(
            '/api/workouts?order_by=duration',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert '1:40:00' == data['data']['workouts'][0]['duration']
        assert '1:40:00' == data['data']['workouts'][0]['moving']
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:57:36' == data['data']['workouts'][1]['duration']
        assert '0:57:36' == data['data']['workouts'][1]['moving']
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert '1:06:40' == data['data']['workouts'][2]['duration']
        assert '0:50:00' == data['data']['workouts'][2]['moving']
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][2]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_workouts_ordered_by_average_speed(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?order_by=ave_speed',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert 36 == data['data']['workouts'][0]['ave_speed']
        assert 10.42 == data['data']['workouts'][4]['ave_speed']
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }


class TestGetWorkoutsWithFilters(ApiTestCaseMixin):
    def test_it_gets_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?from=2018-02-01&to=2018-02-28',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Fri, 23 Feb 2018 10:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:10:00' == data['data']['workouts'][0]['duration']
        assert 'creation_date' in data['data']['workouts'][1]
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
        assert '0:16:40' == data['data']['workouts'][1]['duration']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    def test_it_gets_no_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?from=2018-03-01&to=2018-03-30',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 0,
            'total': 0,
        }

    def test_if_gets_workouts_with_date_filter_from(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?from=2018-04-01',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    def test_it_gets_workouts_with_date_filter_to(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?to=2017-12-31',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    def test_it_gets_workouts_with_distance_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?distance_from=5&distance_to=8.1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    def test_it_gets_workouts_with_duration_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?duration_from=00:52&duration_to=01:20',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Thu, 01 Jun 2017 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_gets_workouts_with_average_speed_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?ave_speed_from=5&ave_speed_to=10',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Fri, 23 Feb 2018 10:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?max_speed_from=10&max_speed_to=20',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_gets_workouts_with_sport_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?sport_id=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            'Sun, 01 Apr 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_gets_one_workout_with_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?title=3 of 7',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        workouts = data['data']['workouts']
        assert len(workouts) == 1
        assert 'Workout 3 of 7' == workouts[0]['title']
        assert 'Mon, 01 Jan 2018 00:00:00 GMT' == workouts[0]['workout_date']

    def test_it_gets_no_workouts_with_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?title=no_such_title',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        workouts = data['data']['workouts']
        assert len(workouts) == 0


class TestGetWorkoutsWithFiltersAndPagination(ApiTestCaseMixin):
    def test_it_gets_page_2_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?from=2017-01-01&page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 7,
        }

    def test_it_get_page_2_with_date_filter_and_ascending_order(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?from=2017-01-01&page=2&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
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
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 7,
        }

    def test_it_gets_all_workouts_with_title_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?title=of 7',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 5
        assert (
            'Wed, 09 May 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 7,
        }

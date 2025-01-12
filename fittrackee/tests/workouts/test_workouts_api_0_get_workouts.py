import json
from datetime import datetime, timedelta
from typing import List
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..utils import OAUTH_SCOPES, jsonify_dict
from .mixins import WorkoutApiTestCaseMixin


class TestGetWorkouts(WorkoutApiTestCaseMixin):
    def test_it_gets_minimal_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
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
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user=user_1)
        )

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
            'Mon, 02 Apr 2018 00:00:00 GMT'
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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        suspended_user: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.get(
            '/api/workouts',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_gets_only_unsuspended_workouts_for_authenticated_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['id']
            == workout_running_user_1.short_id
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

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


class TestGetWorkoutsWithPagination(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_with_default_pagination(
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
        assert '1:00:00' == data['data']['workouts'][0]['duration']
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
        seven_workouts_user_1: List[Workout],
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
        assert '1:00:00' == data['data']['workouts'][0]['duration']
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 31 Dec 2017 23:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert '0:57:36' == data['data']['workouts'][0]['duration']
        assert 'creation_date' in data['data']['workouts'][1]
        assert (
            'Sun, 02 Apr 2017 22:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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
        seven_workouts_user_1: List[Workout],
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 31 Dec 2017 23:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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


class TestGetWorkoutsWithOrder(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_with_default_order(
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 02 Apr 2017 22:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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


class TestGetWorkoutsWithOrderBy(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_ordered_by_workout_date(
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 31 Dec 2017 23:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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


class TestGetWorkoutsWithFilters(WorkoutApiTestCaseMixin):
    def test_it_gets_workouts_with_date_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        equipment_bike_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[1].equipments = [equipment_bike_user_1]
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
        seven_workouts_user_1: List[Workout],
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
        seven_workouts_user_1: List[Workout],
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 31 Dec 2017 23:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Sun, 02 Apr 2017 22:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 02 Apr 2017 22:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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
            'Sun, 31 Dec 2017 23:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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
            'Mon, 02 Apr 2018 00:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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
            'Mon, 02 Apr 2018 00:00:00 GMT'
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

    def test_it_gets_workouts_with_equipment_id_filter(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        workout_running_user_1: Workout,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[1].equipments = [equipment_bike_user_1]
        seven_workouts_user_1[3].equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?equipment_id={equipment_bike_user_1.short_id}",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            seven_workouts_user_1[1].short_id
            == data['data']['workouts'][0]['id']
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_gets_workouts_without_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        sport_2_running: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        seven_workouts_user_1[3].equipments = [equipment_bike_user_1]
        seven_workouts_user_1[5].equipments = [equipment_shoes_user_1]
        seven_workouts_user_1[6].equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?equipment_id=none",
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 4
        assert (
            seven_workouts_user_1[4].short_id
            == data['data']['workouts'][0]['id']
        )
        assert (
            seven_workouts_user_1[2].short_id
            == data['data']['workouts'][1]['id']
        )

        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 4,
        }

    def test_it_gets_workouts_with_notes_filter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        notes = self.random_string()
        seven_workouts_user_1[1].notes = notes
        seven_workouts_user_1[3].notes = self.random_string()
        seven_workouts_user_1[5].notes = (
            f"{self.random_string()} {notes.upper()} "
            f"{self.random_string()}"
        )
        workout_cycling_user_2.notes = notes
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?notes={notes}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        workouts = data['data']['workouts']
        assert len(workouts) == 2
        assert workouts[0]['id'] == seven_workouts_user_1[5].short_id
        assert workouts[1]['id'] == seven_workouts_user_1[1].short_id

    def test_it_returns_all_workouts_when_notes_filter_is_empty_string(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.notes = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?notes=",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        workouts = data['data']['workouts']
        assert len(workouts) == 2
        assert workouts[0]['id'] == workout_running_user_1.short_id
        assert workouts[1]['id'] == workout_cycling_user_1.short_id

    def test_it_gets_workouts_with_description_filter(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        seven_workouts_user_1: List[Workout],
        workout_cycling_user_2: Workout,
    ) -> None:
        description = self.random_string()
        seven_workouts_user_1[1].description = description
        seven_workouts_user_1[3].description = self.random_string()
        seven_workouts_user_1[5].description = (
            f"{self.random_string()} {description.upper()} "
            f"{self.random_string()}"
        )
        workout_cycling_user_2.description = description
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/workouts?description={description}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        workouts = data['data']['workouts']
        assert len(workouts) == 2
        assert workouts[0]['id'] == seven_workouts_user_1[5].short_id
        assert workouts[1]['id'] == seven_workouts_user_1[1].short_id

    def test_it_returns_all_workouts_when_description_filter_is_empty_string(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.description = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/workouts?description=",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        workouts = data['data']['workouts']
        assert len(workouts) == 2
        assert workouts[0]['id'] == workout_running_user_1.short_id
        assert workouts[1]['id'] == workout_cycling_user_1.short_id


class TestGetWorkoutsWithFiltersAndPagination(WorkoutApiTestCaseMixin):
    def test_it_gets_page_2_with_date_filter(
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
            '/api/workouts?from=2017-01-01&page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 2
        assert (
            'Sun, 31 Dec 2017 23:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert (
            'Sun, 02 Apr 2017 22:00:00 GMT'
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
        seven_workouts_user_1: List[Workout],
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


class TestGetWorkoutsWithEquipments(WorkoutApiTestCaseMixin):
    @pytest.mark.parametrize('input_params', ['', '?return_equipments=false'])
    def test_it_returns_workout_without_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
        input_params: str,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts{input_params}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['workouts'][0]['equipments'] == []

    def test_it_returns_workout_with_equipments_when_flag_is_true(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/workouts?return_equipments=true',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['data']['workouts'][0]['equipments'] == [
            jsonify_dict(equipment_bike_user_1.serialize())
        ]

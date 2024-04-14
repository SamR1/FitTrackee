import json
from datetime import timedelta
from typing import List
from unittest.mock import patch
from uuid import uuid4

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestGetWorkouts(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get('/api/workouts')

        self.assert_401(response)

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
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_running_user_1.serialize()
        )
        assert data['data']['workouts'][1] == jsonify_dict(
            workout_cycling_user_1.serialize()
        )
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

        self.assert_401(response, 'provide a valid auth token')

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
        assert data['data']['workouts'][0] == jsonify_dict(
            seven_workouts_user_1[6].serialize()
        )
        assert data['data']['workouts'][1] == jsonify_dict(
            seven_workouts_user_1[5].serialize()
        )
        assert data['data']['workouts'][2] == jsonify_dict(
            seven_workouts_user_1[3].serialize()
        )
        assert data['data']['workouts'][3] == jsonify_dict(
            seven_workouts_user_1[4].serialize()
        )
        assert data['data']['workouts'][4] == jsonify_dict(
            seven_workouts_user_1[2].serialize()
        )

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
        assert data['data']['workouts'][0] == jsonify_dict(
            seven_workouts_user_1[6].serialize()
        )
        assert data['data']['workouts'][1] == jsonify_dict(
            seven_workouts_user_1[5].serialize()
        )
        assert data['data']['workouts'][2] == jsonify_dict(
            seven_workouts_user_1[3].serialize()
        )
        assert data['data']['workouts'][3] == jsonify_dict(
            seven_workouts_user_1[4].serialize()
        )
        assert data['data']['workouts'][4] == jsonify_dict(
            seven_workouts_user_1[2].serialize()
        )
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
        assert data['data']['workouts'][0] == jsonify_dict(
            seven_workouts_user_1[1].serialize()
        )
        assert data['data']['workouts'][1] == jsonify_dict(
            seven_workouts_user_1[0].serialize()
        )
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

        self.assert_500(response)

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
        assert data['data']['workouts'][0] == jsonify_dict(
            seven_workouts_user_1[6].serialize()
        )
        assert data['data']['workouts'][5] == jsonify_dict(
            seven_workouts_user_1[1].serialize()
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
        assert data['data']['workouts'][0] == jsonify_dict(
            seven_workouts_user_1[6].serialize()
        )
        assert data['data']['workouts'][1] == jsonify_dict(
            seven_workouts_user_1[5].serialize()
        )
        assert data['data']['workouts'][2] == jsonify_dict(
            seven_workouts_user_1[3].serialize()
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


class TestGetWorkoutsWithOrderBy(ApiTestCaseMixin):
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


class TestGetWorkoutsWithFilters(ApiTestCaseMixin):
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
        assert (
            'Fri, 23 Feb 2018 00:00:00 GMT'
            == data['data']['workouts'][1]['workout_date']
        )
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


class TestGetWorkoutsWithFiltersAndPagination(ApiTestCaseMixin):
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


class TestGetWorkout(ApiTestCaseMixin):
    def test_it_gets_a_workout(
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
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_cycling_user_1.serialize()
        )

    def test_it_returns_403_if_workout_belongs_to_a_different_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_2.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{self.random_short_id()}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_on_getting_gpx_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{random_short_id}/gpx',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
        assert data['data']['gpx'] == ''

    def test_it_returns_404_on_getting_chart_data_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{random_short_id}/chart_data',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
        assert data['data']['chart_data'] == ''

    def test_it_returns_404_on_getting_gpx_if_workout_have_no_gpx(
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

        response = client.get(
            f'/api/workouts/{workout_short_id}/gpx',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response, f'no gpx file for this workout (id: {workout_short_id})'
        )

    def test_it_returns_404_if_workout_have_no_chart_data(
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

        response = client.get(
            f'/api/workouts/{workout_short_id}/chart_data',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response, f'no gpx file for this workout (id: {workout_short_id})'
        )

    def test_it_returns_500_on_getting_gpx_if_a_workout_has_invalid_gpx_pathname(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_1.short_id}/gpx',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_500(response)
        assert 'data' not in data

    def test_it_returns_500_on_getting_chart_data_if_a_workout_has_invalid_gpx_pathname(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = 'some path'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_1.short_id}/chart_data',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_500(response)
        assert 'data' not in data

    def test_it_returns_404_if_workout_has_no_map(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.get(
            f'/api/workouts/map/{uuid4().hex}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'Map does not exist')

    def test_it_returns_404_if_map_file_not_found(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        map_ip = self.random_string()
        workout_cycling_user_1.map = self.random_string()
        workout_cycling_user_1.map_id = map_ip
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/map/{map_ip}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'Map file does not exist')

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
    )
    @pytest.mark.parametrize(
        'endpoint',
        [
            '/api/workouts/{workout_short_id}',
            '/api/workouts/{workout_short_id}/gpx',
            '/api/workouts/{workout_short_id}/chart_data',
            '/api/workouts/{workout_short_id}/gpx/segment/1',
            '/api/workouts/{workout_short_id}/chart_data/segment/1',
        ],
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        client_scope: str,
        can_access: bool,
        endpoint: str,
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
            endpoint.format(workout_short_id=workout_cycling_user_1.short_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestDownloadWorkoutGpx(ApiTestCaseMixin):
    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{self.random_short_id()}/gpx/download',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'workout not found')

    def test_it_returns_404_if_workout_does_not_have_gpx(
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
            f'/api/workouts/{workout_cycling_user_1.short_id}/gpx/download',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'no gpx file for workout')

    def test_it_returns_404_if_workout_belongs_to_a_different_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/workouts/{workout_cycling_user_2.short_id}/gpx/download',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(response, 'workout not found')

    def test_it_calls_send_from_directory_if_workout_has_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_file_path = 'file.gpx'
        workout_cycling_user_1.gpx = gpx_file_path
        with patch('fittrackee.workouts.workouts.send_from_directory') as mock:
            mock.return_value = 'file'
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            client.get(
                (
                    f'/api/workouts/{workout_cycling_user_1.short_id}/'
                    'gpx/download'
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        mock.assert_called_once_with(
            app.config['UPLOAD_FOLDER'],
            gpx_file_path,
            mimetype='application/gpx+xml',
            as_attachment=True,
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:read': True}.items(),
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

        response = client.get(
            f'/api/workouts/{workout_cycling_user_1.short_id}/gpx/download',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

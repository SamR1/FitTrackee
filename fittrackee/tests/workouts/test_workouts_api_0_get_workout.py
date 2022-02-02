import json
from typing import List
from unittest.mock import mock_open, patch

import pytest
from flask import Flask

from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

from ..test_case_mixins import ApiTestCaseMixin
from ..utils import jsonify_dict, random_string
from .utils import get_random_short_id


class GetWorkoutGpxAsFollowerMixin:
    @staticmethod
    def init_test_data(
        workout: Workout,
        map_visibility: PrivacyLevel,
        follower: User,
        followed: User,
    ) -> None:
        workout.gpx = 'file.gpx'
        workout.workout_visibility = PrivacyLevel.FOLLOWERS
        workout.map_visibility = map_visibility
        followed.approves_follow_request_from(follower)


class GetWorkoutGpxPublicVisibilityMixin:
    @staticmethod
    def init_test_data(workout: Workout, map_visibility: PrivacyLevel) -> None:
        workout.gpx = 'file.gpx'
        workout.workout_visibility = PrivacyLevel.PUBLIC
        workout.map_visibility = map_visibility


class GetWorkoutTestCase(ApiTestCaseMixin):
    route = '/api/workouts/{workout_uuid}'


class TestGetWorkoutAsWorkoutOwner(GetWorkoutTestCase):
    def test_it_gets_owner_workout(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert 'creation_date' in data['data']['workouts'][0]
        assert (
            'Mon, 01 Jan 2018 00:00:00 GMT'
            == data['data']['workouts'][0]['workout_date']
        )
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert 1 == data['data']['workouts'][0]['sport_id']
        assert 10.0 == data['data']['workouts'][0]['distance']
        assert '1:00:00' == data['data']['workouts'][0]['duration']
        assert 'private' == data['data']['workouts'][0]['map_visibility']
        assert 'private' == data['data']['workouts'][0]['workout_visibility']


class TestGetWorkoutAsFollower(GetWorkoutTestCase):
    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert len(data['data']['workouts']) == 0

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: follower', PrivacyLevel.FOLLOWERS),
            ('workout visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout(
        self,
        input_desc: str,
        input_workout_level: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_2.serialize()
        )
        assert 'map_visibility' not in data['data']['workouts'][0]
        assert 'workout_visibility' not in data['data']['workouts'][0]


class TestGetWorkoutAsUser(GetWorkoutTestCase):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=get_random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert len(data['data']['workouts']) == 0

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE),
            ('workout visibility: follower', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_level: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert len(data['data']['workouts']) == 0

    def test_it_returns_another_user_workout_when_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_2.serialize()
        )
        assert 'map_visibility' not in data['data']['workouts'][0]
        assert 'workout_visibility' not in data['data']['workouts'][0]


class TestGetWorkoutAsUnauthenticatedUser(GetWorkoutTestCase):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=get_random_short_id()),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert len(data['data']['workouts']) == 0

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: private', PrivacyLevel.PRIVATE),
            ('workout visibility: follower', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_workout_visibility_is_not_public(
        self,
        input_desc: str,
        input_workout_level: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_level
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert len(data['data']['workouts']) == 0

    def test_it_returns_a_user_workout_when_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert data['data']['workouts'][0]['user'] == jsonify_dict(
            user_1.serialize()
        )
        assert 'map_visibility' not in data['data']['workouts'][0]
        assert 'workout_visibility' not in data['data']['workouts'][0]


class GetWorkoutGpxTestCase(ApiTestCaseMixin):
    route = '/api/workouts/{workout_uuid}/gpx'


class TestGetWorkoutGpxAsWorkoutOwner(GetWorkoutGpxTestCase):
    def test_it_returns_404_if_workout_have_no_gpx(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert (
            'no gpx file for this workout (id: '
            f'{workout_cycling_user_1.short_id})'
        ) in data['message']

    def test_it_returns_owner_workout_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = random_string()
        workout_cycling_user_1.gpx = 'file.gpx'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open', new_callable=mock_open, read_data=gpx_content
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['gpx'] == gpx_content


class TestGetWorkoutGpxAsFollower(
    GetWorkoutGpxTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_2, PrivacyLevel.PRIVATE, user_1, user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open', new_callable=mock_open, read_data=random_string()
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
            ('map visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_followed_user_workout_gpx(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_2, input_map_visibility, user_1, user_2
        )
        gpx_content = random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open', new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['gpx'] == gpx_content


class TestGetWorkoutGpxAsUser(
    GetWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = get_random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['gpx'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, input_map_visibility)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open', new_callable=mock_open, read_data=random_string()
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, PrivacyLevel.PUBLIC)
        gpx_content = random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open', new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['gpx'] == gpx_content


class TestGetWorkoutGpxAsUnauthenticatedUser(
    GetWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = get_random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['gpx'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, input_map_visibility)
        client = app.test_client()
        with patch(
            'builtins.open', new_callable=mock_open, read_data=random_string()
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = random_string()
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client = app.test_client()
        with patch(
            'builtins.open', new_callable=mock_open, read_data=gpx_content
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['gpx'] == gpx_content


class GetGetWorkoutChartDataTestCase(ApiTestCaseMixin):
    route = '/api/workouts/{workout_uuid}/chart_data'


class TestGetWorkoutChartDataAsWorkoutOwner(GetGetWorkoutChartDataTestCase):
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
            self.route.format(workout_uuid=workout_short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert (
            f'no gpx file for this workout (id: {workout_short_id})'
            in data['message']
        )

    def test_it_returns_500_if_a_workout_has_invalid_gpx_pathname(
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'error, please try again or contact the administrator'
            in data['message']
        )
        assert 'data' not in data

    def test_it_returns_owner_workout_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_1.gpx = 'file.gpx'
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutChartDataAsFollower(
    GetGetWorkoutChartDataTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_2, PrivacyLevel.PRIVATE, user_1, user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
            ('map visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_chart_data_for_followed_user_workout(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_2, input_map_visibility, user_1, user_2
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_2.gpx = 'file.gpx'
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutChartDataAsUser(
    GetGetWorkoutChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = get_random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['chart_data'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, input_map_visibility)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_chart_data_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, PrivacyLevel.PUBLIC)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_2.gpx = 'file.gpx'
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutChartDataAsUnauthenticatedUser(
    GetGetWorkoutChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = get_random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['chart_data'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, input_map_visibility)
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_chart_data_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        chart_data: List = []
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client = app.test_client()
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class GetWorkoutSegmentGpxTestCase(ApiTestCaseMixin):
    route = '/api/workouts/{workout_uuid}/gpx/segment/{segment_id}'


class TestGetWorkoutSegmentGpxAsWorkoutOwner(GetWorkoutSegmentGpxTestCase):
    def test_it_returns_404_if_workout_have_no_gpx(
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
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert (
            f'no gpx file for this workout (id: {workout_short_id})'
            in data['message']
        )

    def test_it_returns_404_if_segment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id,
                    segment_id=100,
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert "No segment with id '100'" in data['message']

    def test_it_gets_segment_gpx_for_owner_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert '<trkpt lat="44.68095" lon="6.07367">' in data['data']['gpx']


class TestGetWorkoutSegmentGpxAsFollower(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_1, PrivacyLevel.PRIVATE, user_2, user_1
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']
        assert data['data']['gpx'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
            ('map visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_segment_gpx_for_followed_user_workout(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_1, input_map_visibility, user_2, user_1
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert '<trkpt lat="44.68095" lon="6.07367">' in data['data']['gpx']


class TestGetWorkoutSegmentGpxAsUser(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = get_random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['gpx'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, input_map_visibility)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']
        assert data['data']['gpx'] == ''

    def test_it_returns_segment_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert '<trkpt lat="44.68095" lon="6.07367">' in data['data']['gpx']


class TestGetWorkoutSegmentGpxAsUnauthenticatedUser(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = get_random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['gpx'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, input_map_visibility)
        client = app.test_client()
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
            )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']
        assert data['data']['gpx'] == ''

    def test_it_returns_segment_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client = app.test_client()
        with patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=gpx_file_with_segments,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert '<trkpt lat="44.68095" lon="6.07367">' in data['data']['gpx']


class GetWorkoutSegmentChartDataTestCase(ApiTestCaseMixin):
    route = '/api/workouts/{workout_uuid}/chart_data/segment/{segment_id}'


class TestGetWorkoutSegmentChartDataAsWorkoutOwner(
    GetWorkoutSegmentChartDataTestCase
):
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
            self.route.format(workout_uuid=workout_short_id, segment_id=1),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert (
            f'no gpx file for this workout (id: {workout_short_id})'
            in data['message']
        )

    def test_it_returns_500_if_workout_has_invalid_gpx_pathname(
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
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'error, please try again or contact the administrator'
            in data['message']
        )
        assert 'data' not in data

    def test_it_returns_chart_data(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        chart_data: List = []
        workout_cycling_user_1.gpx = 'file.gpx'
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutSegmentChartDataAsFollower(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxAsFollowerMixin
):
    def test_it_returns_404_when_map_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_1, PrivacyLevel.PRIVATE, user_2, user_1
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
            ('map visibility: public', PrivacyLevel.PUBLIC),
        ],
    )
    def test_it_returns_chart_data_for_follower_user_workout(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_1, input_map_visibility, user_2, user_1
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        chart_data: List = []
        workout_cycling_user_1.gpx = 'file.gpx'
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutSegmentChartDataAsUser(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = get_random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['chart_data'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, input_map_visibility)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_chart_data_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        chart_data: List = []
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        workout_cycling_user_1.gpx = 'file.gpx'
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutSegmentChartDataAsUnauthenticatedUser(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = get_random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert f'workout not found (id: {random_short_id})' in data['message']
        assert data['data']['chart_data'] == ''

    @pytest.mark.parametrize(
        'input_desc,input_map_visibility',
        [
            ('map visibility: private', PrivacyLevel.PRIVATE),
            ('map visibility: followers_only', PrivacyLevel.FOLLOWERS),
        ],
    )
    def test_it_returns_404_when_map_visibility_is_not_public(
        self,
        input_desc: str,
        input_map_visibility: PrivacyLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, input_map_visibility)
        client = app.test_client()

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_chart_data_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        chart_data: List = []
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client = app.test_client()
        with patch('builtins.open', new_callable=mock_open), patch(
            'fittrackee.workouts.workouts.get_chart_data',
            return_value=chart_data,
        ):

            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id, segment_id=1
                ),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['chart_data'] == chart_data


class TestGetWorkoutMap(ApiTestCaseMixin):
    def test_it_returns_404_if_workout_has_no_map(self, app: Flask) -> None:
        client = app.test_client()
        response = client.get(
            f'/api/workouts/map/{random_string()}',
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'Map does not exist' in data['message']

    def test_it_calls_send_from_directory_if_workout_has_map(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        map_id = random_string()
        map_file_path = random_string()
        workout_cycling_user_1.map_id = map_id
        workout_cycling_user_1.map = map_file_path
        client = app.test_client()
        with patch(
            'fittrackee.workouts.workouts.send_from_directory',
            return_value='file',
        ) as mock:

            response = client.get(
                f'/api/workouts/map/{map_id}',
            )

        assert response.status_code == 200
        mock.assert_called_once_with(
            app.config['UPLOAD_FOLDER'], map_file_path
        )


class DownloadWorkoutGpxTestCase(ApiTestCaseMixin):
    route = '/api/workouts/{workout_uuid}/gpx/download'


class TestDownloadWorkoutGpxAsWorkoutOwner(DownloadWorkoutGpxTestCase):
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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'no gpx file for workout' in data['message']

    def test_it_calls_send_from_directory_if_workout_has_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_file_path = 'file.gpx'
        workout_cycling_user_1.gpx = 'file.gpx'
        with patch(
            'fittrackee.workouts.workouts.send_from_directory',
            return_value='file',
        ) as mock:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        mock.assert_called_once_with(
            app.config['UPLOAD_FOLDER'],
            gpx_file_path,
            mimetype='application/gpx+xml',
            as_attachment=True,
        )


class TestDownloadWorkoutGpxAsFollower(DownloadWorkoutGpxTestCase):
    def test_it_returns_404_for_followed_user_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.gpx = 'file.gpx'
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.map_visibility = PrivacyLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']


class TestDownloadWorkoutGpxAsUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=get_random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']

    def test_it_returns_404_for_another_user_workout(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, PrivacyLevel.PUBLIC)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'workout not found' in data['message']


class TestDownloadWorkoutGpxAsUnauthenticatedUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_1, PrivacyLevel.PUBLIC)
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 401
        assert 'error' in data['status']
        assert 'provide a valid auth token' in data['message']

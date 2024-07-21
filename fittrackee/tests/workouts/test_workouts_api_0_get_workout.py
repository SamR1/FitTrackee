import json
from datetime import datetime
from typing import List
from unittest.mock import mock_open, patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.tests.comments.mixins import CommentMixin
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout, WorkoutSegment

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


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
    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

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
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user_1)
        )

    def test_it_gets_owner_suspended_workout(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.suspended_at = datetime.utcnow()
        db.session.commit()
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
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_cycling_user_1.serialize(user_1)
        )


class TestGetWorkoutAsFollower(CommentMixin, GetWorkoutTestCase):
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

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_when_workout_is_suspended_and_no_user_comments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
        follow_request_from_user_3_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        user_2.approves_follow_request_from(user_3)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        self.create_comment(
            user_3,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_when_workout_is_suspended_and_auth_user_commented_workout(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )
        db.session.commit()
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
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_cycling_user_2.serialize(user_1)
        )

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
        assert (
            data['data']['workouts'][0]['map_visibility']
            == PrivacyLevel.PRIVATE.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == input_workout_level
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = PrivacyLevel.FOLLOWERS
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


class TestGetWorkoutAsUser(CommentMixin, GetWorkoutTestCase):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_when_workout_is_suspended_and_no_user_comments(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        self.create_comment(
            user_3, workout_cycling_user_2, text_visibility=PrivacyLevel.PUBLIC
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_when_workout_is_suspended_and_auth_user_commented_workout(  # noqa
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_2.suspended_at = datetime.utcnow()
        self.create_comment(
            user_1,
            workout_cycling_user_2,
            text_visibility=PrivacyLevel.PUBLIC,
        )
        db.session.commit()
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
        assert data['data']['workouts'][0] == jsonify_dict(
            workout_cycling_user_2.serialize(user_1)
        )

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

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_when_user_is_blocked_workout_owner(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        user_2.blocks_user(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
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
        assert (
            data['data']['workouts'][0]['map_visibility']
            == PrivacyLevel.PRIVATE.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == PrivacyLevel.PUBLIC.value
        )

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = PrivacyLevel.PUBLIC
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


class TestGetWorkoutAsUnauthenticatedUser(GetWorkoutTestCase):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=short_id),
        )

        data = self.assert_404(response)
        assert len(data['data']['workouts']) == 0

    def test_it_returns_404_when_workout_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        workout_cycling_user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
        )

        data = self.assert_404(response)
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

        data = self.assert_404(response)
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
        assert (
            data['data']['workouts'][0]['map_visibility']
            == PrivacyLevel.PRIVATE.value
        )
        assert (
            data['data']['workouts'][0]['workout_visibility']
            == PrivacyLevel.PUBLIC.value
        )


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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
        workout_cycling_user_1.gpx = 'file.gpx'
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
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

        self.assert_403(response)

    def test_it_returns_owner_workout_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
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
            'builtins.open',
            new_callable=mock_open,
            read_data=self.random_string(),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_2.short_id})',
        )

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
        gpx_content = self.random_string()
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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        self.init_test_data(
            workout_cycling_user_2, PrivacyLevel.FOLLOWERS, user_1, user_2
        )
        gpx_content = self.random_string()
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
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

        self.assert_403(response)


class TestGetWorkoutGpxAsUser(
    GetWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
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
            'builtins.open',
            new_callable=mock_open,
            read_data=self.random_string(),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_2.short_id
                ),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_2.short_id})',
        )

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, PrivacyLevel.PUBLIC)
        gpx_content = self.random_string()
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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        self.init_test_data(workout_cycling_user_2, PrivacyLevel.PUBLIC)
        gpx_content = self.random_string()
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
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

        self.assert_403(response)


class TestGetWorkoutGpxAsUnauthenticatedUser(
    GetWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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
            'builtins.open',
            new_callable=mock_open,
            read_data=self.random_string(),
        ):
            response = client.get(
                self.route.format(
                    workout_uuid=workout_cycling_user_1.short_id
                ),
            )

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )

    def test_it_returns_gpx_when_map_visibility_is_public(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        gpx_content = self.random_string()
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

        self.assert_500(response)

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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_2.short_id})',
        )

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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.gpx = 'file.gpx'
        self.init_test_data(
            workout_cycling_user_2, PrivacyLevel.FOLLOWERS, user_1, user_2
        )
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


class TestGetWorkoutChartDataAsUser(
    GetGetWorkoutChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_2.short_id})',
        )

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

    def test_it_returns_error_when_user_is_suspended(
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
        workout_cycling_user_2.gpx = 'file.gpx'
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


class TestGetWorkoutChartDataAsUnauthenticatedUser(
    GetGetWorkoutChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )

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

        self.assert_404_with_message(
            response, f'no gpx file for this workout (id: {workout_short_id})'
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

        self.assert_404_with_message(response, "No segment with id '100'")

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

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        gpx_file_with_segments: str,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


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

        data = self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )
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

    def test_it_returns_error_when_user_is_suspended(
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
            workout_cycling_user_1, PrivacyLevel.FOLLOWERS, user_2, user_1
        )
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
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

        self.assert_403(response)


class TestGetWorkoutSegmentGpxAsUser(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )

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

    def test_it_returns_error_when_user_is_suspended(
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
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


class TestGetWorkoutSegmentGpxAsUnauthenticatedUser(
    GetWorkoutSegmentGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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

        data = self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )
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

        self.assert_404_with_message(
            response, f'no gpx file for this workout (id: {workout_short_id})'
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

        self.assert_500(response)

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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
    ) -> None:
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(
                workout_uuid=workout_cycling_user_1.short_id, segment_id=1
            ),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)


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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )

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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        workout_cycling_user_1_segment: WorkoutSegment,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        self.init_test_data(
            workout_cycling_user_1, PrivacyLevel.FOLLOWERS, user_2, user_1
        )
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        chart_data: List = []

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

        self.assert_403(response)


class TestGetWorkoutSegmentChartDataAsUser(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )

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

    def test_it_returns_error_when_user_is_suspended(
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
        workout_cycling_user_1.gpx = 'file.gpx'
        user_2.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
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

        self.assert_403(response)


class TestGetWorkoutSegmentChartDataAsUnauthenticatedUser(
    GetWorkoutSegmentChartDataTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask
    ) -> None:
        random_short_id = self.random_short_id()
        client = app.test_client()

        response = client.get(
            self.route.format(workout_uuid=random_short_id, segment_id=1),
        )

        data = self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )
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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_1.short_id})',
        )

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
            f'/api/workouts/map/{self.random_string()}',
        )

        self.assert_404_with_message(response, 'Map does not exist')

    def test_it_calls_send_from_directory_if_workout_has_map(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        map_id = self.random_string()
        map_file_path = self.random_string()
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


class TestWorkoutScope(ApiTestCaseMixin):
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

        self.assert_404_with_message(response, 'no gpx file for workout')

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

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = 'file.gpx'
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

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
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_2.short_id})',
        )


class TestDownloadWorkoutGpxAsUser(
    DownloadWorkoutGpxTestCase, GetWorkoutGpxPublicVisibilityMixin
):
    def test_it_returns_404_if_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        random_short_id = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(workout_uuid=random_short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_message(
            response, f'workout not found (id: {random_short_id})'
        )

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

        self.assert_404_with_message(
            response,
            f'workout not found (id: {workout_cycling_user_2.short_id})',
        )


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

        self.assert_401(response)

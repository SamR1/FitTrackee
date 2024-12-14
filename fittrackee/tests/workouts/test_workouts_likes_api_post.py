import json
from datetime import datetime

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout, WorkoutLike

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestWorkoutLikePost(ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/like'

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id)
        )

        self.assert_401(response)

    def test_it_return_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=self.random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: follower', VisibilityLevel.FOLLOWERS),
            ('workout visibility: public', VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_creates_workout_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['workouts'] == [
            jsonify_dict(
                workout_cycling_user_2.serialize(user=user_1, light=False)
            )
        ]
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is not None
        )
        assert workout_cycling_user_2.likes.all() == [user_1]

    def test_it_does_not_return_error_when_like_already_exists(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        )
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['id']
            == workout_cycling_user_2.short_id
        )
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is not None
        )
        assert workout_cycling_user_2.likes.all() == [user_1]

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
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

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestWorkoutUndoLikePost(ApiTestCaseMixin, BaseTestMixin):
    route = '/api/workouts/{workout_uuid}/like/undo'

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id)
        )

        self.assert_401(response)

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
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        )
        db.session.add(like)
        db.session.flush()
        user_1.suspended_at = datetime.utcnow()
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_404_when_workout_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=self.random_short_id()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_workout_visibility_is_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PRIVATE
        user_2.approves_follow_request_from(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    def test_it_returns_404_when_user_is_not_follower(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.FOLLOWERS
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    @pytest.mark.parametrize(
        'input_desc,input_workout_level',
        [
            ('workout visibility: follower', VisibilityLevel.FOLLOWERS),
            ('workout visibility: public', VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_removes_workout_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        input_desc: str,
        input_workout_level: VisibilityLevel,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = input_workout_level
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        like = WorkoutLike(
            user_id=user_1.id, workout_id=workout_cycling_user_2.id
        )
        db.session.add(like)
        db.session.commit()

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert data['data']['workouts'] == [
            jsonify_dict(
                workout_cycling_user_2.serialize(user=user_1, light=False)
            )
        ]
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is None
        )
        assert workout_cycling_user_2.likes.all() == []

    def test_it_does_not_return_error_when_no_existing_like(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_2.short_id),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['workouts']) == 1
        assert (
            data['data']['workouts'][0]['id']
            == workout_cycling_user_2.short_id
        )
        assert (
            WorkoutLike.query.filter_by(
                user_id=user_1.id, workout_id=workout_cycling_user_2.id
            ).first()
            is None
        )
        assert workout_cycling_user_2.likes.all() == []

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
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

        response = client.post(
            self.route.format(workout_uuid=workout_cycling_user_1.short_id),
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

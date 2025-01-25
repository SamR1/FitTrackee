from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import FollowRequest, User
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..comments.mixins import CommentMixin
from ..utils import OAUTH_SCOPES
from .mixins import WorkoutApiTestCaseMixin
from .utils import post_a_workout


def get_gpx_filepath(workout_id: int) -> str:
    workout = Workout.query.filter_by(id=workout_id).first()
    return workout.gpx


class TestDeleteWorkoutWithGpx(CommentMixin, WorkoutApiTestCaseMixin):
    def test_it_deletes_a_workout_with_gpx(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        assert response.status_code == 204
        assert Workout.query.first() is None

    def test_it_deletes_a_workout_with_equipment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        equipment_bike_user_1: Equipment,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.filter_by(
            uuid=decode_short_id(workout_short_id)
        ).first()
        workout.equipments = [equipment_bike_user_1]
        db.session.commit()
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        assert response.status_code == 204
        assert Workout.query.first() is None
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

    def test_it_deletes_a_workout_with_several_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        workout_w_shoes_equipment: Workout,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.filter_by(
            uuid=decode_short_id(workout_short_id)
        ).first()
        workout.equipments = [equipment_bike_user_1, equipment_shoes_user_1]
        db.session.commit()
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {token}'),
        )

        assert response.status_code == 204
        assert Workout.query.first() == workout_w_shoes_equipment
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()
        assert equipment_shoes_user_1.total_workouts == 1
        assert (
            equipment_shoes_user_1.total_distance
            == workout_w_shoes_equipment.distance
        )
        assert (
            equipment_shoes_user_1.total_duration
            == workout_w_shoes_equipment.duration
        )
        assert equipment_shoes_user_1.total_moving == timedelta()

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', VisibilityLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                VisibilityLevel.FOLLOWERS,
                403,
            ),
            ('workout visibility: public', VisibilityLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_followed_user_user(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        _, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=input_workout_visibility
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', VisibilityLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                VisibilityLevel.FOLLOWERS,
                404,
            ),
            ('workout visibility: public', VisibilityLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_different_user(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=input_workout_visibility
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility',
        [
            ('workout visibility: private', VisibilityLevel.PRIVATE),
            (
                'workout visibility: followers_only',
                VisibilityLevel.FOLLOWERS,
            ),
            ('workout visibility: public', VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_401_when_no_authenticated(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        _, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=input_workout_visibility
        )
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
        )

        assert response.status_code == 401

    def test_it_returns_403_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        auth_token, workout_short_id = post_a_workout(
            app, gpx_file, workout_visibility=VisibilityLevel.PRIVATE
        )
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_404_if_workout_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f'/api/workouts/{self.random_short_id()}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert 'not found' in data['status']

    def test_a_workout_with_gpx_can_be_deleted_if_gpx_file_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.gpx = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_it_deletes_a_workout_with_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        gpx_file: str,
    ) -> None:
        token, workout_short_id = post_a_workout(app, gpx_file)
        workout = Workout.query.filter_by(
            uuid=decode_short_id(workout_short_id)
        ).first()
        workout.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2, workout, text_visibility=VisibilityLevel.PUBLIC
        )
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_short_id}',
            headers=dict(Authorization=f'Bearer {token}'),
        )
        assert response.status_code == 204
        assert Workout.query.first() is None
        assert comment.workout_id is None

    def test_a_workout_with_gpx_can_be_deleted_if_map_file_is_invalid(
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

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

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

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            data=dict(),
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestDeleteWorkoutWithoutGpx(CommentMixin, WorkoutApiTestCaseMixin):
    def test_it_deletes_a_workout_wo_gpx(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        assert response.status_code == 204
        assert Workout.query.first() is None

    def test_it_deletes_a_workout_with_equipment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204
        assert Workout.query.first() is None
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

    def test_it_returns_404_when_deleting_a_workout_from_different_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert 'not found' in data['status']

    def test_it_deletes_a_workout_with_comment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_1,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        assert response.status_code == 204
        assert Workout.query.first() is None
        assert comment.workout_id is None

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', VisibilityLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                VisibilityLevel.FOLLOWERS,
                403,
            ),
            ('workout visibility: public', VisibilityLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_followed_user_user(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        follow_request_from_user_2_to_user_1: FollowRequest,
    ) -> None:
        user_1.approves_follow_request_from(user_2)
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility,expected_status_code',
        [
            ('workout visibility: private', VisibilityLevel.PRIVATE, 404),
            (
                'workout visibility: followers_only',
                VisibilityLevel.FOLLOWERS,
                404,
            ),
            ('workout visibility: public', VisibilityLevel.PUBLIC, 403),
        ],
    )
    def test_it_returns_error_when_deleting_workout_from_different_user(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        expected_status_code: int,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        'input_desc,input_workout_visibility',
        [
            ('workout visibility: private', VisibilityLevel.PRIVATE),
            (
                'workout visibility: followers_only',
                VisibilityLevel.FOLLOWERS,
            ),
            ('workout visibility: public', VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_returns_401_when_no_authenticated(
        self,
        input_desc: str,
        input_workout_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
        )

        assert response.status_code == 401

    def test_it_returns_error_when_user_is_suspended(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f'/api/workouts/{workout_cycling_user_1.short_id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

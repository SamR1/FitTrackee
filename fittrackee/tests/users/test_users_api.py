import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import patch

from flask import Flask

from fittrackee.federation.models import Actor
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Sport, Workout

from ..test_case_mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestGetUserAsAdmin(ApiTestCaseMixin):
    def test_it_gets_single_user_without_workouts(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            user_2.serialize(user_1_admin)
        )

    def test_it_gets_single_user_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            user_2.serialize(user_1_admin)
        )

    def test_it_gets_authenticated_user(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/users/{user_1_admin.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            user_1_admin.serialize(user_1_admin)
        )

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/users/not_existing',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']


class TestGetUserAsUser(ApiTestCaseMixin):
    def test_it_gets_single_user_without_workouts(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            user_2.serialize(user_1)
        )

    def test_it_gets_single_user_with_workouts(
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
            f'/api/users/{user_2.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            user_2.serialize(user_1)
        )

    def test_it_gets_authenticated_user(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/users/{user_1.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(
            user_1.serialize(user_1)
        )

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/users/not_existing',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']


class TestGetUserAsUnauthenticatedUser(ApiTestCaseMixin):
    def test_it_gets_single_user_without_workouts(
        self, app: Flask, user_2: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/api/users/{user_2.username}',
            content_type='application/json',
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(user_2.serialize())

    def test_it_gets_single_user_with_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/api/users/{user_1.username}',
            content_type='application/json',
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        assert data['data']['users'][0] == jsonify_dict(user_1.serialize())

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(
            '/api/users/not_existing',
            content_type='application/json',
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 404
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']


class TestGetUsersAsAdmin(ApiTestCaseMixin):
    def test_it_gets_users_list(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert data['data']['users'][0] == jsonify_dict(
            user_1_admin.serialize(user_1_admin)
        )
        assert data['data']['users'][1] == jsonify_dict(
            user_3.serialize(user_1_admin)
        )
        assert data['data']['users'][2] == jsonify_dict(
            user_2.serialize(user_1_admin)
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert data['data']['users'][0] == jsonify_dict(
            user_1_admin.serialize(user_1_admin)
        )

        assert data['data']['users'][1] == jsonify_dict(
            user_3.serialize(user_1_admin)
        )
        assert data['data']['users'][2] == jsonify_dict(
            user_2.serialize(user_1_admin)
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    @patch('fittrackee.users.users.USERS_PER_PAGE', 2)
    def test_it_gets_first_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 3,
        }

    @patch('fittrackee.users.users.USERS_PER_PAGE', 2)
    def test_it_gets_next_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 3,
        }

    def test_it_gets_empty_next_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_user_list_with_2_per_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?per_page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 3,
        }

    def test_it_gets_next_page_on_user_list_with_2_per_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=2&per_page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'toto' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_username_ascending(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'toto' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_username_descending(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.utcnow() - timedelta(days=1)
        user_3.created_at = datetime.utcnow() - timedelta(hours=1)
        user_1_admin.created_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=created_at',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date_ascending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.utcnow() - timedelta(days=1)
        user_3.created_at = datetime.utcnow() - timedelta(hours=1)
        user_1_admin.created_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=created_at&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date_descending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.utcnow() - timedelta(days=1)
        user_3.created_at = datetime.utcnow() - timedelta(hours=1)
        user_1_admin.created_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=created_at&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'toto' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_admin_rights(
        self, app: Flask, user_2: User, user_1_admin: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=admin',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_admin_rights_ascending(
        self, app: Flask, user_2: User, user_1_admin: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=admin&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_admin_rights_descending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=admin&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'toto' in data['data']['users'][1]['username']
        assert 'sam' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=workouts_count',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 0 == data['data']['users'][0]['nb_workouts']
        assert 'sam' in data['data']['users'][1]['username']
        assert 0 == data['data']['users'][1]['nb_workouts']
        assert 'toto' in data['data']['users'][2]['username']
        assert 1 == data['data']['users'][2]['nb_workouts']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=workouts_count&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 0 == data['data']['users'][0]['nb_workouts']
        assert 'sam' in data['data']['users'][1]['username']
        assert 0 == data['data']['users'][1]['nb_workouts']
        assert 'toto' in data['data']['users'][2]['username']
        assert 1 == data['data']['users'][2]['nb_workouts']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count_descending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=workouts_count&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 1 == data['data']['users'][0]['nb_workouts']
        assert 'admin' in data['data']['users'][1]['username']
        assert 0 == data['data']['users'][1]['nb_workouts']
        assert 'sam' in data['data']['users'][2]['username']
        assert 0 == data['data']['users'][2]['nb_workouts']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_filtering_on_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=toto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert 'toto' in data['data']['users'][0]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_filtering_on_username_is_case_insensitive(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=TOTO',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert 'toto' in data['data']['users'][0]['username']

    def test_it_returns_empty_users_list_filtering_on_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=not_existing',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 0,
            'total': 0,
        }

    def test_it_users_list_with_complex_query(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username&order=desc&page=2&per_page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert 'admin' in data['data']['users'][0]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 3,
        }


class TestGetUsersAsUser(ApiTestCaseMixin):
    def test_it_gets_users_list(
        self, app: Flask, user_1: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/users',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert data['data']['users'][0] == jsonify_dict(
            user_3.serialize(user_1)
        )
        assert data['data']['users'][1] == jsonify_dict(
            user_1.serialize(user_1)
        )
        assert data['data']['users'][2] == jsonify_dict(
            user_2.serialize(user_1)
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_with_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        sport_2_running: Sport,
        workout_running_user_1: Workout,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/users',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert data['data']['users'][0] == jsonify_dict(
            user_3.serialize(user_1)
        )

        assert data['data']['users'][1] == jsonify_dict(
            user_1.serialize(user_1)
        )
        assert data['data']['users'][2] == jsonify_dict(
            user_2.serialize(user_1)
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }


class TestGetUsersPagination(ApiTestCaseMixin):
    @patch('fittrackee.users.users.USERS_PER_PAGE', 2)
    def test_it_gets_first_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 3,
        }

    @patch('fittrackee.users.users.USERS_PER_PAGE', 2)
    def test_it_gets_next_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 3,
        }

    def test_it_gets_empty_next_page_on_users_list(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_user_list_with_2_per_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?per_page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 3,
        }

    def test_it_gets_next_page_on_user_list_with_2_per_page(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?page=2&per_page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'toto' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_username_ascending(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'toto' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_username_descending(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.utcnow() - timedelta(days=1)
        user_3.created_at = datetime.utcnow() - timedelta(hours=1)
        user_1_admin.created_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=created_at',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date_ascending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.utcnow() - timedelta(days=1)
        user_3.created_at = datetime.utcnow() - timedelta(hours=1)
        user_1_admin.created_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=created_at&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_creation_date_descending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        user_2.created_at = datetime.utcnow() - timedelta(days=1)
        user_3.created_at = datetime.utcnow() - timedelta(hours=1)
        user_1_admin.created_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=created_at&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'toto' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_admin_rights(
        self, app: Flask, user_2: User, user_1_admin: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=admin',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_admin_rights_ascending(
        self, app: Flask, user_2: User, user_1_admin: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=admin&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 'sam' in data['data']['users'][1]['username']
        assert 'admin' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_admin_rights_descending(
        self, app: Flask, user_2: User, user_3: User, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=admin&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 'toto' in data['data']['users'][1]['username']
        assert 'sam' in data['data']['users'][2]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=workouts_count',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 0 == data['data']['users'][0]['nb_workouts']
        assert 'sam' in data['data']['users'][1]['username']
        assert 0 == data['data']['users'][1]['nb_workouts']
        assert 'toto' in data['data']['users'][2]['username']
        assert 1 == data['data']['users'][2]['nb_workouts']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=workouts_count&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'admin' in data['data']['users'][0]['username']
        assert 0 == data['data']['users'][0]['nb_workouts']
        assert 'sam' in data['data']['users'][1]['username']
        assert 0 == data['data']['users'][1]['nb_workouts']
        assert 'toto' in data['data']['users'][2]['username']
        assert 1 == data['data']['users'][2]['nb_workouts']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_ordered_by_workouts_count_descending(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=workouts_count&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert 'toto' in data['data']['users'][0]['username']
        assert 1 == data['data']['users'][0]['nb_workouts']
        assert 'admin' in data['data']['users'][1]['username']
        assert 0 == data['data']['users'][1]['nb_workouts']
        assert 'sam' in data['data']['users'][2]['username']
        assert 0 == data['data']['users'][2]['nb_workouts']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    def test_it_gets_users_list_filtering_on_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=toto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert 'toto' in data['data']['users'][0]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 1,
        }

    def test_it_returns_empty_users_list_filtering_on_username(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=not_existing',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 0
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 0,
            'total': 0,
        }

    def test_it_users_list_with_complex_query(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=username&order=desc&page=2&per_page=2',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert 'admin' in data['data']['users'][0]['username']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': True,
            'page': 2,
            'pages': 2,
            'total': 3,
        }


class TestGetRemoteUsers(ApiTestCaseMixin):
    def test_it_returns_error_when_federation_is_disabled(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/users/remote',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert (
            data['message']
            == 'error, federation is disabled for this instance'
        )


class TestGetUserPicture:
    def test_it_return_error_if_user_has_no_picture(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(f'/api/users/{user_1.username}/picture')

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'No picture.' in data['message']

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get('/api/users/not_existing/picture')

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']


class TestUpdateUser(ApiTestCaseMixin):
    def test_it_adds_admin_rights_to_a_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/users/toto',
            content_type='application/json',
            data=json.dumps(dict(admin=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user['email'] == 'toto@toto.com'
        assert user['admin'] is True

    def test_it_removes_admin_rights_to_a_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/users/toto',
            content_type='application/json',
            data=json.dumps(dict(admin=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1

        user = data['data']['users'][0]
        assert user['email'] == 'toto@toto.com'
        assert user['admin'] is False

    def test_it_returns_error_if_payload_for_admin_rights_is_empty(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/users/toto',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 400
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'invalid payload' in data['message']

    def test_it_returns_error_if_payload_for_admin_rights_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/users/toto',
            content_type='application/json',
            data=json.dumps(dict(admin="")),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 500
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'error, please try again or contact the administrator'
            in data['message']
        )

    def test_it_returns_error_if_user_can_not_change_admin_rights(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/users/toto',
            content_type='application/json',
            data=json.dumps(dict(admin=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'you do not have permissions' in data['message']


class TestDeleteUser(ApiTestCaseMixin):
    def test_user_can_delete_its_own_account(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            '/api/users/test',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_user_with_workout_can_delete_its_own_account(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            '/api/workouts',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        response = client.delete(
            '/api/users/test',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_user_with_preferences_can_delete_its_own_account(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            '/api/users/test',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_user_with_picture_can_delete_its_own_account(
        self, app: Flask, user_1: User, sport_1_cycling: Sport, gpx_file: str
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        client.post(
            '/api/auth/picture',
            data=dict(file=(BytesIO(b'avatar'), 'avatar.png')),
            headers=dict(
                content_type='multipart/form-data',
                Authorization=f'Bearer {auth_token}',
            ),
        )

        response = client.delete(
            '/api/users/test',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_user_can_not_delete_another_user_account(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            '/api/users/toto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert 'you do not have permissions' in data['message']

    def test_it_returns_error_when_deleting_non_existing_user(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            '/api/users/not_existing',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert 'not found' in data['status']
        assert 'user does not exist' in data['message']

    def test_admin_can_delete_another_user_account(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.delete(
            '/api/users/toto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_admin_can_delete_its_own_account(
        self, app: Flask, user_1_admin: User, user_2_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.delete(
            '/api/users/admin',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 204

    def test_admin_can_not_delete_its_own_account_if_no_other_admin(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.delete(
            '/api/users/admin',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert 'error' in data['status']
        assert (
            'you can not delete your account, no other user has admin rights'
            in data['message']
        )

    def test_it_enables_registration_on_user_delete(
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_3_users_max, user_1_admin.email
        )
        client.delete(
            '/api/users/toto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username='justatest',
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )
        assert response.status_code == 201

    def test_it_does_not_enable_registration_on_user_delete(
        self,
        app_with_3_users_max: Flask,
        user_1_admin: User,
        user_2: User,
        user_3: User,
        user_1_paris: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_3_users_max, user_1_admin.email
        )

        client.delete(
            '/api/users/toto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )
        response = client.post(
            '/api/auth/register',
            data=json.dumps(
                dict(
                    username='justatest',
                    email='test@test.com',
                    password='12345678',
                    password_conf='12345678',
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 403
        data = json.loads(response.data.decode())
        assert data['status'] == 'error'
        assert data['message'] == 'error, registration is disabled'

    def test_it_deletes_actor_when_deleting_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        actor_id = user_2.actor_id
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        client.delete(
            f'/api/users/{user_2.username}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert Actor.query.filter_by(id=actor_id).first() is None

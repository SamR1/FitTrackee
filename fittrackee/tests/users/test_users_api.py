import json
from datetime import datetime, timedelta
from io import BytesIO
from unittest.mock import MagicMock, patch

from flask import Flask

from fittrackee.users.models import User, UserSportPreference
from fittrackee.utils import get_readable_duration
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestGetUser(ApiTestCaseMixin):
    def test_it_returns_error_if_user_has_no_admin_rights(
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

        self.assert_403(response)

    def test_user_can_access_his_profile(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/users/{user_1.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user['username'] == user_1.username

    def test_it_gets_inactive_user(
        self, app: Flask, user_1_admin: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/users/{inactive_user.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user == jsonify_dict(inactive_user.serialize(user_1_admin))

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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user == jsonify_dict(user_2.serialize(user_1_admin))

    def test_it_gets_single_user_with_workouts(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.get(
            f'/api/users/{user_1.username}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert data['status'] == 'success'
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user == jsonify_dict(user_1.serialize(user_2_admin))

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users/not_existing',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404_with_entity(response, 'user')


class TestGetUsers(ApiTestCaseMixin):
    def test_it_returns_error_if_user_has_no_admin_rights(
        self, app: Flask, user_1: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/users',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_get_users_list_regardless_their_account_status(
        self, app: Flask, user_1_admin: User, inactive_user: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['users']) == 3
        assert data['data']['users'][0] == jsonify_dict(
            user_1_admin.serialize(user_1_admin)
        )
        assert data['data']['users'][1] == jsonify_dict(
            inactive_user.serialize(user_1_admin)
        )
        assert data['data']['users'][2] == jsonify_dict(
            user_3.serialize(user_1_admin)
        )
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 3,
        }

    @patch('fittrackee.users.users.USER_PER_PAGE', 2)
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['pagination'] == {
            'has_next': True,
            'has_prev': False,
            'page': 1,
            'pages': 2,
            'total': 3,
        }

    @patch('fittrackee.users.users.USER_PER_PAGE', 2)
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

    def test_it_gets_users_list_ordered_by_account_status(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=is_active',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['data']['users'][0]['username'] == inactive_user.username
        assert not data['data']['users'][0]['is_active']
        assert data['data']['users'][1]['username'] == user_1_admin.username
        assert data['data']['users'][1]['is_active']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    def test_it_gets_users_list_ordered_by_account_status_ascending(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=is_active&order=asc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['data']['users'][0]['username'] == inactive_user.username
        assert not data['data']['users'][0]['is_active']
        assert data['data']['users'][1]['username'] == user_1_admin.username
        assert data['data']['users'][1]['is_active']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
        }

    def test_it_gets_users_list_ordered_by_account_status_descending(
        self,
        app: Flask,
        user_1_admin: User,
        inactive_user: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?order_by=is_active&order=desc',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['users']) == 2
        assert data['data']['users'][0]['username'] == user_1_admin.username
        assert data['data']['users'][0]['is_active']
        assert data['data']['users'][1]['username'] == inactive_user.username
        assert not data['data']['users'][1]['is_active']
        assert data['pagination'] == {
            'has_next': False,
            'has_prev': False,
            'page': 1,
            'pages': 1,
            'total': 2,
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

    def test_it_returns_username_matching_query(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=oto',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        assert 'toto' in data['data']['users'][0]['username']

    def test_it_filtering_on_username_is_case_insensitive(
        self, app: Flask, user_1_admin: User, user_2: User, user_3: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/users?q=TOTO',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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

        data = json.loads(response.data.decode())
        assert response.status_code == 200
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


class TestGetUserPicture(ApiTestCaseMixin):
    def test_it_return_error_if_user_has_no_picture(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get(f'/api/users/{user_1.username}/picture')

        self.assert_404_with_message(response, 'No picture.')

    def test_it_returns_error_if_user_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client = app.test_client()

        response = client.get('/api/users/not_existing/picture')

        self.assert_404_with_entity(response, 'user')


class TestUpdateUser(ApiTestCaseMixin):
    def test_it_returns_error_if_payload_is_empty(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_payload_for_admin_rights_is_invalid(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
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
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(admin=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_adds_admin_rights_to_a_user(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
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
            f'/api/users/{user_2.username}',
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

    def test_it_does_not_send_email_when_only_admin_rights_update(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_password_change_email_mock: MagicMock,
        user_reset_password_email: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(admin=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        user_password_change_email_mock.send.assert_not_called()
        user_reset_password_email.send.assert_not_called()

    def test_it_resets_user_password(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        user_2_password = user_2.password

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(reset_password=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert user_2.password != user_2_password

    def test_it_calls_password_change_email_when_password_reset_is_successful(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_password_change_email_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(reset_password=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        user_password_change_email_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_2.email,
            },
            {
                'username': user_2.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
            },
        )

    def test_it_calls_reset_password_email_when_password_reset_is_successful(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_reset_password_email: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        with patch(
            'fittrackee.users.users.User.encode_password_reset_token',
            return_value='xxx',
        ):
            response = client.patch(
                f'/api/users/{user_2.username}',
                content_type='application/json',
                data=json.dumps(dict(reset_password=True)),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        user_reset_password_email.send.assert_called_once_with(
            {
                'language': 'en',
                'email': user_2.email,
            },
            {
                'expiration_delay': get_readable_duration(
                    app.config['PASSWORD_TOKEN_EXPIRATION_SECONDS'],
                    'en',
                ),
                'username': user_2.username,
                'password_reset_url': (
                    'http://0.0.0.0:5000/password-reset?token=xxx'
                ),
                'fittrackee_url': 'http://0.0.0.0:5000',
            },
        )

    def test_it_returns_error_when_updating_email_with_invalid_address(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(new_email=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response, 'valid email must be provided')

    def test_it_returns_error_when_new_email_is_same_as_current_email(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(new_email=user_2.email)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(
            response, 'new email must be different than curent email'
        )

    def test_it_does_not_send_email_when_error_on_updating_email(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_email_updated_to_new_address_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(new_email=self.random_string())),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        user_email_updated_to_new_address_mock.send.assert_not_called()

    def test_it_updates_user_email(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        user_2_email = user_2.email
        user_2_confirmation_token = user_2.confirmation_token

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(new_email='new.' + user_2.email)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        assert user_2.email == user_2_email
        assert user_2.email_to_confirm == 'new.' + user_2.email
        assert user_2.confirmation_token != user_2_confirmation_token

    def test_it_calls_email_updated_to_new_address_when_password_reset_is_successful(  # noqa
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        user_email_updated_to_new_address_mock: MagicMock,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )
        new_email = 'new.' + user_2.email
        expected_token = self.random_string()

        with patch('secrets.token_urlsafe', return_value=expected_token):
            response = client.patch(
                f'/api/users/{user_2.username}',
                content_type='application/json',
                data=json.dumps(dict(new_email=new_email)),
                headers=dict(Authorization=f'Bearer {auth_token}'),
            )

        assert response.status_code == 200
        user_email_updated_to_new_address_mock.send.assert_called_once_with(
            {
                'language': 'en',
                'email': new_email,
            },
            {
                'username': user_2.username,
                'fittrackee_url': 'http://0.0.0.0:5000',
                'email_confirmation_url': (
                    f'http://0.0.0.0:5000/email-update?token={expected_token}'
                ),
            },
        )

    def test_it_activates_user_account(
        self, app: Flask, user_1_admin: User, inactive_user: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{inactive_user.username}',
            content_type='application/json',
            data=json.dumps(dict(activate=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user['email'] == inactive_user.email
        assert user['is_active'] is True
        assert inactive_user.confirmation_token is None

    def test_it_can_only_activate_user_account(
        self, app: Flask, user_1_admin: User, user_2: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/users/{user_2.username}',
            content_type='application/json',
            data=json.dumps(dict(activate=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['users']) == 1
        user = data['data']['users'][0]
        assert user['email'] == user_2.email
        assert user['is_active'] is True
        assert user_2.confirmation_token is None


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

        self.assert_403(response)

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

        self.assert_404_with_entity(response, 'user')

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

        self.assert_403(
            response,
            'you can not delete your account, no other user has admin rights',
        )

    def test_it_enables_registration_after_user_delete(
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
                    username=self.random_string(),
                    email=self.random_email(),
                    password=self.random_string(),
                )
            ),
            content_type='application/json',
        )

        assert response.status_code == 200

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

        self.assert_403(response, 'error, registration is disabled')

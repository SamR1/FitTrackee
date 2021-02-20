import json

from flask import Flask

from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout

from ..api_test_case import ApiTestCaseMixin

expected_sport_1_cycling_result = {
    'id': 1,
    'label': 'Cycling',
    'img': None,
    'is_active': True,
}
expected_sport_1_cycling_admin_result = expected_sport_1_cycling_result.copy()
expected_sport_1_cycling_admin_result['has_workouts'] = False

expected_sport_2_running_result = {
    'id': 2,
    'label': 'Running',
    'img': None,
    'is_active': True,
}
expected_sport_2_running_admin_result = expected_sport_2_running_result.copy()
expected_sport_2_running_admin_result['has_workouts'] = False

expected_sport_1_cycling_inactive_result = {
    'id': 1,
    'label': 'Cycling',
    'img': None,
    'is_active': False,
}
expected_sport_1_cycling_inactive_admin_result = (
    expected_sport_1_cycling_inactive_result.copy()
)
expected_sport_1_cycling_inactive_admin_result['has_workouts'] = False


class TestGetSports(ApiTestCaseMixin):
    def test_it_gets_all_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/sports',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert data['data']['sports'][0] == expected_sport_1_cycling_result
        assert data['data']['sports'][1] == expected_sport_2_running_result

    def test_it_gets_all_sports_with_inactive_one(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling_inactive: Sport,
        sport_2_running: Sport,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/sports',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_result
        )
        assert data['data']['sports'][1] == expected_sport_2_running_result

    def test_it_gets_all_sports_with_admin_rights(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling_inactive: Sport,
        sport_2_running: Sport,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.get(
            '/api/sports',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_admin_result
        )
        assert (
            data['data']['sports'][1] == expected_sport_2_running_admin_result
        )


class TestGetSport(ApiTestCaseMixin):
    def test_it_gets_a_sport(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0] == expected_sport_1_cycling_result

    def test_it_returns_404_if_sport_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['sports']) == 0

    def test_it_gets_a_inactive_sport(
        self, app: Flask, user_1: User, sport_1_cycling_inactive: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.get(
            '/api/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_result
        )

    def test_it_get_an_inactive_sport_with_admin_rights(
        self, app: Flask, user_1_admin: User, sport_1_cycling_inactive: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.get(
            '/api/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert (
            data['data']['sports'][0]
            == expected_sport_1_cycling_inactive_admin_result
        )


class TestUpdateSport(ApiTestCaseMixin):
    def test_it_disables_a_sport(
        self, app: Flask, user_1_admin: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is False
        assert data['data']['sports'][0]['has_workouts'] is False

    def test_it_enables_a_sport(
        self, app: Flask, user_1_admin: User, sport_1_cycling: Sport
    ) -> None:
        sport_1_cycling.is_active = False
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is True
        assert data['data']['sports'][0]['has_workouts'] is False

    def test_it_disables_a_sport_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is False
        assert data['data']['sports'][0]['has_workouts'] is True

    def test_it_enables_a_sport_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        sport_1_cycling.is_active = False
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=True)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0]['is_active'] is True
        assert data['data']['sports'][0]['has_workouts'] is True

    def test_returns_error_if_user_has_no_admin_rights(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(app)

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'success' not in data['status']
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_returns_error_if_payload_is_invalid(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'Invalid payload.' in data['message']

    def test_it_returns_error_if_sport_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, as_admin=True
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['sports']) == 0

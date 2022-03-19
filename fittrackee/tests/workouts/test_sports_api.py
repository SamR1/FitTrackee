import json

from flask import Flask

from fittrackee import db
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin

expected_sport_1_cycling_result = {
    'id': 1,
    'label': 'Cycling',
    'is_active': True,
    'is_active_for_user': True,
    'color': None,
    'stopped_speed_threshold': 1,
}
expected_sport_1_cycling_admin_result = expected_sport_1_cycling_result.copy()
expected_sport_1_cycling_admin_result['has_workouts'] = False

expected_sport_2_running_result = {
    'id': 2,
    'label': 'Running',
    'is_active': True,
    'is_active_for_user': True,
    'color': None,
    'stopped_speed_threshold': 0.1,
}
expected_sport_2_running_admin_result = expected_sport_2_running_result.copy()
expected_sport_2_running_admin_result['has_workouts'] = False

expected_sport_1_cycling_inactive_result = {
    'id': 1,
    'label': 'Cycling',
    'is_active': False,
    'is_active_for_user': False,
    'color': None,
    'stopped_speed_threshold': 1,
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
            app, user_1_admin.email
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

    def test_it_gets_sports_with_auth_user_preferences(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_admin_sport_1_preference: UserSportPreference,
    ) -> None:
        user_admin_sport_1_preference.color = '#000000'
        user_admin_sport_1_preference.stopped_speed_threshold = 0.5
        user_admin_sport_1_preference.is_active = False
        db.session.commit()

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/sports',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert data['data']['sports'][0]['color'] == '#000000'
        assert data['data']['sports'][0]['stopped_speed_threshold'] == 0.5
        assert data['data']['sports'][0]['is_active_for_user'] is False
        assert (
            data['data']['sports'][1] == expected_sport_2_running_admin_result
        )


class TestGetSport(ApiTestCaseMixin):
    def test_it_gets_a_sport(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0] == expected_sport_1_cycling_result

    def test_it_gets_a_sport_with_preferences(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/sports/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['sports']) == 0

    def test_it_gets_a_inactive_sport(
        self, app: Flask, user_1: User, sport_1_cycling_inactive: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
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
            == expected_sport_1_cycling_inactive_result
        )

    def test_it_get_an_inactive_sport_with_admin_rights(
        self, app: Flask, user_1_admin: User, sport_1_cycling_inactive: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
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
            app, user_1_admin.email
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
        assert data['data']['sports'][0]['is_active_for_user'] is False
        assert data['data']['sports'][0]['has_workouts'] is False

    def test_it_enables_a_sport(
        self, app: Flask, user_1_admin: User, sport_1_cycling: Sport
    ) -> None:
        sport_1_cycling.is_active = False
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
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
        assert data['data']['sports'][0]['is_active_for_user'] is True
        assert data['data']['sports'][0]['has_workouts'] is False

    def test_it_disables_a_sport_with_workouts(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
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
        assert data['data']['sports'][0]['is_active_for_user'] is False
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
            app, user_1_admin.email
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
        assert data['data']['sports'][0]['is_active_for_user'] is True
        assert data['data']['sports'][0]['has_workouts'] is True

    def test_it_disables_a_sport_with_preferences(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        user_admin_sport_1_preference: UserSportPreference,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
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
        assert data['data']['sports'][0]['is_active_for_user'] is False
        assert data['data']['sports'][0]['is_active_for_user'] is False
        assert data['data']['sports'][0]['has_workouts'] is False

    def test_it_enables_a_sport_with_preferences(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling: Sport,
        user_admin_sport_1_preference: UserSportPreference,
    ) -> None:
        sport_1_cycling.is_active = False
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
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
        assert data['data']['sports'][0]['is_active_for_user'] is True
        assert data['data']['sports'][0]['has_workouts'] is False

    def test_returns_error_if_user_has_no_admin_rights(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_returns_error_if_payload_is_invalid(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_error_if_sport_does_not_exist(
        self, app: Flask, user_1_admin: User
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            '/api/sports/1',
            content_type='application/json',
            data=json.dumps(dict(is_active=False)),
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['sports']) == 0

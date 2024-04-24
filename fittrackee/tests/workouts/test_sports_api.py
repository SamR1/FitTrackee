import json

import pytest
from flask import Flask
from sqlalchemy.dialects.postgresql import insert

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestGetSports(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
    ) -> None:
        client = app.test_client()

        response = client.get('/api/sports')

        self.assert_401(response)

    @pytest.mark.parametrize(
        'input_check_workouts',
        ["", "?check_workouts=false", "?check_workouts=true"],
    )
    def test_it_gets_all_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        input_check_workouts: bool,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/sports{input_check_workouts}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling.serialize()
        )
        assert data['data']['sports'][1] == jsonify_dict(
            sport_2_running.serialize()
        )

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
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling_inactive.serialize()
        )
        assert data['data']['sports'][1] == jsonify_dict(
            sport_2_running.serialize()
        )

    @pytest.mark.parametrize(
        'input_check_workouts',
        ["", "?check_workouts=false", "?check_workouts=true"],
    )
    def test_it_gets_all_sports_with_admin_rights(
        self,
        app: Flask,
        user_1_admin: User,
        sport_1_cycling_inactive: Sport,
        sport_2_running: Sport,
        input_check_workouts: bool,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/sports{input_check_workouts}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        assert response.status_code == 200
        check_workouts = input_check_workouts == "?check_workouts=true"
        data = json.loads(response.data.decode())
        assert 'success' in data['status']
        assert len(data['data']['sports']) == 2
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling_inactive.serialize(check_workouts=check_workouts)
        )
        assert data['data']['sports'][1] == jsonify_dict(
            sport_2_running.serialize(check_workouts=check_workouts)
        )

    def test_it_gets_sports_with_auth_user_preferences_and_default_equipment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()

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
        assert len(data['data']['sports']) == 1
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling.serialize(
                sport_preferences=user_1_sport_1_preference.serialize(),
            )
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
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling.serialize(
                sport_preferences=user_admin_sport_1_preference.serialize(),
            )
        )
        assert data['data']['sports'][1] == jsonify_dict(
            sport_2_running.serialize()
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
            '/api/sports',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling.serialize()
        )

    def test_it_gets_a_sport_with_preferences(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
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
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling.serialize(
                sport_preferences=user_1_sport_1_preference.serialize()
            )
        )

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
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling_inactive.serialize()
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
        assert data['data']['sports'][0] == jsonify_dict(
            sport_1_cycling_inactive.serialize()
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
            f'/api/sports/{sport_1_cycling.id}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


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

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'workouts:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        user_2: User,
        sport_1_cycling: Sport,
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1_admin, scope=client_scope
        )

        response = client.patch(
            f'/api/sports/{sport_1_cycling.id}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

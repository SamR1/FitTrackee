import json
from datetime import datetime

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import EquipmentType
from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import OAUTH_SCOPES, jsonify_dict


class TestGetEquipmentTypes(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client = app.test_client()

        response = client.get('/api/equipment-types')

        self.assert_401(response)

    def test_it_gets_all_equipment_types_normal_user(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_1_shoe_inactive: EquipmentType,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/equipment-types',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 2
        assert data['data']['equipment_types'][0] == jsonify_dict(
            equipment_type_1_shoe.serialize(is_admin=False)
        )
        assert data['data']['equipment_types'][1] == jsonify_dict(
            equipment_type_2_bike.serialize(is_admin=False)
        )

    def test_it_gets_all_equipment_types_admin_user(
        self,
        app: Flask,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_1_shoe_inactive: EquipmentType,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/equipment-types',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 3
        assert data['data']['equipment_types'][0] == jsonify_dict(
            equipment_type_1_shoe.serialize(is_admin=True)
        )
        assert data['data']['equipment_types'][1] == jsonify_dict(
            equipment_type_1_shoe_inactive.serialize(is_admin=True)
        )
        assert data['data']['equipment_types'][2] == jsonify_dict(
            equipment_type_2_bike.serialize(is_admin=True)
        )

    def test_suspended_ser_can_get_all_equipment_types(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_1_shoe_inactive: EquipmentType,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        user_1.suspended_at = datetime.utcnow()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/equipment-types',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 2
        assert data['data']['equipment_types'][0] == jsonify_dict(
            equipment_type_1_shoe.serialize(is_admin=False)
        )
        assert data['data']['equipment_types'][1] == jsonify_dict(
            equipment_type_2_bike.serialize(is_admin=False)
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'equipments:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
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
            '/api/equipment-types',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetEquipmentType(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client = app.test_client()

        response = client.get(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
        )

        self.assert_401(response)

    def test_it_gets_single_equipment_type(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 1
        assert data['data']['equipment_types'][0] == jsonify_dict(
            equipment_type_1_shoe.serialize(is_admin=False)
        )

    def test_it_returns_404_if_equipment_type_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/equipment-types/{self.random_int()}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['equipment_types']) == 0

    def test_it_returns_404_if_equipment_type_is_inactive(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe_inactive: EquipmentType,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f'/api/equipment-types/{equipment_type_1_shoe_inactive.id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['equipment_types']) == 0

    def test_it_returns_inactive_equipment_type_when_user_is_admin(
        self,
        app: Flask,
        user_1_admin: User,
        equipment_type_1_shoe_inactive: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f'/api/equipment-types/{equipment_type_1_shoe_inactive.id}',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 1
        assert data['data']['equipment_types'][0] == jsonify_dict(
            equipment_type_1_shoe_inactive.serialize(is_admin=True)
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'equipments:read': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
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
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestUpdateEquipmentTypes(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client = app.test_client()

        response = client.patch(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            json={"is_active": False},
        )

        self.assert_401(response)

    def test_it_returns_403_if_user_has_not_admin_rights(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            json={"is_active": False},
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_403(response)

    def test_it_returns_400_if_is_active_is_missing(
        self,
        app: Flask,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            json={},
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_400(response)

    def test_it_returns_404_if_equipment_does_not_exist(
        self,
        app: Flask,
        user_1_admin: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/equipment-types/{self.random_int()}',
            content_type='application/json',
            json={"is_active": False},
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        self.assert_404(response)

    @pytest.mark.parametrize('expected_active_status', [True, False])
    def test_it_updates_an_equipment_type(
        self,
        app: Flask,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
        expected_active_status: bool,
    ) -> None:
        equipment_type_1_shoe.is_active = not expected_active_status
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            json={"is_active": expected_active_status},
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 1
        assert (
            data['data']['equipment_types'][0]['is_active']
            is expected_active_status
        )

    @pytest.mark.parametrize('expected_active_status', [True, False])
    def test_it_does_not_raise_error_if_equipment_status_is_the_same(
        self,
        app: Flask,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
        expected_active_status: bool,
    ) -> None:
        equipment_type_1_shoe.is_active = expected_active_status
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.patch(
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            json={"is_active": expected_active_status},
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 1
        assert (
            data['data']['equipment_types'][0]['is_active']
            is expected_active_status
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        {**OAUTH_SCOPES, 'equipments:write': True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: Flask,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
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
            f'/api/equipment-types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            json={"is_active": False},
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

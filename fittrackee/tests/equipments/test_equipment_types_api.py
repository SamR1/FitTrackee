import json

import pytest
from flask import Flask

from fittrackee.equipments.models import EquipmentType
from fittrackee.users.models import User

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestGetEquipmentTypes(ApiTestCaseMixin):
    def test_it_gets_all_equipment_types_normal_user(
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
            '/api/equipment_types',
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
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/equipment_types',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment_types']) == 2
        assert data['data']['equipment_types'][0] == jsonify_dict(
            equipment_type_1_shoe.serialize(is_admin=True)
        )
        assert data['data']['equipment_types'][1] == jsonify_dict(
            equipment_type_2_bike.serialize(is_admin=True)
        )

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('profile:read', True),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', False),
        ],
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
            '/api/equipment_types',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetEquipmentType(ApiTestCaseMixin):
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
            '/api/equipment_types/1',
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
            '/api/equipment_types/3',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = self.assert_404(response)
        assert len(data['data']['equipment_types']) == 0

    @pytest.mark.parametrize(
        'client_scope, can_access',
        [
            ('application:write', False),
            ('profile:read', True),
            ('profile:write', False),
            ('users:read', False),
            ('users:write', False),
            ('workouts:read', False),
            ('workouts:write', False),
        ],
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
            f'/api/equipment_types/{equipment_type_1_shoe.id}',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)

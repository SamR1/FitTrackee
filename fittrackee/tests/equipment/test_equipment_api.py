import json

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipment.models import Equipment, EquipmentType
from fittrackee.users.models import User, UserSportPreference
from fittrackee.workouts.models import Workout, Sport

from ..mixins import ApiTestCaseMixin
from ..utils import jsonify_dict


class TestGetEquipment(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
    ) -> None:
        client = app.test_client()

        response = client.get('/api/equipment')

        self.assert_401(response)

    def test_it_gets_all_equipment(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/equipment',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 2
        assert data['data']['equipment'][0] == jsonify_dict(
            equipment_1_bike.serialize()
        )
        assert data['data']['equipment'][1] == jsonify_dict(
            equipment_2_shoes.serialize()
        )

    def test_it_gets_all_equipment_with_inactive_one(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
        equipment_1_bike_inactive: Equipment
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/equipment',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 3
        assert data['data']['equipment'][0] == jsonify_dict(
            equipment_1_bike.serialize()
        )
        assert data['data']['equipment'][1] == jsonify_dict(
            equipment_2_shoes.serialize()
        )
        assert data['data']['equipment'][2] == jsonify_dict(
            equipment_1_bike_inactive.serialize()
        )

    def test_it_doesnt_gets_other_user_equipment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            '/api/equipment',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 0

    def test_it_gets_all_equipment_with_admin_rights(
        self,
        app: Flask,
        user_1: User,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/equipment',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 2
        assert data['data']['equipment'][0] == jsonify_dict(
            equipment_1_bike.serialize()
        )
        assert data['data']['equipment'][1] == jsonify_dict(
            equipment_2_shoes.serialize()
        )

    def test_it_gets_all_equipment_with_admin_rights_only_user(
        self,
        app: Flask,
        user_1: User,
        user_1_admin: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            '/api/equipment',
            query_string='only_user',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 0


    def test_it_gets_equipment_by_id(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/equipment/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 1
        assert data['data']['equipment'][0] == jsonify_dict(
            equipment_1_bike.serialize()
        )

    def test_it_gets_equipment_by_id_non_existent_id(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            '/api/equipment/3',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['equipment']) == 0

    def test_it_gets_other_user_equipment_by_id(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            '/api/equipment/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['equipment']) == 0

    def test_it_gets_other_user_equipment_by_id_as_admin(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment,
        equipment_2_shoes: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.get(
            '/api/equipment/1',
            headers=dict(Authorization=f'Bearer {auth_token}'),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['equipment']) == 1
        assert data['data']['equipment'][0] == jsonify_dict(
            equipment_1_bike.serialize()
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
        equipment_1_bike: Equipment,
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
            '/api/equipment',
            content_type='application/json',
            headers=dict(Authorization=f'Bearer {access_token}'),
        )

        self.assert_response_scope(response, can_access)


class TestGetEquipmentType(ApiTestCaseMixin):
    def test_it_gets_all_equipment_types_normal_user(
        self, 
        app: Flask, 
        user_1: User, 
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType
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
        equipment_type_2_bike: EquipmentType
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

    def test_it_gets_single_equipment_type(
        self, 
        app: Flask, 
        user_1: User, 
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType
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
        equipment_type_2_bike: EquipmentType
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


class TestPostEquipment(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_1_bike: Equipment
    ) -> None:
        client = app.test_client()

        response = client.post(
            '/api/equipment',
            data={
                "equipment_type_id": 1,
                "label": "test",
                "description": "test"
            }
        )
        self.assert_401(response)

    def test_it_adds_an_equipment(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_2_shoes: Equipment
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/equipment',
            json = {
                "label": "Test shoes",
                "description": "A piece of equipment for testing",
                "equipment_type": 1
            },
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert 'created' in data['status']
        assert len(data['data']['equipment']) == 1
        assert 'Test shoes' == data['data']['equipment'][0]['label']
        assert (
            'A piece of equipment for testing' 
            == data['data']['equipment'][0]['description']
        )
        assert 1 == data['data']['equipment'][0]['equipment_type']
        assert 2 == data['data']['equipment'][0]['id']

    def test_invalid_payload_response(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            '/api/equipment',
            json = {
                "description": "A piece of equipment with missing label",
                "equipment_type": 1
            },
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert (
            'The "label" and "equipment_type" parameters must be '
            'provided in the body of the request'
        ) in data['message']


    def test_integrity_error_response(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # send the same request twice to violate unique constraint
        for i in range(2):
            response = client.post(
                '/api/equipment',
                json = {
                    "label": "Test label",
                    "description": "A piece of equipment with missing label",
                    "equipment_type": 1
                },
                headers = {
                    "Authorization": f'Bearer {auth_token}'
                }
            )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'fail' in data['status']
        assert 'Error during equipment save' in data['message']


class TestPatchEquipment(ApiTestCaseMixin):
    def test_it_updates_equipment(
            self,
            app: Flask,
            user_1: User,
            equipment_type_1_shoe: EquipmentType,
            equipment_type_2_bike: EquipmentType,
            equipment_1_bike: Equipment,
        ) -> None:
            client, auth_token = self.get_test_client_and_auth_token(
                app, user_1.email
            )

            # test original info
            response = client.get(
                '/api/equipment/1',
                headers = {"Authorization": f'Bearer {auth_token}'}
            )
            e = response.json['data']['equipment'][0]
            assert e['label'] == 'Test bike equipment'
            assert e['description'] == 'A bike for testing purposes'
            assert e['equipment_type'] == 2
            assert e['is_active'] == True
            
            new_label = "Updated equipment 1 label"
            new_description = "Updated equipment 1 description"
            new_type = 1
            new_active = False

            response = client.patch(
                f'/api/equipment/1',
                json={
                    'label': new_label,
                    'description': new_description,
                    'is_active': new_active,
                    'equipment_type': new_type
                },
                headers = {"Authorization": f'Bearer {auth_token}'}
            )
            
            e = response.json['data']['equipment'][0]
            assert e['label'] == new_label
            assert e['description'] == new_description
            assert e['equipment_type'] == new_type
            assert e['is_active'] == new_active

            response = client.get(
                '/api/equipment/1',
                headers = {"Authorization": f'Bearer {auth_token}'}
            )
            
            e = response.json['data']['equipment'][0]
            assert e['label'] == new_label
            assert e['description'] == new_description
            assert e['equipment_type'] == new_type
            assert e['is_active'] == new_active


    def test_invalid_payload_response_no_payload(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/equipment/1',
            json = {},
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'No request data was supplied' in data['message']

    def test_invalid_payload_response_bad_payload(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/equipment/1',
            json = {'bogus_param': 1},
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'No valid parameters supplied' in data['message']

    def test_invalid_equipment_id(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            '/api/equipment/1',
            json = {'is_active': False},
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['equipment']) == 0

    def test_integrity_error_response(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_2_shoes: Equipment
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # Try to change equipment type to one that does not exist in DB
        response = client.patch(
            '/api/equipment/1',
            json = {
                "equipment_type": 2
            },
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 500
        assert 'fail' in data['status']
        assert 'Error during equipment update' in data['message']

class TestDeleteEquipment(ApiTestCaseMixin):
    def test_simple_delete_one_equipment(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_2_shoes: Equipment
    ):
        """Tests deleting a piece of equipment with no workouts."""
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        
        response = client.delete(
            '/api/equipment/1',
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        assert response.status_code == 204
        assert len(db.session.query(Equipment).all()) == 0

    def test_delete_error_equipment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ):
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        
        response = client.delete(
            '/api/equipment/1',
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['equipment']) == 0
        assert len(db.session.query(Equipment).all()) == 0

    def test_cannot_delete_equipment_for_other_user(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_2_shoes: Equipment,
        user_2: User
    ):
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )
        # equipment_2_shoes is owned by user_1

        response = client.delete(
            '/api/equipment/1',
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 403
        assert 'error' in data['status']
        assert (
            "Cannot delete another user's equipment "
            "without admin rights" in data['message']
        )
        assert len(db.session.query(Equipment).all()) == 1

    def test_admin_can_delete_other_user_equipment(
        self,
        app: Flask,
        user_1: User,
        user_2_admin: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_2_shoes: Equipment
    ):
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )
        
        response = client.delete(
            '/api/equipment/1',
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        assert response.status_code == 204
        assert len(db.session.query(Equipment).all()) == 0


    def test_cannot_delete_equipment_with_workout(
        self,
        app: Flask,
        user_1: User,
        workout_w_equipment: Workout,
    ):
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # workout_w_equipment has one equipment

        response = client.delete(
            '/api/equipment/1',
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        data = response.json
        assert response.status_code == 403
        assert 'error' in data['status']
        assert (
            "Cannot delete equipment that has associated workouts. "
            "Equipment id 1 has 1 associated workout. (Provide "
            "argument 'force' as a query parameter to override "
            "this check)" in data['message']
        )
        assert len(db.session.query(Equipment).all()) == 1

    def test_can_force_delete_equipment_with_workout(
        self,
        app: Flask,
        user_1: User,
        workout_w_equipment: Workout,
    ):
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # workout_w_equipment has one equipment; after delete
        # the workout should have no equipment

        response = client.delete(
            '/api/equipment/1',
            query_string='force', 
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        assert response.status_code == 204

        # check workout has no equipment
        w = db.session.query(Workout).filter(
            Workout.id == workout_w_equipment.id
        ).first()
        assert w.equipment == []

        # check equipment_workout table is empty
        assert len(
            db.session.execute("SELECT * from equipment_workout").all()
        ) == 0
        assert len(db.session.query(Equipment).all()) == 0
        
    def test_deleting_equipment_sets_user_sport_default_to_null(
        self,
        app: Flask,
        user_1: User,
        user_sport_1_preference: UserSportPreference,
    ):
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # workout_w_equipment has one equipment; after delete
        # the workout should have no equipment

        response = client.delete(
            '/api/equipment/1',
            query_string='force', 
            headers = {
                "Authorization": f'Bearer {auth_token}'
            }
        )

        assert response.status_code == 204

        # check user sport preference has null equipment
        up = db.session.query(UserSportPreference).filter(
            UserSportPreference.user_id == user_sport_1_preference.user_id,
            UserSportPreference.sport_id == 1
        ).first()
        assert up.default_equipment_id is None

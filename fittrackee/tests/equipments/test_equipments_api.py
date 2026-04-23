import json
from datetime import datetime, timedelta, timezone
from typing import Tuple
from unittest.mock import patch

import pytest
from flask import Flask

from fittrackee import db
from fittrackee.equipments.models import Equipment, EquipmentType
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.users.roles import UserRole
from fittrackee.utils import decode_short_id
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.models import Sport, Workout

from ..mixins import ApiTestCaseMixin, EquipmentMixin
from ..utils import jsonify_dict


class TestGetEquipments(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: Flask,
    ) -> None:
        client = app.test_client()

        response = client.get("/api/equipments")

        self.assert_401(response)

    def test_it_does_not_return_error_if_user_suspended(
        self, app: Flask, user_1: User
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/equipments",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert data["data"]["equipments"] == []

    def test_it_gets_all_user_equipments(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/equipments",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 2
        assert data["data"]["equipments"][0] == jsonify_dict(
            equipment_bike_user_1.serialize(current_user=user_1)
        )
        assert data["data"]["equipments"][1] == jsonify_dict(
            equipment_shoes_user_1.serialize(current_user=user_1)
        )

    def test_it_gets_all_equipments_with_inactive_one(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        equipment_bike_user_1_inactive: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            "/api/equipments",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 3
        assert data["data"]["equipments"][0] == jsonify_dict(
            equipment_bike_user_1.serialize(current_user=user_1)
        )
        assert data["data"]["equipments"][1] == jsonify_dict(
            equipment_shoes_user_1.serialize(current_user=user_1)
        )
        assert data["data"]["equipments"][2] == jsonify_dict(
            equipment_bike_user_1_inactive.serialize(current_user=user_1)
        )

    def test_it_doesnt_get_other_user_equipments(
        self,
        app: Flask,
        user_2: User,
        equipment_shoes_user_1: Equipment,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            "/api/equipments",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["equipments"] == [
            jsonify_dict(equipment_shoes_user_2.serialize(current_user=user_2))
        ]

    def test_it_gets_only_user_equipments_when_user_is_admin(
        self,
        app: Flask,
        user_2_admin: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.get(
            "/api/equipments",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["equipments"] == []

    def test_it_does_not_get_equipment_even_when_visibility_is_public(
        self,
        app: Flask,
        user_2_admin: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        equipment_shoes_user_1.visibility = VisibilityLevel.PUBLIC
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.get(
            "/api/equipments",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["equipments"] == []

    def test_expected_scope_is_equipments_read(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint="/api/equipments",
            invalid_scope="workouts:read",
            expected_endpoint_scope="equipments:read",
        )


class TestGetEquipment(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, equipment_shoes_user_1: Equipment
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/equipments/{equipment_shoes_user_1.short_id}"
        )

        self.assert_401(response)

    def test_it_gets_equipment_by_id(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]

    def test_suspended_user_can_get_equipment(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        user_1.suspended_at = datetime.now(timezone.utc)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert data["data"]["equipments"] == [
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        ]

    def test_it_returns_error_when_equipment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"/api/equipments/{self.random_short_id()}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    def test_it_does_not_return_other_user_equipment(
        self,
        app: Flask,
        user_2: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        equipment_shoes_user_1.visibility = VisibilityLevel.PUBLIC
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.get(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    def test_it_does_not_get_other_user_equipment_as_admin(
        self,
        app: Flask,
        user_2_admin: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2_admin.email
        )

        response = client.get(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404(response)

    def test_expected_scope_is_equipments_read(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="get",
            endpoint=f"/api/equipments/{self.random_short_id()}",
            invalid_scope="workouts:read",
            expected_endpoint_scope="equipments:read",
        )


class TestPostEquipment(ApiTestCaseMixin, EquipmentMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, equipment_bike_user_1: Equipment
    ) -> None:
        client = app.test_client()

        response = client.post(
            "/api/equipments",
            content_type="application/json",
            json={
                "equipment_type_id": equipment_bike_user_1.id,
                "label": self.random_short_id(),
                "description": self.random_short_id(),
            },
        )
        self.assert_401(response)

    def test_it_adds_an_equipment_with_minimal_payload(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_1_shoe.id,
                "label": "Test shoes",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "Test shoes" == equipment["label"]
        assert equipment["description"] is None
        assert equipment["is_active"] is True
        assert equipment_type_1_shoe.serialize() == equipment["equipment_type"]

    def test_it_returns_error_when_equipment_type_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": self.random_int(),
                "label": self.random_string(),
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "invalid equipment type id")

    def test_it_returns_error_when_equipment_type_is_inactive(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe_inactive: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_1_shoe_inactive.id,
                "label": self.random_string(),
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "equipment type is inactive")

    def test_it_adds_an_equipment_with_description(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        description = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "description": description,
                "equipment_type_id": equipment_type_1_shoe.id,
                "label": "Test shoes",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "Test shoes" == equipment["label"]
        assert equipment["description"] == description

    def test_it_raises_error_when_label_exceeds_50_characters(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        label = self.random_string(100)
        description = self.random_string()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "description": description,
                "equipment_type_id": equipment_type_1_shoe.id,
                "label": label,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "label exceeds 50 characters")

    @pytest.mark.parametrize("missing_arg", ["label", "equipment_type_id"])
    def test_it_returns_400_when_payload_is_invalid(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        missing_arg: str,
    ) -> None:
        data = {
            "description": "A piece of equipment with missing label",
            "equipment_type_id": equipment_type_1_shoe.id,
            "label": equipment_type_1_shoe.id,
        }
        del data[missing_arg]

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json=data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            (
                "the 'label' and 'equipment_type_id' parameters must be "
                "provided"
            ),
        )

    def test_it_returns_400_when_equipment_type_is_invalid(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": self.random_int(),
                "label": self.random_short_id(),
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "invalid equipment type")

    def test_it_returns_400_when_an_equipment_exists_with_the_same_label(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "description": self.random_short_id(),
                "equipment_type_id": equipment_shoes_user_1.equipment_type_id,
                "label": equipment_shoes_user_1.label,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            "equipment already exists with the same label",
        )

    def test_another_user_can_add_equipment_with_the_same_label(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_shoes_user_1.equipment_type_id,
                "label": equipment_shoes_user_1.label,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["label"] == equipment_shoes_user_1.label
        assert equipment["equipment_type"] == equipment_type_1_shoe.serialize()

    def test_it_returns_error_when_sport_not_found(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_3_cycling_transport: Sport,
    ) -> None:
        sport_id = self.random_int()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_2_bike.id,
                "label": "My Bike",
                "default_for_sport_ids": [
                    sport_id,
                    sport_3_cycling_transport.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, f"sport (id {sport_id}) does not exist")

    def test_it_adds_an_equipment_with_default_sports(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        sport_3_cycling_transport: Sport,
        user_1_sport_1_preference: UserSportPreference,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_2_bike.id,
                "label": "My Bike",
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_3_cycling_transport.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "My Bike" == equipment["label"]
        assert set(equipment["default_for_sport_ids"]) == {
            sport_1_cycling.id,
            sport_3_cycling_transport.id,
        }
        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment["id"])
        ).one()
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_3_cycling_transport.id,
                equipment_id=equipment.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_adds_a_piece_of_equipment_when_default_equipement_with_same_type_exists(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        sport_3_cycling_transport: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        # in this case, existing piece is removed
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_2_bike.id,
                "label": "My New Bike",
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_3_cycling_transport.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "My New Bike" == equipment["label"]
        assert set(equipment["default_for_sport_ids"]) == {
            sport_1_cycling.id,
            sport_3_cycling_transport.id,
        }
        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment["id"])
        ).one()
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_3_cycling_transport.id,
                equipment_id=equipment.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    @patch("fittrackee.equipments.utils.MAX_MISC_LIMIT", 2)
    def test_it_adds_a_piece_of_equipment_when_default_equipement_with_misc_type_already_exists(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        sport_3_cycling_transport: Sport,
        user_1_sport_1_preference: UserSportPreference,
        user_1_sport_2_preference: UserSportPreference,
        user_1_sport_3_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_misc_1_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1, equipment_misc_1_user_1],
            user_1_sport_1_preference,
        )
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1], user_1_sport_2_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_6_misc.id,
                "label": "Another Misc equipment",
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_3_cycling_transport.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "Another Misc equipment" == equipment["label"]
        assert set(equipment["default_for_sport_ids"]) == {
            sport_1_cycling.id,
            sport_3_cycling_transport.id,
        }
        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment["id"])
        ).one()
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment_bike_user_1,
            equipment,
            equipment_misc_1_user_1,
        }
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_misc_1_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )
        assert user_1_sport_2_preference.default_equipments.all() == [
            equipment_misc_1_user_1
        ]
        assert user_1_sport_3_preference.default_equipments.all() == [
            equipment
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_3_cycling_transport.id,
                equipment_id=equipment.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )

    @patch("fittrackee.equipments.utils.MAX_MISC_LIMIT", 2)
    def test_it_returns_error_when_with_misc_equipments_exceed_limit_regardless_active_status(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_6_misc: EquipmentType,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1, equipment_misc_2_user_1],
            user_1_sport_1_preference,
        )
        equipment_misc_2_user_1.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_6_misc.id,
                "label": "Another Misc equipment",
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_2_running.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            "a maximum of 2 pieces of Misc equipment can be added",
            status="limit_exceeded",
        )

    def test_it_adds_a_piece_of_equipment_when_default_equipement_with_different_type_exists(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        sport_3_cycling_transport: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        # in this case, existing piece is not removed
        self.add_user_sport_preference_equipement(
            [equipment_shoes_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_2_bike.id,
                "label": "My New Bike",
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_3_cycling_transport.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "My New Bike" == equipment["label"]
        assert set(equipment["default_for_sport_ids"]) == {
            sport_1_cycling.id,
            sport_3_cycling_transport.id,
        }
        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment["id"])
        ).first()
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment,
            equipment_shoes_user_1,
        }
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment
        ]

    def test_it_creates_sport_preference(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "label": "Test shoe",
                "equipment_type_id": equipment_type_1_shoe.id,
                "default_for_sport_ids": [sport_2_running.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        assert data["data"]["equipments"][0]["default_for_sport_ids"] == [
            sport_2_running.id
        ]
        sport_2_running_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_2_running.id
        ).one()
        assert (
            sport_2_running_pref.stopped_speed_threshold
            == sport_2_running.stopped_speed_threshold
        )
        assert (
            sport_2_running_pref.pace_speed_display
            == sport_2_running.pace_speed_display
        )

    def test_it_replaces_existing_default_equipment_on_creation(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1_sport_1_preference: UserSportPreference,
        user_1_sport_2_preference: UserSportPreference,
        user_2_sport_2_preference: UserSportPreference,
        equipment_type_1_shoe: EquipmentType,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_shoes_user_1], user_1_sport_2_preference
        )
        self.add_user_sport_preference_equipement(
            [equipment_shoes_user_2], user_2_sport_2_preference
        )
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_1_shoe.id,
                "label": "Another shoes",
                "default_for_sport_ids": [sport_2_running.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "Another shoes" == equipment["label"]
        assert equipment["default_for_sport_ids"] == [sport_2_running.id]
        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment["id"])
        ).one()
        assert user_1_sport_2_preference.default_equipments.all() == [
            equipment
        ]

        # user_1 cycling preferences remain unchanged
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]

        # user_2 running preferences remain unchanged
        assert user_2_sport_2_preference.default_equipments.all() == [
            equipment_shoes_user_2
        ]

    def test_it_returns_400_when_sport_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_type_2_bike: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "description": self.random_short_id(),
                "equipment_type_id": equipment_type_2_bike.id,
                "label": self.random_string(),
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_2_running.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            f"invalid sport '{sport_2_running.label}' for "
            f"equipment type '{equipment_type_2_bike.label}'",
        )

    def test_it_returns_400_when_visibility_is_invalid(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_1_shoe.id,
                "label": "Test shoes",
                "visibility": "invalid",
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "invalid visibility")

    def test_it_adds_an_equipment_with_given_visibility(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_1_shoe.id,
                "label": "Test shoes",
                "visibility": VisibilityLevel.PUBLIC.value,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert "Test shoes" == equipment["label"]
        assert equipment["visibility"] == VisibilityLevel.PUBLIC.value

    def test_it_adds_racket_as_equipment(
        self,
        app: Flask,
        user_1: User,
        sport_5_outdoor_tennis: "Sport",
        equipment_type_4_racket: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        equipment_label = "My new racket"

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_4_racket.id,
                "label": equipment_label,
                "default_for_sport_ids": [sport_5_outdoor_tennis.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 201
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["label"] == equipment_label
        assert set(equipment["default_for_sport_ids"]) == {
            sport_5_outdoor_tennis.id
        }
        assert Equipment.query.filter_by(label=equipment_label).count() == 1
        assert (
            UserSportPreference.query.filter_by(
                sport_id=sport_5_outdoor_tennis.id
            ).count()
            == 1
        )

    def test_it_adds_paddle_as_equipment(
        self,
        app: Flask,
        user_1: User,
        sport_7_kayaking: Sport,
        equipment_type_5_paddle: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        equipment_label = "My new paddle"

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_5_paddle.id,
                "label": equipment_label,
                "default_for_sport_ids": [sport_7_kayaking.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["label"] == equipment_label
        assert set(equipment["default_for_sport_ids"]) == {sport_7_kayaking.id}
        assert Equipment.query.filter_by(label=equipment_label).count() == 1
        assert (
            UserSportPreference.query.filter_by(
                sport_id=sport_7_kayaking.id
            ).count()
            == 1
        )

    def test_it_adds_misc_as_equipment(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_6_misc: "Equipment",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        equipment_label = "HR monitor"

        response = client.post(
            "/api/equipments",
            json={
                "equipment_type_id": equipment_type_6_misc.id,
                "label": equipment_label,
                "default_for_sport_ids": [sport_1_cycling.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 201
        data = json.loads(response.data.decode())
        assert "created" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["label"] == equipment_label
        assert set(equipment["default_for_sport_ids"]) == {sport_1_cycling.id}
        assert Equipment.query.filter_by(label=equipment_label).count() == 1
        assert (
            UserSportPreference.query.filter_by(
                sport_id=sport_1_cycling.id
            ).count()
            == 1
        )

    def test_expected_scope_is_equipments_write(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="post",
            endpoint="/api/equipments",
            invalid_scope="equipments:read",
            expected_endpoint_scope="equipments:write",
        )


class TestPatchEquipment(ApiTestCaseMixin, EquipmentMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, equipment_bike_user_1: Equipment
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/equipments/{equipment_bike_user_1.short_id}"
        )

        self.assert_401(response)

    def test_it_returns_404_when_equipment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{self.random_short_id()}",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    def test_it_returns_404_when_user_tries_to_modify_another_user_equipment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={"label": "new label"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    def test_it_returns_400_when_all_payload_is_missing(
        self, app: Flask, user_1: User, equipment_shoes_user_1: Equipment
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "no request data was supplied")

    def test_it_returns_400_when_payload_is_invalid(
        self, app: Flask, user_1: User, equipment_shoes_user_1: Equipment
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={self.random_short_id(): self.random_short_id()},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "no valid parameters supplied")

    @pytest.mark.parametrize(
        "input_values",
        [
            ("label", "new label"),
            ("description", "new description"),
            ("is_active", False),
            ("visibility", VisibilityLevel.FOLLOWERS.value),
        ],
    )
    def test_it_updates_equipment(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
        input_values: Tuple,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={input_values[0]: input_values[1]},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        equipment = response.json["data"]["equipments"][0]  # type: ignore
        assert equipment[input_values[0]] == input_values[1]

        response = client.get(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        equipment = response.json["data"]["equipments"][0]  # type: ignore
        assert equipment[input_values[0]] == input_values[1]

    def test_it_updates_equipment_with_same_label(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        label = equipment_bike_user_1.label
        new_description = self.random_short_id()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "label": label,
                "description": new_description,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        equipment = response.json["data"]["equipments"][0]  # type: ignore
        assert equipment["label"] == label
        assert equipment["description"] == new_description
        updated_equipment = Equipment.query.filter_by(
            id=equipment_bike_user_1.id
        ).one()
        assert updated_equipment.label == label
        assert updated_equipment.description == new_description

    def test_it_returns_400_when_label_exceeds_50_characters(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        label = self.random_string(100)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={
                "label": label,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "label exceeds 50 characters")

    def test_it_returns_400_on_editing_label_when_same_equipment_exists(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
        equipment_bike_user_1_inactive: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={"label": equipment_bike_user_1_inactive.label},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            "equipment already exists with the same label",
        )

    def test_it_returns_400_when_visibility_is_invalid(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={"visibility": "invalid"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "invalid visibility")

    def test_it_updates_equipment_type(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"equipment_type_id": equipment_type_1_shoe.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        equipment = response.json["data"]["equipments"][0]  # type: ignore
        assert equipment["equipment_type"] == equipment_type_1_shoe.serialize()

        response = client.get(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        equipment = response.json["data"]["equipments"][0]  # type: ignore
        assert equipment["equipment_type"] == equipment_type_1_shoe.serialize()

    def test_it_returns_error_when_equipment_type_does_not_exist(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"equipment_type_id": self.random_int()},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "invalid equipment type id")

    def test_it_returns_error_when_equipment_type_is_inactive(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe_inactive: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"equipment_type_id": equipment_type_1_shoe_inactive.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(response, "equipment type is inactive")

    def test_it_keeps_inactive_equipment_type(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        equipment_type_2_bike.is_active = False
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_label = self.random_string()

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "equipment_type_id": equipment_type_2_bike.id,
                "label": new_label,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        equipment = response.json["data"]["equipments"][0]  # type: ignore
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["label"] == new_label
        assert equipment_bike_user_1.label == new_label

    def test_it_removes_workout_associations_and_default_sports_on_type_change_from_bike_to_kayak(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_3_kayak: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
    ) -> None:
        # kayak type is invalid for cycling sports
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        another_workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()
        equipment_from_bike_to_kayak_user_1 = equipment_bike_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_bike_to_kayak_user_1.short_id}",
            json={"equipment_type_id": equipment_type_3_kayak.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert (
            equipment["equipment_type"] == equipment_type_3_kayak.serialize()
        )
        assert equipment["default_for_sport_ids"] == []
        assert equipment_from_bike_to_kayak_user_1.total_distance == 0.0
        assert (
            equipment_from_bike_to_kayak_user_1.total_duration == timedelta()
        )
        assert equipment_from_bike_to_kayak_user_1.total_moving == timedelta()
        assert equipment_from_bike_to_kayak_user_1.total_workouts == 0
        assert user_1_sport_1_preference.default_equipments.all() == []
        assert workout_cycling_user_1.equipments == []
        assert another_workout_cycling_user_1.equipments == []

    def test_it_removes_workout_associations_and_invalid_default_sports_on_type_change_from_bike_to_shoes(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_1_shoe: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
    ) -> None:
        # shoes type is valid for cycling sports
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        another_workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()
        equipment_from_bike_to_shoes_user_1 = equipment_bike_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_bike_to_shoes_user_1.short_id}",
            json={"equipment_type_id": equipment_type_1_shoe.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_1_shoe.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert equipment_from_bike_to_shoes_user_1.total_distance == 0.0
        assert (
            equipment_from_bike_to_shoes_user_1.total_duration == timedelta()
        )
        assert equipment_from_bike_to_shoes_user_1.total_moving == timedelta()
        assert equipment_from_bike_to_shoes_user_1.total_workouts == 0
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_from_bike_to_shoes_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_bike_to_shoes_user_1.id,
                equipment_type_id=equipment_type_1_shoe.id,  # check type
            )
            .first()
            is not None
        )
        assert workout_cycling_user_1.equipments == []
        assert another_workout_cycling_user_1.equipments == []

    def test_it_removes_workout_associations_and_invalid_default_sports_on_type_change_from_shoes_to_bike(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        user_1_sport_2_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_shoes_user_1, equipment_bike_user_1],
            user_1_sport_1_preference,
        )
        self.add_user_sport_preference_equipement(
            [equipment_shoes_user_1], user_1_sport_2_preference
        )
        workout_cycling_user_1.equipments = [
            equipment_bike_user_1,
            equipment_shoes_user_1,
        ]
        another_workout_cycling_user_1.equipments = [
            equipment_bike_user_1,
            equipment_shoes_user_1,
        ]
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()
        equipment_from_shoes_to_bike_user_1 = equipment_shoes_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_shoes_to_bike_user_1.short_id}",
            json={"equipment_type_id": equipment_type_2_bike.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["default_for_sport_ids"] == []
        assert equipment_from_shoes_to_bike_user_1.total_distance == 0.0
        assert (
            equipment_from_shoes_to_bike_user_1.total_duration == timedelta()
        )
        assert equipment_from_shoes_to_bike_user_1.total_moving == timedelta()
        assert equipment_from_shoes_to_bike_user_1.total_workouts == 0
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]
        assert user_1_sport_2_preference.default_equipments.all() == []
        assert workout_cycling_user_1.equipments == [equipment_bike_user_1]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,
            )
            .first()
            is not None
        )
        assert another_workout_cycling_user_1.equipments == [
            equipment_bike_user_1
        ]
        workout_running_user_1.equipments = []

    def test_it_removes_workout_associations_and_default_sports_on_type_change_from_bike_to_misc(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
    ) -> None:
        # misc type is valid for cycling sports
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        another_workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()
        equipment_from_bike_to_misc_user_1 = equipment_bike_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_bike_to_misc_user_1.short_id}",
            json={"equipment_type_id": equipment_type_6_misc.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_6_misc.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert equipment_bike_user_1.total_distance == (
            workout_cycling_user_1.distance  # type: ignore
            + another_workout_cycling_user_1.distance
        )
        assert equipment_bike_user_1.total_duration == (
            workout_cycling_user_1.duration
            + another_workout_cycling_user_1.duration
        )
        assert equipment_bike_user_1.total_moving == (
            workout_cycling_user_1.moving  # type: ignore
            + another_workout_cycling_user_1.moving
        )
        assert equipment_bike_user_1.total_workouts == 2
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_from_bike_to_misc_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_bike_to_misc_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )
        assert workout_cycling_user_1.equipments == [
            equipment_from_bike_to_misc_user_1
        ]
        assert another_workout_cycling_user_1.equipments == [
            equipment_from_bike_to_misc_user_1
        ]

    @patch("fittrackee.equipments.utils.MAX_MISC_LIMIT", 2)
    def test_it_returns_400_on_type_change_from_bike_to_misc_and_exceeds_limit(
        self,
        app: Flask,
        user_1: User,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [
                equipment_bike_user_1,
                equipment_misc_1_user_1,
                equipment_misc_2_user_1,
            ],
            user_1_sport_1_preference,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"equipment_type_id": equipment_type_6_misc.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            "a maximum of 2 pieces of Misc equipment can be added",
            "limit_exceeded",
        )

    def test_it_sets_equipement_item_as_default_for_given_sport_ids(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        equipment_type_1_shoe: EquipmentType,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={"default_for_sport_ids": [sport_2_running.id]},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        assert response.json["data"]["equipments"][0][  # type: ignore
            "default_for_sport_ids"
        ] == [sport_2_running.id]
        sport_preferences = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_2_running.id
        ).one()
        assert sport_preferences.default_equipments.all() == [
            equipment_shoes_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_2_running.id,
                equipment_id=equipment_shoes_user_1.id,
                equipment_type_id=equipment_type_1_shoe.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_returns_400_when_default_sport_id_is_invalid(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_2_running.id,
                ]
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            f"invalid sport '{sport_2_running.label}' for "
            f"equipment type '{equipment_type_2_bike.label}'",
        )

    def test_it_updates_default_sports_when_sport_preference_exists(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        sport_3_cycling_transport: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_3_cycling_transport.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert set(equipment["default_for_sport_ids"]) == {
            sport_1_cycling.id,
            sport_3_cycling_transport.id,
        }
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment_bike_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_3_cycling_transport.id,
                equipment_id=equipment_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_replaces_default_sports_when_sport_preference_exists_with_same_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        sport_2_running: Sport,
        user_1_sport_2_preference: UserSportPreference,
        equipment_shoes_user_1: Equipment,
        equipment_another_shoes_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_shoes_user_1], user_1_sport_2_preference
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_another_shoes_user_1.short_id}",
            json={
                "default_for_sport_ids": [
                    sport_2_running.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert set(equipment["default_for_sport_ids"]) == {
            sport_2_running.id,
        }
        assert user_1_sport_2_preference.default_equipments.all() == [
            equipment_another_shoes_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_2_running.id,
                equipment_id=equipment_another_shoes_user_1.id,
                equipment_type_id=equipment_type_1_shoe.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_updates_default_sports_when_sport_preference_exists_with_different_type(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        equipment_type_1_shoe: "EquipmentType",
        equipment_type_2_bike: "EquipmentType",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
        equipment_bike_user_1: "Equipment",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment_bike_user_1,
            equipment_shoes_user_1,
        }
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_shoes_user_1.id,
                equipment_type_id=equipment_type_1_shoe.id,  # check type
            )
            .first()
            is not None
        )

    @patch("fittrackee.equipments.utils.MAX_MISC_LIMIT", 2)
    def test_it_updates_default_sports_when_sport_preference_already_exists_with_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_6_misc: EquipmentType,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1],
            user_1_sport_1_preference,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_misc_2_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment_misc_1_user_1,
            equipment_misc_2_user_1,
        }
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_misc_1_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_misc_2_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )

    @patch("fittrackee.equipments.utils.MAX_MISC_LIMIT", 2)
    def test_it_returns_error_when_updating_default_sports_and_misc_equipments_exceed_limit(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_6_misc: EquipmentType,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
        equipment_misc_3_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1, equipment_misc_2_user_1],
            user_1_sport_1_preference,
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_misc_3_user_1.short_id}",
            json={
                "default_for_sport_ids": [
                    sport_1_cycling.id,
                    sport_2_running.id,
                ],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_400(
            response,
            "a maximum of 2 pieces of Misc equipment can be added",
            status="limit_exceeded",
        )

    def test_it_removes_default_sports(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"default_for_sport_ids": []},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["default_for_sport_ids"] == []
        assert user_1_sport_1_preference.default_equipments.all() == []
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_bike_user_1.id,
            )
            .first()
            is None
        )

    def test_it_does_not_remove_existing_default_sport_when_modifying_another_value(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_label = self.random_short_id()

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"label": new_label},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["label"] == new_label
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_keeps_default_sports_ids_when_changing_from_not_misc_to_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        equipment_from_bike_to_misc_user_1 = equipment_bike_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_bike_to_misc_user_1.short_id}",
            json={"equipment_type_id": equipment_type_6_misc.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_6_misc.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_from_bike_to_misc_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_bike_to_misc_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_keeps_default_sports_ids_when_changing_from_misc_to_not_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        equipment_from_misc_to_bike_user_1 = equipment_misc_1_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_misc_to_bike_user_1.short_id}",
            json={"equipment_type_id": equipment_type_2_bike.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_from_misc_to_bike_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_misc_to_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_removes_default_sports_ids_when_invalid_and_changing_from_misc_to_not_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_4_racket: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        equipment_from_misc_to_racket_user_1 = equipment_misc_1_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_misc_to_racket_user_1.short_id}",
            json={"equipment_type_id": equipment_type_4_racket.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert (
            equipment["equipment_type"] == equipment_type_4_racket.serialize()
        )
        # racket type is invalid for cycling
        assert equipment["default_for_sport_ids"] == []
        assert user_1_sport_1_preference.default_equipments.all() == []
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                equipment_id=equipment_from_misc_to_racket_user_1.id,
            )
            .first()
            is None
        )

    def test_it_adds_sports_ids_and_changes_type_from_misc_to_not_misc_type(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_2_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        equipment_from_misc_to_bike_user_1 = equipment_misc_1_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_misc_to_bike_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
                "equipment_type_id": equipment_type_2_bike.id,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment_misc_2_user_1,
            equipment_from_misc_to_bike_user_1,
        }
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_misc_2_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_misc_to_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_keeps_default_sports_ids_when_provided_and_changing_from_not_misc_to_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        equipment_from_bike_to_misc_user_1 = equipment_bike_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_bike_to_misc_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
                "equipment_type_id": equipment_type_6_misc.id,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_6_misc.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_from_bike_to_misc_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_bike_to_misc_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_keeps_default_sports_ids_when_provided_and_changing_from_misc_to_not_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1, equipment_misc_2_user_1],
            user_1_sport_1_preference,
        )
        db.session.commit()
        equipment_from_misc_to_bike_user_1 = equipment_misc_1_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_misc_to_bike_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
                "equipment_type_id": equipment_type_2_bike.id,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment_from_misc_to_bike_user_1,
            equipment_misc_2_user_1,
        }
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_misc_to_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_misc_2_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_updates_default_for_sport_ids_when_changing_from_non_misc_to_misc_type(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_6_misc: EquipmentType,
        equipment_racket_user_1: Equipment,
    ) -> None:
        equipment_from_racket_to_misc_user_1 = equipment_racket_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_racket_to_misc_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
                "equipment_type_id": equipment_type_6_misc.id,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_6_misc.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        sport_1_cycling_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_1_cycling.id
        ).one()
        assert sport_1_cycling_pref.default_equipments.all() == [
            equipment_from_racket_to_misc_user_1
        ]
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_racket_to_misc_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )

    def test_it_removes_invalid_default_for_sport_ids_when_provided_and_invalid_with_type_change(  # noqa
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_4_racket: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_misc_1_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        equipment_from_misc_to_racket_user_1 = equipment_misc_1_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_misc_to_racket_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
                "equipment_type_id": equipment_type_4_racket.id,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert (
            equipment["equipment_type"] == equipment_type_4_racket.serialize()
        )
        assert equipment["default_for_sport_ids"] == []
        assert user_1_sport_1_preference.default_equipments.all() == []
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                equipment_id=equipment_from_misc_to_racket_user_1.id,
            )
            .first()
            is None
        )

    def test_it_replaces_default_sports_on_change_from_misc_to_non_misc_type(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_type_2_bike: EquipmentType,
        equipment_type_6_misc: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_misc_1_user_1: Equipment,
        equipment_misc_2_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_misc_1_user_1, equipment_bike_user_1],
            user_1_sport_1_preference,
        )
        db.session.commit()
        equipment_from_misc_to_bike_user_1 = equipment_misc_2_user_1
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_from_misc_to_bike_user_1.short_id}",
            json={
                "default_for_sport_ids": [sport_1_cycling.id],
                "equipment_type_id": equipment_type_2_bike.id,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert set(user_1_sport_1_preference.default_equipments.all()) == {
            equipment_misc_1_user_1,
            equipment_from_misc_to_bike_user_1,
        }
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_misc_1_user_1.id,
                equipment_type_id=equipment_type_6_misc.id,  # check type
            )
            .first()
            is not None
        )
        assert (
            db.session.query(UserSportPreferenceEquipment)
            .filter_by(
                user_id=user_1.id,
                sport_id=sport_1_cycling.id,
                equipment_id=equipment_from_misc_to_bike_user_1.id,
                equipment_type_id=equipment_type_2_bike.id,  # check type
            )
            .first()
            is not None
        )

    def test_expected_scope_is_equipments_write(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="patch",
            endpoint=f"/api/equipments/{self.random_short_id()}",
            invalid_scope="equipments:read",
            expected_endpoint_scope="equipments:write",
        )


class TestRefreshEquipment(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, equipment_bike_user_1: Equipment
    ) -> None:
        client = app.test_client()

        response = client.post(
            f"/api/equipments/{equipment_bike_user_1.short_id}/refresh",
        )

        self.assert_401(response)

    def test_it_returns_404_when_equipment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/equipments/{self.random_short_id()}/refresh",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    def test_it_returns_404_when_equipment_belongs_to_another_user(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/equipments/{equipment_shoes_user_2.short_id}/refresh",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    def test_it_returns_null_total_when_no_associated_workouts(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        workout_running_user_1: Workout,
    ) -> None:
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        # invalid values
        equipment_bike_user_1.total_distance = self.random_int()
        equipment_bike_user_1.total_duration = timedelta(
            seconds=self.random_int()
        )
        equipment_bike_user_1.total_moving = timedelta(
            seconds=self.random_int()
        )
        equipment_bike_user_1.total_workouts = self.random_int()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/equipments/{equipment_bike_user_1.short_id}/refresh",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        assert equipment_bike_user_1.total_distance == 0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()
        assert equipment_bike_user_1.total_workouts == 0
        data = json.loads(response.data.decode())
        assert data["data"]["equipments"][0] == (
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        )
        # other equipment remains unchanged
        assert (
            equipment_shoes_user_1.total_distance
            == workout_running_user_1.distance
        )
        assert (
            equipment_shoes_user_1.total_duration
            == workout_running_user_1.duration
        )
        assert (
            equipment_shoes_user_1.total_moving
            == workout_running_user_1.moving
        )
        assert equipment_shoes_user_1.total_workouts == 1

    def test_it_recalculates_when_workouts_are_associated(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
        another_workout_cycling_user_1: Workout,
    ) -> None:
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        another_workout_cycling_user_1.equipments = [equipment_bike_user_1]
        db.session.commit()
        # invalid values
        equipment_bike_user_1.total_distance = self.random_int()
        equipment_bike_user_1.total_duration = timedelta(
            seconds=self.random_int()
        )
        equipment_bike_user_1.total_moving = timedelta(
            seconds=self.random_int()
        )
        equipment_bike_user_1.total_workouts = self.random_int()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            f"/api/equipments/{equipment_bike_user_1.short_id}/refresh",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        assert equipment_bike_user_1.total_distance == (
            workout_cycling_user_1.distance  # type: ignore
            + another_workout_cycling_user_1.distance  # type: ignore
        )
        assert equipment_bike_user_1.total_duration == (
            workout_cycling_user_1.duration
            + another_workout_cycling_user_1.duration
        )
        assert equipment_bike_user_1.total_moving == (
            workout_cycling_user_1.moving  # type: ignore
            + another_workout_cycling_user_1.moving  # type: ignore
        )
        assert equipment_bike_user_1.total_workouts == 2
        data = json.loads(response.data.decode())
        assert data["data"]["equipments"][0] == (
            jsonify_dict(equipment_bike_user_1.serialize(current_user=user_1))
        )
        # other equipment remains unchanged
        assert (
            equipment_shoes_user_1.total_distance
            == workout_running_user_1.distance
        )
        assert (
            equipment_shoes_user_1.total_duration
            == workout_running_user_1.duration
        )
        assert (
            equipment_shoes_user_1.total_moving
            == workout_running_user_1.moving
        )
        assert equipment_shoes_user_1.total_workouts == 1


class TestDeleteEquipment(ApiTestCaseMixin, EquipmentMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, equipment_bike_user_1: Equipment
    ) -> None:
        client = app.test_client()

        response = client.delete(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
        )

        self.assert_401(response)

    def test_it_deletes_given_equipment(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        """Tests deleting a piece of equipment with no workouts."""
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 204
        assert Equipment.query.all() == []

    def test_it_returns_404_when_equipment_does_not_exist(
        self,
        app: Flask,
        user_1: User,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/equipments/{self.random_short_id()}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = self.assert_404(response)
        assert len(data["data"]["equipments"]) == 0

    @pytest.mark.parametrize("input_admin", [True, False])
    def test_it_returns_404_when_user_tries_to_delete_equipment_for_other_user(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
        user_2: User,
        input_admin: bool,
    ) -> None:
        if input_admin:
            user_1.role = UserRole.ADMIN.value
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_2.email
        )

        response = client.delete(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        self.assert_404(response)

    def test_it_cannot_delete_equipment_with_workout(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
        workout_w_shoes_equipment: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = response.json
        assert response.status_code == 403
        assert "error" in data["status"]  # type: ignore
        assert (
            "Cannot delete equipment that has associated workouts. "
            f"Equipment id {equipment_shoes_user_1.short_id} has 1 "
            "associated workout. (Provide "
            "argument 'force' as a query parameter to override "
            "this check)" in data["message"]  # type: ignore
        )
        assert len(db.session.query(Equipment).all()) == 1

    def test_it_can_force_delete_equipment_with_workout(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_1: Equipment,
        workout_w_shoes_equipment: Workout,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # workout_w_shoes_equipment has one equipment; after delete
        # the workout should have no equipment

        response = client.delete(
            f"/api/equipments/{equipment_shoes_user_1.short_id}",
            query_string="force",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 204

        # check workout has no equipment
        w = (
            db.session.query(Workout)
            .filter(Workout.id == workout_w_shoes_equipment.id)
            .one()
        )
        assert w.equipments == []

        # check equipment_workout table is empty
        assert Equipment.query.all() == []

    def test_deleting_equipment_sets_sport_preferences_equipment_to_empty_list(
        self,
        app: Flask,
        user_1: User,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1], user_1_sport_1_preference
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        # workout_w_shoes_equipment has one equipment; after delete
        # the workout should have no equipment

        response = client.delete(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            query_string="force",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 204

        # check user sport preference has null equipment
        up = (
            db.session.query(UserSportPreference)
            .filter(
                UserSportPreference.user_id
                == user_1_sport_1_preference.user_id,
                UserSportPreference.sport_id == 1,
            )
            .one()
        )
        assert up.default_equipments.all() == []

    def test_expected_scope_is_equipments_write(
        self, app: Flask, user_1: User
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="delete",
            endpoint=f"/api/equipments/{self.random_short_id()}",
            invalid_scope="equipments:read",
            expected_endpoint_scope="equipments:write",
        )

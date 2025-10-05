import json
from datetime import datetime, timedelta, timezone
from typing import Tuple

import pytest
from flask import Flask
from sqlalchemy.dialects.postgresql import insert

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

from ..mixins import ApiTestCaseMixin
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


class TestPostEquipment(ApiTestCaseMixin):
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
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment
        ]

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
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_shoes_user_1.id,
                        "sport_id": user_1_sport_2_preference.sport_id,
                        "user_id": user_1_sport_2_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_shoes_user_2.id,
                        "sport_id": user_2_sport_2_preference.sport_id,
                        "user_id": user_2_sport_2_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                ],
            )
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
        equipment_type_1_shoe: EquipmentType,
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            "/api/equipments",
            json={
                "description": self.random_short_id(),
                "equipment_type_id": equipment_type_1_shoe.id,
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
            f"invalid sport '{sport_1_cycling.label}' for "
            f"equipment type '{equipment_type_1_shoe.label}'",
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


class TestPatchEquipment(ApiTestCaseMixin):
    def test_it_returns_error_if_user_is_not_authenticated(
        self, app: Flask, equipment_bike_user_1: Equipment
    ) -> None:
        client = app.test_client()

        response = client.get(
            f"/api/equipments/{equipment_bike_user_1.short_id}"
        )

        self.assert_401(response)

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

    def test_it_removes_workout_associations_and_default_sports_on_type_change(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
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
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        another_workout_cycling_user_1.equipments = [equipment_bike_user_1]
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={"equipment_type_id": equipment_type_1_shoe.id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_1_shoe.serialize()
        assert equipment["default_for_sport_ids"] == []
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()
        assert equipment_bike_user_1.total_workouts == 0
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
        assert user_1_sport_1_preference.default_equipments.all() == []
        assert workout_cycling_user_1.equipments == []
        assert another_workout_cycling_user_1.equipments == []
        assert workout_running_user_1.equipments == [equipment_shoes_user_1]

    def test_workouts_associations_remain_unchanged_when_no_type_change(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
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
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        new_label = self.random_string()

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "equipment_type_id": equipment_type_2_bike.id,
                "new_label": new_label,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_2_bike.serialize()
        assert equipment["default_for_sport_ids"] == [sport_1_cycling.id]
        assert (
            equipment_bike_user_1.total_distance
            == workout_cycling_user_1.distance
        )
        assert (
            equipment_bike_user_1.total_duration
            == workout_cycling_user_1.duration
        )
        assert (
            equipment_bike_user_1.total_moving == workout_cycling_user_1.moving
        )
        assert equipment_bike_user_1.total_workouts == 1
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
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]
        assert workout_cycling_user_1.equipments == [equipment_bike_user_1]
        assert workout_running_user_1.equipments == [equipment_shoes_user_1]

    def test_it_updates_type_and_default_sports(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        user_1_sport_1_preference: UserSportPreference,
        user_1_sport_2_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
        workout_running_user_1: Workout,
    ) -> None:
        # bike equipment, with 'Cycling (sport)' as default sport
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
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        another_workout_cycling_user_1.equipments = [equipment_bike_user_1]
        workout_running_user_1.equipments = [equipment_shoes_user_1]
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        # changed to
        # - shoes equipment type
        # - and 'Running' as default sport
        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "equipment_type_id": equipment_type_1_shoe.id,
                "default_for_sport_ids": [sport_2_running.id],
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["equipment_type"] == equipment_type_1_shoe.serialize()
        assert equipment["default_for_sport_ids"] == [sport_2_running.id]
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()
        assert equipment_bike_user_1.total_workouts == 0
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
        assert user_1_sport_1_preference.default_equipments.all() == []
        assert user_1_sport_2_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]
        assert workout_cycling_user_1.equipments == []
        assert another_workout_cycling_user_1.equipments == []
        assert workout_running_user_1.equipments == [equipment_shoes_user_1]

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

    def test_it_returns_404_when_user_try_to_modify_another_user_equipment(
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

    def test_it_updates_default_sports(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        sport_3_cycling_transport: Sport,
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
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment_bike_user_1
        ]

    def test_it_removes_existing_default_sport(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
        sport_1_cycling: Sport,
        sport_3_cycling_transport: Sport,
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
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_bike_user_1.short_id}",
            json={
                "default_for_sport_ids": [
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
        assert equipment["default_for_sport_ids"] == [
            sport_3_cycling_transport.id,
        ]
        assert user_1_sport_1_preference.default_equipments.all() == []
        sport_3_cycling_transport_pref = UserSportPreference.query.filter_by(
            user_id=user_1.id, sport_id=sport_3_cycling_transport.id
        ).one()
        assert sport_3_cycling_transport_pref.default_equipments.all() == [
            equipment_bike_user_1
        ]

    def test_it_removes_default_sports(
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
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

    def test_it_replaces_existing_default_equipment(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        sport_2_running: Sport,
        user_1_sport_1_preference: UserSportPreference,
        user_1_sport_2_preference: UserSportPreference,
        user_2_sport_2_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
        equipment_another_shoes_user_1: Equipment,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_shoes_user_1.id,
                        "sport_id": user_1_sport_2_preference.sport_id,
                        "user_id": user_1_sport_2_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_shoes_user_2.id,
                        "sport_id": user_2_sport_2_preference.sport_id,
                        "user_id": user_2_sport_2_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    },
                ],
            )
        )
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            f"/api/equipments/{equipment_another_shoes_user_1.short_id}",
            json={"default_for_sport_ids": [sport_2_running.id]},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert "success" in data["status"]
        assert len(data["data"]["equipments"]) == 1
        equipment = data["data"]["equipments"][0]
        assert equipment["default_for_sport_ids"] == [sport_2_running.id]
        assert user_1_sport_2_preference.default_equipments.all() == [
            equipment_another_shoes_user_1
        ]

        # user_1 cycling preferences remain unchanged
        assert user_1_sport_1_preference.default_equipments.all() == [
            equipment_bike_user_1
        ]

        # user_2 running preferences remain unchanged
        assert user_2_sport_2_preference.default_equipments.all() == [
            equipment_shoes_user_2
        ]

    def test_it_does_not_remove_existing_default_sport_when_modifying_another_value(  # noqa
        self,
        app: Flask,
        user_1: User,
        equipment_type_2_bike: EquipmentType,
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

    def test_it_returns_400_when_sport_is_invalid(
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


class TestDeleteEquipment(ApiTestCaseMixin):
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

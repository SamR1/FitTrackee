import pytest
from flask import Flask

from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.equipments.models import Equipment
from fittrackee.equipments.utils import handle_equipments
from fittrackee.users.models import User

from ..mixins import RandomMixin


class TestHandleEquipments(RandomMixin):
    def test_it_raises_error_when_equipment_ids_are_not_int(
        self, app: Flask, user_1: User
    ) -> None:
        with pytest.raises(
            InvalidEquipmentsException,
            match="equipment_ids must be an array of integers",
        ):
            handle_equipments(
                equipment_ids=['1'], auth_user=user_1  # type: ignore
            )

    def test_it_raises_error_when_equipment_ids_are_a_list(
        self, app: Flask, user_1: User
    ) -> None:
        with pytest.raises(
            InvalidEquipmentsException,
            match="equipment_ids must be an array of integers",
        ):
            handle_equipments(
                equipment_ids='1', auth_user=user_1  # type: ignore
            )

    def test_it_raises_error_when_equipment_does_not_exist(
        self, app: Flask, user_1: User
    ) -> None:
        equipment_id = self.random_int()
        with pytest.raises(
            InvalidEquipmentException,
            match=f"equipment with id {equipment_id} does not exist",
        ):
            handle_equipments(equipment_ids=[equipment_id], auth_user=user_1)

    def test_it_raises_error_when_equipment_does_not_belong_to_user(
        self,
        app: Flask,
        user_1: User,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=(
                f"equipment with id {equipment_shoes_user_2.id} does not exist"
            ),
        ):
            handle_equipments(
                equipment_ids=[equipment_shoes_user_2.id], auth_user=user_1
            )

    def test_it_raises_error_when_equipment_is_not_active(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1_inactive: Equipment,
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=(
                f"equipment with id {equipment_bike_user_1_inactive.id} "
                "is inactive"
            ),
        ):
            handle_equipments(
                equipment_ids=[equipment_bike_user_1_inactive.id],
                auth_user=user_1,
            )

    def test_it_returns_empty_list_when_no_equipment_ids(
        self, app: Flask, user_1: User
    ) -> None:
        equipments_list = handle_equipments(equipment_ids=[], auth_user=user_1)

        assert equipments_list == []

    def test_it_returns_none_when_provided_equipments_is_none(
        self, app: Flask, user_1: User
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=None, auth_user=user_1
        )

        assert equipments_list is None

    def test_it_returns_equipment_ids_list_when_no_existing_equipments(
        self, app: Flask, user_1: User, equipment_bike_user_1: Equipment
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[equipment_bike_user_1.id],
            auth_user=user_1,
            existing_equipments=[],
        )

        assert equipments_list == [equipment_bike_user_1]

    def test_it_keeps_inactive_equipment_when_it_already_exists(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1_inactive: Equipment,
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[
                equipment_bike_user_1_inactive.id,
            ],
            auth_user=user_1,
            existing_equipments=[equipment_bike_user_1_inactive],
        )

        assert equipments_list == [equipment_bike_user_1_inactive]

    def test_it_returns_updated_equipments_list(
        self,
        app: Flask,
        user_1: User,
        equipment_bike_user_1: Equipment,
        equipment_bike_user_1_inactive: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[
                equipment_bike_user_1.id,
                equipment_shoes_user_1.id,
            ],
            auth_user=user_1,
            existing_equipments=[
                equipment_bike_user_1_inactive,
                equipment_shoes_user_1,
            ],
        )

        assert set(equipments_list) == {  # type: ignore
            equipment_bike_user_1,
            equipment_shoes_user_1,
        }

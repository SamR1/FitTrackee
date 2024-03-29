import re

import pytest
from flask import Flask

from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.equipments.models import Equipment
from fittrackee.equipments.utils import handle_equipments
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport

from ..mixins import RandomMixin


class TestHandleEquipments(RandomMixin):
    def test_it_raises_error_when_equipment_ids_are_not_int(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        with pytest.raises(
            InvalidEquipmentsException,
            match="equipment_ids must be an array of integers",
        ):
            handle_equipments(
                equipment_ids=['1'],  # type: ignore
                auth_user=user_1,
                sport_id=sport_1_cycling.id,
            )

    def test_it_raises_error_when_equipment_ids_are_a_list(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        with pytest.raises(
            InvalidEquipmentsException,
            match="equipment_ids must be an array of integers",
        ):
            handle_equipments(
                equipment_ids='1',  # type: ignore
                auth_user=user_1,
                sport_id=sport_1_cycling.id,
            )

    def test_it_raises_error_when_equipment_does_not_exist(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        equipment_id = self.random_int()
        with pytest.raises(
            InvalidEquipmentException,
            match=f"equipment with id {equipment_id} does not exist",
        ):
            handle_equipments(
                equipment_ids=[equipment_id],
                auth_user=user_1,
                sport_id=sport_1_cycling.id,
            )

    def test_it_raises_error_when_equipment_does_not_belong_to_user(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_shoes_user_2: Equipment,
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=(
                f"equipment with id {equipment_shoes_user_2.id} does not exist"
            ),
        ):
            handle_equipments(
                equipment_ids=[equipment_shoes_user_2.id],
                auth_user=user_1,
                sport_id=sport_1_cycling.id,
            )

    def test_it_raises_error_when_equipment_is_not_active(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
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
                sport_id=sport_1_cycling.id,
            )

    def test_it_returns_empty_list_when_no_equipment_ids(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[], auth_user=user_1, sport_id=sport_1_cycling.id
        )

        assert equipments_list == []

    def test_it_returns_none_when_provided_equipments_is_none(
        self, app: Flask, user_1: User, sport_1_cycling: Sport
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=None, auth_user=user_1, sport_id=sport_1_cycling.id
        )

        assert equipments_list is None

    def test_it_raises_error_when_sport_not_found(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
    ) -> None:
        sport_id = self.random_int()
        with pytest.raises(
            InvalidEquipmentsException,
            match=f"sport id {sport_id} not found",
        ):
            handle_equipments(
                equipment_ids=[equipment_bike_user_1.id],
                auth_user=user_1,
                sport_id=sport_id,
            )

    def test_it_raises_error_when_equipment_type_is_not_valid_for_sport(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=re.escape(
                f"invalid equipment id {equipment_shoes_user_1.id} "
                f"for sport {sport_1_cycling.label}"
            ),
        ):
            handle_equipments(
                equipment_ids=[equipment_shoes_user_1.id],
                auth_user=user_1,
                sport_id=sport_1_cycling.id,
            )

    def test_it_returns_equipment_ids_list_when_no_existing_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1: Equipment,
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[equipment_bike_user_1.id],
            auth_user=user_1,
            sport_id=sport_1_cycling.id,
            existing_equipments=[],
        )

        assert equipments_list == [equipment_bike_user_1]

    def test_it_keeps_inactive_equipment_when_it_already_exists(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        equipment_bike_user_1_inactive: Equipment,
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[
                equipment_bike_user_1_inactive.id,
            ],
            auth_user=user_1,
            sport_id=sport_1_cycling.id,
            existing_equipments=[equipment_bike_user_1_inactive],
        )

        assert equipments_list == [equipment_bike_user_1_inactive]

    def test_it_returns_updated_equipments_list(
        self,
        app: Flask,
        user_1: User,
        sport_2_running: Sport,
        equipment_shoes_user_1: Equipment,
        equipment_another_shoes_user_1: Equipment,
        equipment_shoes_user_1_inactive: Equipment,
    ) -> None:
        equipments_list = handle_equipments(
            equipment_ids=[
                equipment_shoes_user_1.id,
                equipment_another_shoes_user_1.id,
            ],
            auth_user=user_1,
            sport_id=sport_2_running.id,
            existing_equipments=[
                equipment_shoes_user_1_inactive,
                equipment_shoes_user_1,
            ],
        )

        assert set(equipments_list) == {  # type: ignore
            equipment_another_shoes_user_1,
            equipment_shoes_user_1,
        }

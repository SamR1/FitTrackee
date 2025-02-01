from datetime import datetime, timedelta, timezone

import pytest

from fittrackee import db
from fittrackee.equipments.models import Equipment, EquipmentType
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout


@pytest.fixture()
def equipment_type_1_shoe() -> EquipmentType:
    equip_type = EquipmentType(label="Shoes", is_active=True)
    db.session.add(equip_type)
    db.session.commit()
    return equip_type


@pytest.fixture()
def equipment_type_1_shoe_inactive() -> EquipmentType:
    equip_type = EquipmentType(label="Shoes", is_active=False)
    db.session.add(equip_type)
    db.session.commit()
    return equip_type


@pytest.fixture()
def equipment_type_2_bike() -> EquipmentType:
    equip_type = EquipmentType(label="Bike", is_active=True)
    db.session.add(equip_type)
    db.session.commit()
    return equip_type


@pytest.fixture()
def equipment_bike_user_1(
    equipment_type_2_bike: EquipmentType, user_1: User
) -> Equipment:
    equip = Equipment(
        label="Test bike equipment",
        equipment_type_id=equipment_type_2_bike.id,
        description="A bike for testing purposes",
        user_id=user_1.id,
        is_active=True,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_bike_user_1_inactive(
    equipment_type_2_bike: EquipmentType, user_1: User
) -> Equipment:
    equip = Equipment(
        label="Test inactive bike equipment",
        equipment_type_id=equipment_type_2_bike.id,
        description="An inactive bike for testing purposes",
        user_id=user_1.id,
        is_active=False,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_shoes_user_1(
    equipment_type_1_shoe: EquipmentType, user_1: User
) -> Equipment:
    equip = Equipment(
        label="Test shoe equipment",
        equipment_type_id=equipment_type_1_shoe.id,
        description="An shoe equipment for testing purposes",
        user_id=user_1.id,
        is_active=True,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_shoes_user_1_inactive(
    equipment_type_1_shoe: EquipmentType, user_1: User
) -> Equipment:
    equip = Equipment(
        label="Inactive shoe equipment",
        equipment_type_id=equipment_type_1_shoe.id,
        description="An shoe equipment for testing purposes",
        user_id=user_1.id,
        is_active=False,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_another_shoes_user_1(
    equipment_type_1_shoe: EquipmentType, user_1: User
) -> Equipment:
    equip = Equipment(
        label="Another shoe equipment",
        equipment_type_id=equipment_type_1_shoe.id,
        description="An shoe equipment for testing purposes",
        user_id=user_1.id,
        is_active=True,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_shoes_user_2(
    equipment_type_1_shoe: EquipmentType, user_2: User
) -> Equipment:
    equip = Equipment(
        label="My shoes",
        equipment_type_id=equipment_type_1_shoe.id,
        description="New shoes",
        user_id=user_2.id,
        is_active=True,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def workout_w_shoes_equipment(
    sport_2_running: Sport,
    user_1: User,
    equipment_type_1_shoe: EquipmentType,
    equipment_shoes_user_1: Equipment,
) -> Workout:
    workout = Workout(
        user_id=user_1.id,
        sport_id=sport_2_running.id,
        workout_date=datetime(2017, 3, 20, tzinfo=timezone.utc),
        distance=5,
        duration=timedelta(seconds=1024),
    )
    db.session.add(workout)
    db.session.flush()
    workout.equipments.append(equipment_shoes_user_1)
    db.session.commit()
    return workout

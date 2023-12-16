from datetime import datetime, timedelta

import pytest

from fittrackee import db
from fittrackee.equipment.models import Equipment, EquipmentType
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport, Workout


@pytest.fixture()
def equipment_type_1_shoe() -> EquipmentType:
    equip_type = EquipmentType(label='Shoe', is_active=True)
    db.session.add(equip_type)
    db.session.commit()
    return equip_type


@pytest.fixture()
def equipment_type_1_shoe_inactive() -> EquipmentType:
    equip_type = EquipmentType(label='Shoe', is_active=False)
    db.session.add(equip_type)
    db.session.commit()
    return equip_type


@pytest.fixture()
def equipment_type_2_bike() -> EquipmentType:
    equip_type = EquipmentType(label='Bike', is_active=True)
    db.session.add(equip_type)
    db.session.commit()
    return equip_type


@pytest.fixture()
def equipment_1_bike() -> Equipment:
    equip = Equipment(
        label='Test bike equipment',
        equipment_type_id=2,
        description='A bike for testing purposes',
        user_id=1,
        is_active=True,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_1_bike_inactive() -> Equipment:
    equip = Equipment(
        label='Test bike equipment',
        equipment_type_id=2,
        description='An inactive bike for testing purposes',
        user_id=1,
        is_active=False,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def equipment_2_shoes() -> Equipment:
    equip = Equipment(
        label='Test shoe equipment',
        equipment_type_id=1,
        description='An shoe equipment for testing purposes',
        user_id=1,
        is_active=True,
    )
    db.session.add(equip)
    db.session.commit()
    return equip


@pytest.fixture()
def workout_w_equipment(
    sport_2_running: Sport,
    user_1: User,
    equipment_type_1_shoe: EquipmentType,
    equipment_2_shoes: Equipment,
) -> Workout:
    workout = Workout(
        user_id=1,
        sport_id=1,
        workout_date=datetime.strptime('20/03/2017', '%d/%m/%Y'),
        distance=5,
        duration=timedelta(seconds=1024),
    )
    workout.equipment.append(equipment_2_shoes)
    db.session.commit()
    return workout

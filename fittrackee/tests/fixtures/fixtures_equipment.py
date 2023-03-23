import datetime
from io import BytesIO
from typing import Generator, List
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from fittrackee import db
from fittrackee.equipment.models import Equipment, EquipmentType
from fittrackee.workouts.utils.maps import StaticMap

byte_io = BytesIO()
Image.new('RGB', (256, 256)).save(byte_io, 'PNG')
byte_image = byte_io.getvalue()

@pytest.fixture()
def equipment_type_1_shoe() -> EquipmentType:
    equip_type = EquipmentType(
        label='Shoe', 
        is_active=True
    )
    db.session.add(equip_type)
    db.session.commit()
    return equip_type

@pytest.fixture()
def equipment_type_1_shoe_inactive() -> EquipmentType:
    equip_type = EquipmentType(
        label='Shoe', 
        is_active=False
    )
    db.session.add(equip_type)
    db.session.commit()
    return equip_type

@pytest.fixture()
def equipment_type_2_bike() -> EquipmentType:
    equip_type = EquipmentType(
        label='Bike', 
        is_active=True
    )
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
        is_active=True
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
        is_active=False
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
        is_active=True
    )
    db.session.add(equip)
    db.session.commit()
    return equip


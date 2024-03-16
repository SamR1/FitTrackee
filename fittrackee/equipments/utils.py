from typing import List, Optional, Union

from fittrackee.equipments.models import Equipment
from fittrackee.users.models import User

from .exceptions import InvalidEquipmentException


def handle_equipments(
    equipment_ids: Optional[List],
    auth_user: User,
    existing_equipment_ids: Optional[List[Equipment]] = None,
) -> Union[List[Equipment], None]:
    equipments_list = None
    if equipment_ids is not None:
        equipments_list = []
        if not isinstance(equipment_ids, list):
            raise InvalidEquipmentException(
                "equipment_ids must be an array of integers"
            )
        for equipment_id in equipment_ids:
            if not isinstance(equipment_id, int):
                raise InvalidEquipmentException(
                    "equipment_ids must be an array of integers"
                )
            equipment = Equipment.query.filter_by(
                id=equipment_id, user_id=auth_user.id
            ).first()
            if not equipment:
                raise InvalidEquipmentException(
                    f"equipment with id {equipment_id} does not exist"
                )
            if not equipment.is_active and (
                not existing_equipment_ids
                or equipment not in existing_equipment_ids
            ):
                raise InvalidEquipmentException(
                    f"equipment with id {equipment_id} is inactive"
                )
            equipments_list.append(equipment)
    return equipments_list

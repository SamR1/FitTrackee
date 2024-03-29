from typing import List, Optional, Union

from fittrackee.equipments.models import Equipment
from fittrackee.users.models import User
from fittrackee.workouts.models import Sport

from .exceptions import InvalidEquipmentException, InvalidEquipmentsException

SPORT_EQUIPMENT_TYPES = {
    "Shoes": ["Hiking", "Mountaineering", "Running", "Trail", "Walking"],
    "Bike": [
        "Cycling (Sport)",
        "Cycling (Transport)",
        "Cycling (Trekking)",
        "Mountain Biking",
        "Mountain Biking (Electric)",
    ],
    "Bike Trainer": ["Cycling (Virtual)"],
    "Kayak_Boat": ["Rowing"],
    "Skis": ["Skiing (Alpine)", "Skiing (Cross Country)"],
    "Snowshoes": ["Snowshoes"],
}


def handle_equipments(
    equipment_ids: Optional[List[int]],
    auth_user: User,
    sport_id: int,
    existing_equipments: Optional[List[Equipment]] = None,
) -> Union[List[Equipment], None]:
    equipments_list = None

    if equipment_ids is not None:
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            raise InvalidEquipmentsException(f"sport id {sport_id} not found")

        equipments_list = []
        if not isinstance(equipment_ids, list):
            raise InvalidEquipmentsException(
                "equipment_ids must be an array of integers"
            )
        for equipment_id in equipment_ids:
            if not isinstance(equipment_id, int):
                raise InvalidEquipmentsException(
                    "equipment_ids must be an array of integers"
                )
            equipment = Equipment.query.filter_by(
                id=equipment_id, user_id=auth_user.id
            ).first()
            if not equipment:
                raise InvalidEquipmentException(
                    status="not_found",
                    message=f"equipment with id {equipment_id} does not exist",
                    equipment_id=equipment_id,
                )

            if sport.label not in SPORT_EQUIPMENT_TYPES.get(
                equipment.equipment_type.label, []
            ):
                raise InvalidEquipmentException(
                    status="invalid",
                    message=f"invalid equipment id {equipment.id} "
                    f"for sport {sport.label}",
                    equipment_id=equipment_id,
                )

            if not equipment.is_active and (
                not existing_equipments or equipment not in existing_equipments
            ):
                raise InvalidEquipmentException(
                    status="inactive",
                    message=f"equipment with id {equipment_id} is inactive",
                    equipment_id=equipment_id,
                )
            equipments_list.append(equipment)
    return equipments_list

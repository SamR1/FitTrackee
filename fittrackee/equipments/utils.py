from typing import List, Optional, Union

from fittrackee.equipments.models import Equipment
from fittrackee.users.models import User
from fittrackee.utils import decode_short_id
from fittrackee.workouts.models import Sport

from .exceptions import InvalidEquipmentException, InvalidEquipmentsException

SPORT_EQUIPMENT_TYPES = {
    "Shoes": [
        "Hiking",
        "Mountaineering",
        "Running",
        "Swimrun",
        "Trail",
        "Walking",
    ],
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
    equipment_short_ids: Optional[List[str]],
    auth_user: User,
    sport_id: int,
    existing_equipments: Optional[List[Equipment]] = None,
) -> Union[List[Equipment], None]:
    equipments_list: Optional[List[Equipment]] = None

    if equipment_short_ids is not None:
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            raise InvalidEquipmentsException(f"sport id {sport_id} not found")

        equipments_list = []
        if not isinstance(equipment_short_ids, list):
            raise InvalidEquipmentsException(
                "equipment_ids must be an array of strings"
            )

        # for now only one equipment par sport or workout
        if len(equipment_short_ids) > 1:
            raise InvalidEquipmentsException("only one equipment can be added")

        for equipment_short_id in equipment_short_ids:
            if not isinstance(equipment_short_id, str):
                raise InvalidEquipmentsException(
                    "equipment_ids must be an array of strings"
                )
            equipment = Equipment.query.filter_by(
                uuid=decode_short_id(equipment_short_id), user_id=auth_user.id
            ).first()
            if not equipment:
                raise InvalidEquipmentException(
                    status="not_found",
                    message=(
                        f"equipment with id {equipment_short_id} "
                        "does not exist"
                    ),
                    equipment_short_id=equipment_short_id,
                )

            if sport.label not in SPORT_EQUIPMENT_TYPES.get(
                equipment.equipment_type.label, []
            ):
                raise InvalidEquipmentException(
                    status="invalid",
                    message=(
                        f"invalid equipment id {equipment.short_id} "
                        f"for sport {sport.label}"
                    ),
                    equipment_short_id=equipment_short_id,
                )

            if not equipment.is_active and (
                not existing_equipments or equipment not in existing_equipments
            ):
                raise InvalidEquipmentException(
                    status="inactive",
                    message=(
                        f"equipment with id {equipment_short_id} "
                        "is inactive"
                    ),
                    equipment_short_id=equipment_short_id,
                )
            equipments_list.append(equipment)
    return equipments_list

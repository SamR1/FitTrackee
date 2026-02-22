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
        "Padel (Outdoor)",
        "Running",
        "Swimrun",
        "Tennis (Outdoor)",
        "Trail",
        "Walking",
        "Cycling (Sport)",
        "Cycling (Transport)",
        "Cycling (Trekking)",
        "Halfbike",
        "Mountain Biking",
        "Mountain Biking (Electric)",
    ],
    "Bike": [
        "Cycling (Sport)",
        "Cycling (Transport)",
        "Cycling (Trekking)",
        "Halfbike",
        "Mountain Biking",
        "Mountain Biking (Electric)",
    ],
    "Bike Trainer": ["Cycling (Virtual)"],
    "Board": ["Standup Paddleboarding", "Windsurfing"],
    "Kayak_Boat": [
        "Canoeing",
        "Canoeing (Whitewater)",
        "Kayaking",
        "Kayaking (Whitewater)",
        "Rowing",
    ],
    "Paddle": [
        "Canoeing",
        "Canoeing (Whitewater)",
        "Kayaking",
        "Kayaking (Whitewater)",
        "Rowing",
        "Standup Paddleboarding",
    ],
    "Skis": ["Skiing (Alpine)", "Skiing (Cross Country)"],
    "Racket": ["Padel (Outdoor)", "Tennis (Outdoor)"],
    "Snowshoes": ["Snowshoes"],
}
MAX_MISC_LIMIT = 5
TYPE_ERROR_MESSAGE = "equipment_ids must be an array of strings"


def handle_pieces_of_equipment(
    equipment_short_ids: Optional[List[str]],
    auth_user: User,
    sport_id: int,
    existing_equipments: Optional[List[Equipment]] = None,
) -> Union[List[Equipment], None]:
    if equipment_short_ids is None:
        return equipment_short_ids

    equipments_list: List[Equipment] = []
    if not equipment_short_ids:
        return equipments_list

    if not isinstance(equipment_short_ids, list):
        raise InvalidEquipmentsException(TYPE_ERROR_MESSAGE)

    sport = Sport.query.filter_by(id=sport_id).first()
    if not sport:
        raise InvalidEquipmentsException(f"sport id {sport_id} not found")

    equipment_types = []
    misc_count = 0
    for equipment_short_id in equipment_short_ids:
        if not isinstance(equipment_short_id, str):
            raise InvalidEquipmentsException(TYPE_ERROR_MESSAGE)

        equipment = Equipment.query.filter_by(
            uuid=decode_short_id(equipment_short_id), user_id=auth_user.id
        ).first()
        if not equipment:
            raise InvalidEquipmentException(
                status="not_found",
                message=(
                    f"equipment with id {equipment_short_id} does not exist"
                ),
                equipment_short_id=equipment_short_id,
            )

        if not equipment.is_active and (
            not existing_equipments or equipment not in existing_equipments
        ):
            raise InvalidEquipmentException(
                status="inactive",
                message=(
                    f"equipment with id {equipment_short_id} is inactive"
                ),
                equipment_short_id=equipment_short_id,
            )

        if equipment.equipment_type.label == "Misc":
            misc_count += 1
            if misc_count > MAX_MISC_LIMIT:
                raise InvalidEquipmentsException(
                    f"a maximum of {MAX_MISC_LIMIT} pieces of equipment "
                    "can be added"
                )
        else:
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

            if equipment.equipment_type in equipment_types:
                raise InvalidEquipmentsException(
                    "only one piece of equipment per type can be provided"
                )
            equipment_types.append(equipment.equipment_type)

        equipments_list.append(equipment)

    return equipments_list

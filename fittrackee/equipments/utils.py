from typing import List, Optional, Set, Union

from sqlalchemy.dialects.postgresql import insert

from fittrackee.equipments.models import Equipment, EquipmentType
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.utils import decode_short_id
from fittrackee.workouts.models import Sport

from .. import db
from .exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
    MiscEquipmentLimitExceededException,
)

SPORT_EQUIPMENT_TYPES = {
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
    "Skates": ["Ice Skating", "Inline Skating"],
    "Paddle": [
        "Canoeing",
        "Canoeing (Whitewater)",
        "Kayaking",
        "Kayaking (Whitewater)",
        "Rowing",
        "Standup Paddleboarding",
    ],
    "Racket": ["Padel (Outdoor)", "Tennis (Outdoor)"],
    "Skis": ["Skiing (Alpine)", "Skiing (Cross Country)"],
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
                    f"a maximum of {MAX_MISC_LIMIT} pieces of Misc equipment "
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


def handle_default_sports(
    default_for_sport_ids: List[int],
    auth_user: User,
    equipment_type: EquipmentType,
) -> List[UserSportPreference]:
    user_sport_preferences = []
    for sport_id in default_for_sport_ids:
        sport = Sport.query.filter_by(id=sport_id).first()
        if not sport:
            raise InvalidEquipmentsException(
                f"sport (id {sport_id}) does not exist"
            )

        # check if sport is valid for equipment type
        if (
            equipment_type.label != "Misc"
            and sport.label
            not in SPORT_EQUIPMENT_TYPES.get(equipment_type.label, [])
        ):
            raise InvalidEquipmentsException(
                f"invalid sport '{sport.label}' for equipment "
                f"type '{equipment_type.label}'"
            )

        user_sport_preference = UserSportPreference.query.filter_by(
            user_id=auth_user.id,
            sport_id=sport_id,
        ).first()
        if not user_sport_preference:
            user_sport_preference = UserSportPreference(
                user_id=auth_user.id,
                sport_id=sport_id,
                stopped_speed_threshold=sport.stopped_speed_threshold,
                pace_speed_display=sport.pace_speed_display,
            )
            db.session.add(user_sport_preference)
            db.session.flush()
        user_sport_preferences.append(user_sport_preference)
    return user_sport_preferences


def update_user_sport_equipment_preferences_for_misc_if_exist(
    equipment: "Equipment",
    user_sport_preferences: Optional[List["UserSportPreference"]],
    auth_user: "User",
    default_for_sport_ids: list[int],
) -> None:
    if not user_sport_preferences:
        return

    # can not exceeds max limit for Misc type
    sport_ids = []
    for sport_id in default_for_sport_ids:
        query = db.session.query(UserSportPreferenceEquipment).filter(
            UserSportPreferenceEquipment.c.user_id == auth_user.id,
            UserSportPreferenceEquipment.c.sport_id == sport_id,
            UserSportPreferenceEquipment.c.equipment_id != equipment.id,
            (
                UserSportPreferenceEquipment.c.equipment_type_id
                == equipment.equipment_type_id
            ),
        )
        if query.count() >= MAX_MISC_LIMIT:
            sport_ids.append(sport_id)

    if sport_ids:
        raise MiscEquipmentLimitExceededException(
            message=f"a maximum of {MAX_MISC_LIMIT} pieces of Misc "
            f"equipment can be added",
            sport_ids=sport_ids,
        )
    db.session.execute(
        insert(UserSportPreferenceEquipment)
        .values(
            [
                {
                    "equipment_id": equipment.id,
                    "equipment_type_id": equipment.equipment_type_id,
                    "sport_id": sport.sport_id,
                    "user_id": auth_user.id,
                }
                for sport in user_sport_preferences
            ]
        )
        .on_conflict_do_nothing()
    )


def update_user_sport_equipment_preferences_for_non_misc_if_exist(
    equipment: "Equipment",
    user_sport_preferences: Optional[List["UserSportPreference"]],
    auth_user: "User",
    default_for_sport_ids: list[int],
    skip_default_sports_update: Set[int],
) -> None:
    if not user_sport_preferences:
        return

    # remove existing default sports for equipment items with the same
    # equipment type
    db.session.query(UserSportPreferenceEquipment).filter(
        UserSportPreferenceEquipment.c.user_id == auth_user.id,
        UserSportPreferenceEquipment.c.sport_id.in_(
            list(set(default_for_sport_ids) - skip_default_sports_update)
        ),
        (
            UserSportPreferenceEquipment.c.equipment_type_id
            == equipment.equipment_type_id
        ),
    ).delete()

    # create new default sports for equipment item
    values = [
        {
            "equipment_id": equipment.id,
            "equipment_type_id": equipment.equipment_type_id,
            "sport_id": sport.sport_id,
            "user_id": auth_user.id,
        }
        for sport in user_sport_preferences
        if sport.sport_id not in skip_default_sports_update
    ]
    if values:
        db.session.execute(
            insert(UserSportPreferenceEquipment)
            .values(values)
            .on_conflict_do_nothing()
        )


def update_user_sport_equipment_preferences_if_exist(
    equipment: "Equipment",
    user_sport_preferences: Optional[List["UserSportPreference"]],
    auth_user: "User",
    default_for_sport_ids: list[int],
    skip_default_sports_update: Optional[Set[int]] = None,
) -> None:
    if equipment.equipment_type.label == "Misc":
        update_user_sport_equipment_preferences_for_misc_if_exist(
            equipment,
            user_sport_preferences,
            auth_user,
            default_for_sport_ids,
        )
    else:
        if skip_default_sports_update is None:
            skip_default_sports_update = set()
        update_user_sport_equipment_preferences_for_non_misc_if_exist(
            equipment,
            user_sport_preferences,
            auth_user,
            default_for_sport_ids,
            skip_default_sports_update,
        )

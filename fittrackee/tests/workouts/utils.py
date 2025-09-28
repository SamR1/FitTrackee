from io import BytesIO
from typing import TYPE_CHECKING, Dict, List, Optional

from werkzeug.datastructures import FileStorage

from fittrackee import db
from fittrackee.workouts.services import WorkoutsFromFileCreationService

if TYPE_CHECKING:
    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.visibility_levels import VisibilityLevel
    from fittrackee.workouts.models import Workout

MAX_WORKOUT_VALUES = {
    "drop": 99999.999,
    "speed": 9999.99,
    "distance": 999.999,
    "elevation": 9999.99,
}


def create_a_workout_with_file(
    user: "User",
    workout_file: str,
    *,
    sport_id: int = 1,
    extension: str = "gpx",
    workout_visibility: Optional["VisibilityLevel"] = None,
    equipments: Optional[List["Equipment"]] = None,
) -> "Workout":
    file_storage = FileStorage(
        filename=f"file.{extension}",
        stream=BytesIO(str.encode(workout_file)),
    )
    workouts_data: Dict = {"sport_id": sport_id}
    if workout_visibility:
        workouts_data["workout_visibility"] = workout_visibility.value
    service = WorkoutsFromFileCreationService(
        auth_user=user, file=file_storage, workouts_data=workouts_data
    )
    new_workout = service.create_workout_from_file(
        extension=extension, equipments=equipments
    )
    db.session.commit()
    return new_workout


def add_follower(user: "User", follower: "User") -> None:
    follower.send_follow_request_to(user)
    user.approves_follow_request_from(follower)

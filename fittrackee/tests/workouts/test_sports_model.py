from typing import TYPE_CHECKING

from fittrackee import db
from fittrackee.constants import PaceSpeedDisplay
from fittrackee.workouts.models import Sport, Workout

from ..mixins import EquipmentMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User, UserSportPreference


class TestSportModel:
    def test_sport_cycling_model(
        self, app: "Flask", sport_1_cycling: "Sport"
    ) -> None:
        assert sport_1_cycling.has_workouts is False
        assert sport_1_cycling.is_active is True
        assert sport_1_cycling.label == "Cycling (Sport)"
        assert sport_1_cycling.stopped_speed_threshold == 1.0
        assert sport_1_cycling.pace_speed_display == PaceSpeedDisplay.SPEED

        assert str(sport_1_cycling) == f"<Sport '{sport_1_cycling.label}'>"

    def test_it_serializes_sport_without_workout(
        self, app: "Flask", sport_1_cycling: "Sport"
    ) -> None:
        serialized_sport = sport_1_cycling.serialize()

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": True,
            "is_active_for_user": True,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 1.0,
        }

    def test_it_serializes_sport_with_workouts_and_check_workouts_as_false(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        assert sport_1_cycling.has_workouts is True

        serialized_sport = sport_1_cycling.serialize(check_workouts=False)

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": True,
            "is_active_for_user": True,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 1.0,
        }

    def test_it_serializes_sport_with_workouts_and_check_workouts_as_true(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        assert sport_1_cycling.has_workouts is True

        serialized_sport = sport_1_cycling.serialize(check_workouts=True)

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": True,
            "is_active_for_user": True,
            "has_workouts": True,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 1.0,
        }

    def test_it_serializes_running(
        self, app: "Flask", sport_2_running: Sport
    ) -> None:
        assert sport_2_running.stopped_speed_threshold == 0.1
        assert sport_2_running.pace_speed_display == PaceSpeedDisplay.PACE

        serialized_sport = sport_2_running.serialize()

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_2_running.id,
            "is_active": True,
            "is_active_for_user": True,
            "label": sport_2_running.label,
            "pace_speed_display": sport_2_running.pace_speed_display,
            "stopped_speed_threshold": sport_2_running.stopped_speed_threshold,
        }


class TestSportModelWithPreferences(EquipmentMixin):
    def test_sport_model_with_color_preference(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        user_1_sport_1_preference.color = "#00000"

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_1_sport_1_preference.serialize()
        )

        assert serialized_sport == {
            "color": "#00000",
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": True,
            "is_active_for_user": True,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 1.0,
        }

    def test_sport_model_with_is_active_preference(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        user_1_sport_1_preference.is_active = False

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_1_sport_1_preference.serialize()
        )

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": True,
            "is_active_for_user": False,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 1.0,
        }

    def test_inactive_sport_model_with_is_active_preference(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        sport_1_cycling.is_active = False
        user_1_sport_1_preference.is_active = True

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_1_sport_1_preference.serialize()
        )

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": False,
            "is_active_for_user": False,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 1.0,
        }

    def test_sport_model_with_threshold_preference(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        user_1_sport_1_preference.stopped_speed_threshold = 0.5
        db.session.commit()

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_1_sport_1_preference.serialize()
        )

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_1_cycling.id,
            "is_active": True,
            "is_active_for_user": True,
            "label": sport_1_cycling.label,
            "stopped_speed_threshold": 0.5,
        }

    def test_sport_model_with_default_equipments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
        equipment_bike_user_1: "Equipment",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        self.add_user_sport_preference_equipement(
            [equipment_bike_user_1, equipment_shoes_user_1],
            user_1_sport_1_preference,
        )

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_1_sport_1_preference.serialize()
        )

        assert len(serialized_sport["default_equipments"]) == 2
        assert (
            equipment_bike_user_1.serialize(current_user=user_1)
            in serialized_sport["default_equipments"]
        )
        assert (
            equipment_shoes_user_1.serialize(current_user=user_1)
            in serialized_sport["default_equipments"]
        )

    def test_sport_model_with_pace_preference(
        self,
        app: "Flask",
        user_1: "User",
        sport_2_running: "Sport",
        user_1_sport_2_preference: "UserSportPreference",
    ) -> None:
        user_1_sport_2_preference.pace_speed_display = PaceSpeedDisplay.SPEED
        db.session.commit()

        serialized_sport = sport_2_running.serialize(
            sport_preferences=user_1_sport_2_preference.serialize()
        )

        assert serialized_sport == {
            "color": None,
            "default_equipments": [],
            "id": sport_2_running.id,
            "is_active": True,
            "is_active_for_user": True,
            "label": sport_2_running.label,
            "pace_speed_display": PaceSpeedDisplay.SPEED,
            "stopped_speed_threshold": 0.1,
        }

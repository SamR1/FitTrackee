from typing import Dict, Optional

from flask import Flask
from sqlalchemy.dialects.postgresql import insert

from fittrackee import db
from fittrackee.equipments.models import Equipment
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.workouts.models import Sport, Workout


class TestSportModel:
    @staticmethod
    def assert_sport_model(
        sport: Sport, is_admin: Optional[bool] = False
    ) -> Dict:
        assert 1 == sport.id
        assert 'Cycling' == sport.label
        assert '<Sport \'Cycling\'>' == str(sport)

        serialized_sport = sport.serialize(is_admin=is_admin)
        assert serialized_sport['default_equipments'] == []
        assert serialized_sport['label'] == sport.label
        assert serialized_sport['id'] == sport.id
        assert serialized_sport['is_active'] is True
        assert serialized_sport['is_active_for_user'] is True
        assert serialized_sport['color'] is None
        assert serialized_sport['stopped_speed_threshold'] == 1
        return serialized_sport

    def test_sport_model_without_workout(
        self, app: Flask, sport_1_cycling: Sport
    ) -> None:
        serialized_sport = self.assert_sport_model(sport_1_cycling)
        assert 'has_workouts' not in serialized_sport

    def test_sport_model_with_workout(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_sport = self.assert_sport_model(sport_1_cycling)
        assert 'has_workouts' not in serialized_sport

    def test_sport_model_with_workout_as_admin(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        workout_cycling_user_1: Workout,
    ) -> None:
        serialized_sport = self.assert_sport_model(sport_1_cycling, True)
        assert serialized_sport['has_workouts'] is True


class TestSportModelWithPreferences:
    def test_sport_model_with_color_preference(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        user_sport_1_preference.color = '#00000'

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_sport_1_preference.serialize()
        )

        assert serialized_sport['default_equipments'] == []
        assert serialized_sport['id'] == 1
        assert serialized_sport['label'] == 'Cycling'
        assert serialized_sport['is_active'] is True
        assert serialized_sport['is_active_for_user'] is True
        assert serialized_sport['color'] == '#00000'
        assert serialized_sport['stopped_speed_threshold'] == 1
        assert 'has_workouts' not in serialized_sport

    def test_sport_model_with_is_active_preference(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        user_sport_1_preference.is_active = False

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_sport_1_preference.serialize()
        )

        assert serialized_sport['default_equipments'] == []
        assert serialized_sport['id'] == 1
        assert serialized_sport['label'] == 'Cycling'
        assert serialized_sport['is_active'] is True
        assert serialized_sport['is_active_for_user'] is False
        assert serialized_sport['color'] is None
        assert serialized_sport['stopped_speed_threshold'] == 1
        assert 'has_workouts' not in serialized_sport

    def test_inactive_sport_model_with_is_active_preference(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        sport_1_cycling.is_active = False
        user_sport_1_preference.is_active = True

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_sport_1_preference.serialize()
        )

        assert serialized_sport['default_equipments'] == []
        assert serialized_sport['id'] == 1
        assert serialized_sport['label'] == 'Cycling'
        assert serialized_sport['is_active'] is False
        assert serialized_sport['is_active_for_user'] is False
        assert serialized_sport['color'] is None
        assert serialized_sport['stopped_speed_threshold'] == 1
        assert 'has_workouts' not in serialized_sport

    def test_sport_model_with_threshold_preference(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
    ) -> None:
        user_sport_1_preference.stopped_speed_threshold = 0.5
        db.session.commit()

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_sport_1_preference.serialize()
        )

        assert serialized_sport['default_equipments'] == []
        assert serialized_sport['id'] == 1
        assert serialized_sport['label'] == 'Cycling'
        assert serialized_sport['is_active'] is True
        assert serialized_sport['is_active_for_user'] is True
        assert serialized_sport['color'] is None
        assert serialized_sport['stopped_speed_threshold'] == 0.5
        assert 'has_workouts' not in serialized_sport

    def test_sport_model_with_default_equipments(
        self,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        user_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
        equipment_shoes_user_1: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_sport_1_preference.sport_id,
                        "user_id": user_sport_1_preference.user_id,
                    },
                    {
                        "equipment_id": equipment_shoes_user_1.id,
                        "sport_id": user_sport_1_preference.sport_id,
                        "user_id": user_sport_1_preference.user_id,
                    },
                ]
            )
        )

        serialized_sport = sport_1_cycling.serialize(
            sport_preferences=user_sport_1_preference.serialize()
        )

        assert len(serialized_sport['default_equipments']) == 2
        assert (
            equipment_bike_user_1.serialize()
            in serialized_sport['default_equipments']
        )
        assert (
            equipment_shoes_user_1.serialize()
            in serialized_sport['default_equipments']
        )

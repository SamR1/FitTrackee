from datetime import timedelta
from typing import Dict

from flask import Flask
from sqlalchemy.dialects.postgresql import insert

from fittrackee import db
from fittrackee.equipments.models import Equipment, EquipmentType
from fittrackee.users.models import (
    User,
    UserSportPreference,
    UserSportPreferenceEquipment,
)
from fittrackee.workouts.models import Sport, Workout


class TestEquipmentModel:
    @staticmethod
    def assert_equipment_model(equip: Equipment) -> Dict:
        assert 1 == equip.id
        assert 'Test bike equipment' == equip.label
        assert '<Equipment 1 \'Test bike equipment\'>' == str(equip)

        serialized_equip = equip.serialize()
        assert serialized_equip['id'] == equip.id
        assert serialized_equip['user_id'] == 1
        assert serialized_equip['label'] == equip.label
        assert (
            serialized_equip['equipment_type']
            == equip.equipment_type.serialize()
        )
        assert serialized_equip['description'] == 'A bike for testing purposes'
        assert serialized_equip['is_active'] is True
        return serialized_equip

    def test_equipment_model_without_workout(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        equipment_bike_user_1.total_distance = 0.0
        equipment_bike_user_1.total_duration = timedelta()
        equipment_bike_user_1.total_moving = timedelta()
        equipment_bike_user_1.workouts_count = 0
        serialized_equip = self.assert_equipment_model(equipment_bike_user_1)
        assert serialized_equip['workouts_count'] == 0
        assert serialized_equip['total_distance'] == 0
        assert serialized_equip['total_duration'] == '0:00:00'
        assert serialized_equip['total_moving'] == '0:00:00'

    def test_equipment_model_with_workouts(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        user_1: User,
        workout_cycling_user_1: Workout,
        another_workout_cycling_user_1: Workout,
        equipment_bike_user_1: Equipment,
    ) -> None:
        equipment_bike_user_1.workouts = [
            workout_cycling_user_1,
            another_workout_cycling_user_1,
        ]
        db.session.commit()

        equipment_bike_user_1.total_distance = (
            workout_cycling_user_1.distance
            + another_workout_cycling_user_1.distance
        )
        equipment_bike_user_1.total_duration = (
            workout_cycling_user_1.duration
            + another_workout_cycling_user_1.duration
        )
        equipment_bike_user_1.total_moving = (
            workout_cycling_user_1.moving
            + another_workout_cycling_user_1.moving
        )
        equipment_bike_user_1.workouts_count = 2
        serialized_equip = self.assert_equipment_model(equipment_bike_user_1)
        assert (
            serialized_equip['total_distance']
            == equipment_bike_user_1.total_distance
        )
        assert serialized_equip['total_duration'] == str(
            equipment_bike_user_1.total_duration
        )
        assert serialized_equip['total_moving'] == str(
            equipment_bike_user_1.total_moving
        )
        assert (
            serialized_equip['workouts_count']
            == equipment_bike_user_1.workouts_count
        )

        # remove one equipment
        equipment_bike_user_1.workouts = [workout_cycling_user_1]
        db.session.commit()

        equipment_bike_user_1.total_distance = workout_cycling_user_1.distance
        equipment_bike_user_1.total_duration = workout_cycling_user_1.moving
        equipment_bike_user_1.total_moving = workout_cycling_user_1.moving
        equipment_bike_user_1.workouts_count = 1
        serialized_equip = self.assert_equipment_model(equipment_bike_user_1)
        assert (
            serialized_equip['total_distance']
            == equipment_bike_user_1.total_distance
        )
        assert serialized_equip['total_duration'] == str(
            equipment_bike_user_1.total_duration
        )
        assert serialized_equip['total_moving'] == str(
            equipment_bike_user_1.total_moving
        )
        assert (
            serialized_equip['workouts_count']
            == equipment_bike_user_1.workouts_count
        )

        # remove all equipments
        equipment_bike_user_1.workouts = []
        db.session.commit()

        equipment_bike_user_1.total_distance = 0.0
        equipment_bike_user_1.total_duration = timedelta()
        equipment_bike_user_1.workouts_count = 0
        serialized_equip = self.assert_equipment_model(equipment_bike_user_1)
        assert (
            serialized_equip['total_distance']
            == equipment_bike_user_1.total_distance
        )
        assert serialized_equip['total_duration'] == str(
            equipment_bike_user_1.total_duration
        )
        assert serialized_equip['total_moving'] == str(
            equipment_bike_user_1.total_moving
        )
        assert (
            serialized_equip['workouts_count']
            == equipment_bike_user_1.workouts_count
        )

    def test_equipment_model_with_sport_association(
        self,
        app: Flask,
        sport_1_cycling: Sport,
        user_1: User,
        user_sport_1_preference: UserSportPreference,
        equipment_bike_user_1: Equipment,
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_sport_1_preference.sport_id,
                        "user_id": user_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.add(equipment_bike_user_1)
        db.session.commit()

        serialized_equip = self.assert_equipment_model(equipment_bike_user_1)

        assert serialized_equip['default_for_sport_ids'] == [
            sport_1_cycling.id
        ]


class TestEquipmentTypeModel:
    @staticmethod
    def assert_equipment_type_model(
        equip_type: EquipmentType, is_admin: bool = False
    ) -> Dict:
        assert 1 == equip_type.id
        assert 'Shoe' == equip_type.label
        assert '<EquipmentType \'Shoe\'>' == str(equip_type)

        serialized_equip = equip_type.serialize(is_admin=is_admin)
        assert serialized_equip['id'] == equip_type.id
        assert serialized_equip['label'] == equip_type.label
        assert serialized_equip['is_active'] is True
        return serialized_equip

    def test_equipment_type_model(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        serialized_equip_type = self.assert_equipment_type_model(
            equipment_type_1_shoe
        )
        assert 'has_workouts' not in serialized_equip_type

    def test_equipment_type_model_as_admin(
        self,
        app: Flask,
        user_1: User,
        equipment_type_1_shoe: EquipmentType,
        equipment_type_2_bike: EquipmentType,
        equipment_bike_user_1: Equipment,
    ) -> None:
        serialized_equip_type = self.assert_equipment_type_model(
            equipment_type_1_shoe, is_admin=True
        )
        assert serialized_equip_type['has_equipments'] is False

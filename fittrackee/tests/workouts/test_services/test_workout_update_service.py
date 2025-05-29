import re
from datetime import timedelta
from typing import TYPE_CHECKING, Dict

import pytest

from fittrackee import db
from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.tests.mixins import RandomMixin
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import WorkoutException
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Record,
)
from fittrackee.workouts.services import WorkoutUpdateService

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport, Workout


class TestWorkoutUpdateServiceInitForWorkoutWithoutFile(RandomMixin):
    def test_it_instantiates_service_with_minimal_workout_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        # only one key
        workout_data = {"notes": "some notes"}
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, workout_data
        )

        assert service.auth_user == user_1
        assert service.equipments_list is None
        assert service.sport is None
        assert service.with_file is False
        assert service.workout == workout_cycling_user_1
        assert service.workout_data == workout_data

    def test_it_instantiates_service_with_all_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        workout_data = {
            "sport_id": sport_2_running.id,
            "workout_date": "2025-02-08 09:00",
            "ascent": 10,
            "descent": 35,
            "description": "just a description",
            "equipment_ids": [equipment_shoes_user_1.short_id],
            "notes": "some notes",
            "title": "workout title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, workout_data
        )

        assert service.auth_user == user_1
        assert service.equipments_list == [equipment_shoes_user_1]
        assert service.sport == sport_2_running
        assert service.with_file is False
        assert service.workout == workout_cycling_user_1
        assert service.workout_data == workout_data

    def test_it_raises_error_when_sport_id_is_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        sport_id = 999
        with pytest.raises(
            WorkoutException,
            match="sport id 999 not found",
        ):
            WorkoutUpdateService(
                user_1, workout_cycling_user_1, {"sport_id": sport_id}
            )

    def test_it_raises_error_when_key_is_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        workout_data = {
            "analysis_visibility": VisibilityLevel.PUBLIC,
            "ascent": 10,
            "descent": 35,
            "description": "just a description",
            "equipment_ids": [equipment_shoes_user_1.short_id],
            "notes": "some notes",
            "title": "workout title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }

        with pytest.raises(
            WorkoutException,
            match=re.escape(
                "invalid key ('analysis_visibility') for workout without gpx"
            ),
        ):
            WorkoutUpdateService(user_1, workout_cycling_user_1, workout_data)

    @pytest.mark.parametrize(
        "input_description, input_workout_data",
        [
            ("missing descent", {"ascent": 50}),
            ("missing ascent", {"descent": 50}),
            ("ascent is None", {"ascent": None, "descent": 50}),
            ("descent is None", {"ascent": 50, "descent": None}),
            ("invalid ascent", {"ascent": -1, "descent": 50}),
            ("invalid descent", {"ascent": 50, "descent": -2}),
        ],
    )
    def test_it_raises_error_when_elevation_data_are_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        input_description: str,
        input_workout_data: Dict,
    ) -> None:
        with pytest.raises(
            WorkoutException, match="invalid ascent or descent"
        ):
            WorkoutUpdateService(
                user_1, workout_cycling_user_1, input_workout_data
            )

    def test_it_raises_error_when_equipment_id_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        equipment_short_id = self.random_short_id()
        with pytest.raises(
            InvalidEquipmentException,
            match=f"equipment with id {equipment_short_id} does not exist",
        ):
            WorkoutUpdateService(
                user_1,
                workout_cycling_user_1,
                {"equipment_ids": [equipment_short_id]},
            )

    def test_it_raises_error_when_equipment_is_invalid_for_sport(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=re.escape(
                f"invalid equipment id {equipment_shoes_user_1.short_id} "
                f"for sport {sport_1_cycling.label}"
            ),
        ):
            WorkoutUpdateService(
                user_1,
                workout_cycling_user_1,
                {"equipment_ids": [equipment_shoes_user_1.short_id]},
            )

    def test_it_raises_error_when_multiple_equipments_are_provided(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_running_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
        equipment_another_shoes_user_1: "Equipment",
    ) -> None:
        with pytest.raises(
            InvalidEquipmentsException,
            match="only one equipment can be added",
        ):
            WorkoutUpdateService(
                user_1,
                workout_running_user_1,
                {
                    "equipment_ids": [
                        equipment_shoes_user_1.short_id,
                        equipment_another_shoes_user_1.short_id,
                    ]
                },
            )

    def test_it_raises_error_when_equipment_belongs_to_another_user(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        user_2: "User",
        workout_running_user_1: "Workout",
        equipment_shoes_user_2: "Equipment",
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=(
                f"equipment with id {equipment_shoes_user_2.short_id} "
                f"does not exist"
            ),
        ):
            WorkoutUpdateService(
                user_1,
                workout_running_user_1,
                {"equipment_ids": [equipment_shoes_user_2.short_id]},
            )

    def test_it_raises_error_when_equipment_is_inactive(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_bike_user_1_inactive: "Equipment",
    ) -> None:
        with pytest.raises(
            InvalidEquipmentException,
            match=(
                f"equipment with id {equipment_bike_user_1_inactive.short_id}"
                " is inactive"
            ),
        ):
            WorkoutUpdateService(
                user_1,
                workout_cycling_user_1,
                {"equipment_ids": [equipment_bike_user_1_inactive.short_id]},
            )

    def test_it_does_not_raise_error_when_inactive_equipment_is_already_associated(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_bike_user_1_inactive: "Equipment",
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1_inactive]

        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"equipment_ids": [equipment_bike_user_1_inactive.short_id]},
        )

        assert service.equipments_list == [equipment_bike_user_1_inactive]


class TestWorkoutUpdateServiceInitForWorkoutWithFile:
    def test_it_instantiates_service_with_minimal_workout_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        # only one key
        workout_data = {"notes": "some notes"}
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, workout_data
        )

        assert service.auth_user == user_1
        assert service.equipments_list is None
        assert service.sport is None
        assert service.with_file is True
        assert service.workout == workout_cycling_user_1
        assert service.workout_data == workout_data

    def test_it_instantiates_service_with_all_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        workout_data = {
            "analysis_visibility": VisibilityLevel.PUBLIC,
            "description": "just a description",
            "equipment_ids": [equipment_shoes_user_1.short_id],
            "map_visibility": VisibilityLevel.PUBLIC,
            "notes": "some notes",
            "sport_id": sport_2_running.id,
            "title": "workout title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, workout_data
        )

        assert service.auth_user == user_1
        assert service.equipments_list == [equipment_shoes_user_1]
        assert service.sport == sport_2_running
        assert service.with_file is True
        assert service.workout == workout_cycling_user_1
        assert service.workout_data == workout_data

    def test_it_raises_error_when_sport_id_is_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        sport_id = 999
        with pytest.raises(
            WorkoutException,
            match="sport id 999 not found",
        ):
            WorkoutUpdateService(
                user_1, workout_cycling_user_1, {"sport_id": sport_id}
            )

    def test_it_raises_error_when_key_is_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        workout_cycling_user_1.gpx = "some path"
        workout_data = {
            "analysis_visibility": VisibilityLevel.PUBLIC,
            "distance": 10,
            "duration": 3600,
            "description": "just a description",
            "equipment_ids": [equipment_shoes_user_1.short_id],
            "notes": "some notes",
            "title": "workout title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }

        with pytest.raises(
            WorkoutException,
            match=re.escape(
                "invalid keys ('distance', 'duration') for workout with gpx"
            ),
        ):
            WorkoutUpdateService(user_1, workout_cycling_user_1, workout_data)


class TestWorkoutUpdateServiceUpdate(RandomMixin):
    """
    for workouts with and without file
    """

    def test_it_updates_sport(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        initial_data = workout_cycling_user_1.get_workout_data(
            user=user_1, additional_data=True
        )
        updated_data = {"sport_id": sport_2_running.id}
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, updated_data
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.get_workout_data(
            user=user_1, additional_data=True
        ) == {**initial_data, **updated_data}
        assert workout_cycling_user_1.equipments == []

    @pytest.mark.parametrize(
        "input_workout_data_key, input_workout_data_limit, "
        "expected_workout_data_limit",
        [
            (
                "description",
                DESCRIPTION_MAX_CHARACTERS,
                DESCRIPTION_MAX_CHARACTERS,
            ),
            (
                "description",
                DESCRIPTION_MAX_CHARACTERS + 1,
                DESCRIPTION_MAX_CHARACTERS,
            ),
            ("description", 0, 0),  # empties value
            ("notes", NOTES_MAX_CHARACTERS, NOTES_MAX_CHARACTERS),
            ("notes", NOTES_MAX_CHARACTERS + 1, NOTES_MAX_CHARACTERS),
            ("notes", 0, 0),  # empties value
            ("title", TITLE_MAX_CHARACTERS, TITLE_MAX_CHARACTERS),
            ("title", TITLE_MAX_CHARACTERS + 1, TITLE_MAX_CHARACTERS),
            ("title", 0, 0),  # empties value
        ],
    )
    def test_it_updates_workout_value_depending_on_max_length_limit(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        input_workout_data_key: str,
        input_workout_data_limit: int,
        expected_workout_data_limit: int,
    ) -> None:
        updated_data = self.random_string(length=input_workout_data_limit)
        setattr(
            workout_cycling_user_1,
            input_workout_data_key,
            self.random_string(length=8),
        )
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {input_workout_data_key: updated_data},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            getattr(workout_cycling_user_1, input_workout_data_key)
            == updated_data[:expected_workout_data_limit]
        )

    def test_it_updates_equipment_when_sport_is_not_provided(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"equipment_ids": [equipment_bike_user_1.short_id]},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.equipments == [equipment_bike_user_1]
        assert equipment_bike_user_1.total_workouts == 1
        assert (
            equipment_bike_user_1.total_distance
            == workout_cycling_user_1.distance
        )
        assert (
            equipment_bike_user_1.total_duration
            == workout_cycling_user_1.duration
        )
        assert (
            equipment_bike_user_1.total_moving == workout_cycling_user_1.moving
        )

    def test_it_updates_equipment_when_sport_is_provided(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {
                "sport_id": sport_2_running.id,
                "equipment_ids": [equipment_shoes_user_1.short_id],
            },
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.sport_id == sport_2_running.id
        assert workout_cycling_user_1.equipments == [equipment_shoes_user_1]

    def test_it_removes_equipment(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"equipment_ids": []},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.equipments == []

    def test_it_removes_invalid_equipment_on_sport_change(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workout_cycling_user_1.equipments = [equipment_bike_user_1]
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"sport_id": sport_2_running.id},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.equipments == []

    def test_it_updates_workout_visibility(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"workout_visibility": VisibilityLevel.PUBLIC},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.workout_visibility == VisibilityLevel.PUBLIC
        )


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutUpdateServiceUpdateForWorkoutWithoutFile(RandomMixin):
    def test_it_updates_elevation_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, {"ascent": 10, "descent": 30}
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.ascent == 10
        assert workout_cycling_user_1.descent == 30
        ha_record = Record.query.filter_by(record_type="HA").one()
        assert ha_record.value == 10

    def test_it_empties_elevation_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.ascent = 100
        workout_cycling_user_1.descent = 150
        db.session.commit()
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, {"ascent": None, "descent": None}
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.ascent is None
        assert workout_cycling_user_1.descent is None
        assert Record.query.filter_by(record_type="HA").first() is None
        assert Record.query.count() == 4

    def test_it_updates_workout_date_when_no_timezone_set(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_date = "2025-02-15 15:05"
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"workout_date": "2025-02-15 15:05"},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            str(workout_cycling_user_1.workout_date)
            == f"{workout_date}:00+00:00"
        )

    def test_it_updates_workout_date_when_timezone_is_set(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1_paris: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        service = WorkoutUpdateService(
            user_1_paris,
            workout_cycling_user_1,
            {"workout_date": "2025-02-15 15:05"},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            str(workout_cycling_user_1.workout_date)
            == "2025-02-15 14:05:00+00:00"
        )

    def test_it_updates_duration(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        duration = 7200
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, {"duration": duration}
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert workout_cycling_user_1.duration == timedelta(seconds=duration)
        assert workout_cycling_user_1.moving == timedelta(seconds=duration)
        assert float(workout_cycling_user_1.max_speed) == 5.0  # type: ignore
        assert float(workout_cycling_user_1.ave_speed) == 5.0  # type: ignore
        assert Record.query.filter_by(record_type="AS").one().value == 5.0
        assert Record.query.filter_by(
            record_type="LD"
        ).one().value == timedelta(seconds=duration)
        assert Record.query.filter_by(record_type="MS").one().value == 5.0

    def test_it_updates_distance(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        distance = 15.0
        service = WorkoutUpdateService(
            user_1, workout_cycling_user_1, {"distance": distance}
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert float(workout_cycling_user_1.distance) == distance  # type: ignore
        assert float(workout_cycling_user_1.max_speed) == 15.0  # type: ignore
        assert float(workout_cycling_user_1.ave_speed) == 15.0  # type: ignore
        assert Record.query.filter_by(record_type="AS").one().value == 15.0
        assert Record.query.filter_by(record_type="MS").one().value == 15.0


class TestWorkoutUpdateServiceUpdateForWorkoutWithFile(RandomMixin):
    def test_it_updates_map_visibility(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.map_visibility = VisibilityLevel.PUBLIC
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"map_visibility": VisibilityLevel.FOLLOWERS},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.map_visibility == VisibilityLevel.FOLLOWERS
        )

    @pytest.mark.parametrize(
        "input_map_visibility,input_analysis_visibility",
        [
            (VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE),
            (VisibilityLevel.PUBLIC, VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_updates_map_visibility_with_valid_value(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        input_map_visibility: "VisibilityLevel",
        input_analysis_visibility: "VisibilityLevel",
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = input_analysis_visibility
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"map_visibility": input_map_visibility},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.map_visibility == input_analysis_visibility
        )

    def test_it_updates_analysis_visibility(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        workout_cycling_user_1.analysis_visibility = VisibilityLevel.PUBLIC
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"analysis_visibility": VisibilityLevel.FOLLOWERS},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.analysis_visibility
            == VisibilityLevel.FOLLOWERS
        )

    @pytest.mark.parametrize(
        "input_analysis_visibility,input_workout_visibility",
        [
            (VisibilityLevel.FOLLOWERS, VisibilityLevel.PRIVATE),
            (VisibilityLevel.PUBLIC, VisibilityLevel.FOLLOWERS),
        ],
    )
    def test_it_updates_analysis_visibility_with_valid_value(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        workout_cycling_user_1: "Workout",
        input_analysis_visibility: "VisibilityLevel",
        input_workout_visibility: "VisibilityLevel",
    ) -> None:
        workout_cycling_user_1.gpx = "file.gpx"
        workout_cycling_user_1.workout_visibility = input_workout_visibility
        service = WorkoutUpdateService(
            user_1,
            workout_cycling_user_1,
            {"analysis_visibility": input_analysis_visibility},
        )

        service.update()
        db.session.commit()

        db.session.refresh(workout_cycling_user_1)
        assert (
            workout_cycling_user_1.analysis_visibility
            == input_workout_visibility
        )

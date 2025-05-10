from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Dict

import pytest
from sqlalchemy.dialects.postgresql import insert

from fittrackee import db
from fittrackee.database import PSQL_INTEGER_LIMIT
from fittrackee.equipments.exceptions import InvalidEquipmentsException
from fittrackee.tests.mixins import RandomMixin
from fittrackee.users.models import UserSportPreferenceEquipment
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import (
    WorkoutExceedingValueException,
    WorkoutException,
)
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    WORKOUT_VALUES_LIMIT,
    Record,
    Sport,
    Workout,
    WorkoutSegment,
)
from fittrackee.workouts.services.workout_creation_service import (
    WorkoutCreationService,
    WorkoutData,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User, UserSportPreference


class TestWorkoutCreationServiceInit:
    def test_it_instantiates_service_with_minimal_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        workout_data = {
            "distance": 18.0,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        assert service.auth_user == user_1
        assert service.workout_data == WorkoutData(**workout_data)  # type: ignore

    def test_it_instantiates_service_with_all_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workout_data = {
            "distance": 18,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "ascent": 10,
            "descent": 35,
            "description": "just a description",
            "equipment_ids": [equipment_bike_user_1.short_id],
            "notes": "some notes",
            "title": "workout title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }
        service = WorkoutCreationService(user_1, workout_data)

        assert service.auth_user == user_1
        assert service.workout_data == WorkoutData(**workout_data)  # type: ignore


class TestWorkoutCreationServiceGetWorkoutDate(RandomMixin):
    def test_it_raises_error_when_workout_date_format_is_invalid(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        workout_data = {
            "distance": 18,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-09",
        }
        service = WorkoutCreationService(user_1, workout_data)

        with pytest.raises(
            WorkoutException, match="invalid format for workout date"
        ):
            service.get_workout_date()

    def test_it_returns_workout_date_when_timezone_is_set_for_user(
        self, app: "Flask", sport_1_cycling: "Sport", user_1_paris: "User"
    ) -> None:
        workout_data = {
            "distance": 18,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1_paris, workout_data)

        workout_date = service.get_workout_date()

        assert workout_date == datetime(2025, 2, 8, 8, tzinfo=timezone.utc)

    def test_it_returns_workout_date_when_no_timezone_set_for_user(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        workout_data = {
            "distance": 18,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        workout_date = service.get_workout_date()

        assert workout_date == datetime(2025, 2, 8, 9, tzinfo=timezone.utc)


@pytest.mark.disable_autouse_update_records_patch
class TestWorkoutCreationServiceProcess(RandomMixin):
    def test_it_creates_workout_with_minimal_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        # workout
        workout = Workout.query.one()
        assert workout.analysis_visibility == VisibilityLevel.PRIVATE
        assert workout.ascent is None
        assert float(workout.ave_speed) == 18.0
        assert workout.bounds is None
        assert workout.creation_date is not None
        assert workout.descent is None
        assert workout.description is None
        assert float(workout.distance) == 15.0
        assert workout.duration == timedelta(minutes=50)
        assert workout.gpx is None
        assert workout.map is None
        assert workout.map_id is None
        assert workout.map_visibility == VisibilityLevel.PRIVATE
        assert workout.max_alt is None
        assert workout.max_speed == 18.0
        assert workout.min_alt is None
        assert workout.modification_date is None
        assert workout.moving == timedelta(minutes=50)
        assert workout.notes is None
        assert workout.pauses == timedelta(seconds=0)
        assert workout.sport_id == sport_1_cycling.id
        assert workout.suspended_at is None
        assert workout.title == "Cycling (Sport) - 2025-02-08 09:00:00"
        assert workout.user_id == user_1.id
        assert workout.weather_start is None
        assert workout.weather_end is None
        assert workout.workout_date == datetime(
            2025, 2, 8, 9, tzinfo=timezone.utc
        )
        assert workout.workout_visibility == VisibilityLevel.PRIVATE
        # segment
        assert WorkoutSegment.query.count() == 0
        # records
        records = Record.query.order_by(Record.record_type.asc()).all()
        assert len(records) == 4
        assert records[0].serialize() == {
            "id": 1,
            "record_type": "AS",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": workout.ave_speed,
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[1].serialize() == {
            "id": 2,
            "record_type": "FD",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": workout.distance,
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[2].serialize() == {
            "id": 3,
            "record_type": "LD",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": str(workout.duration),
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }
        assert records[3].serialize() == {
            "id": 4,
            "record_type": "MS",
            "sport_id": workout.sport_id,
            "user": workout.user.username,
            "value": workout.max_speed,
            "workout_date": workout.workout_date,
            "workout_id": workout.short_id,
        }

    def test_it_returns_new_workout(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        service = WorkoutCreationService(
            user_1,
            {
                "distance": 15,
                "duration": 3000,
                "sport_id": sport_1_cycling.id,
                "workout_date": "2025-02-08 09:00",
            },
        )

        [new_workout], _ = service.process()
        db.session.commit()

        assert new_workout == Workout.query.one()

    def test_it_creates_workout_with_low_value_for_distance(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        distance = 0.001
        service = WorkoutCreationService(
            user_1,
            {
                "distance": distance,
                "duration": 3000,
                "sport_id": sport_1_cycling.id,
                "workout_date": "2025-02-08 09:00",
            },
        )

        service.process()
        db.session.commit()

        new_workout = Workout.query.one()
        assert float(new_workout.distance) == distance

    @pytest.mark.parametrize(
        "input_description, input_elevation_data",
        [
            ("missing descent", {"ascent": 50}),
            ("missing ascent", {"descent": 50}),
            ("invalid ascent", {"ascent": "invalid", "descent": 50}),
            ("invalid descent", {"ascent": 50, "descent": "invalid"}),
        ],
    )
    def test_it_raises_error_when_elevation_data_are_invalid(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        input_description: str,
        input_elevation_data: Dict,
    ) -> None:
        workout_data = {
            "distance": 18,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-09 08:00",
            **input_elevation_data,
        }
        service = WorkoutCreationService(user_1, workout_data)

        with pytest.raises(
            WorkoutException, match="invalid ascent or descent"
        ):
            service.process()

    @pytest.mark.parametrize("input_key", ["distance", "ascent", "descent"])
    def test_it_raises_error_when_workout_value_exceeds_limit(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        input_key: str,
    ) -> None:
        workout_data = {
            "ascent": 120,
            "descent": 80,
            "distance": 18,
            "duration": 3600,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-09 08:00",
            **{input_key: WORKOUT_VALUES_LIMIT[input_key] + 0.001},
        }
        service = WorkoutCreationService(user_1, workout_data)

        with pytest.raises(
            WorkoutExceedingValueException,
            match=(
                "one or more values, entered or calculated, exceed the limits"
            ),
        ):
            service.process()

    def test_it_raises_error_when_duration_exceeds_limit(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        workout_data = {
            "ascent": 120,
            "descent": 80,
            "distance": 18,
            "duration": PSQL_INTEGER_LIMIT + 1,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-09 08:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        with pytest.raises(
            WorkoutExceedingValueException,
            match=(
                "one or more values, entered or calculated, exceed the limits"
            ),
        ):
            service.process()

    def test_it_raises_error_when_speed_exceeds_limit(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
    ) -> None:
        workout_data = {
            "sport_id": sport_1_cycling.id,
            "duration": 36,
            "workout_date": "2023-07-26 12:00",
            "distance": 100,
            "ascent": 120,
            "descent": 80,
        }
        service = WorkoutCreationService(user_1, workout_data)

        with pytest.raises(
            WorkoutExceedingValueException,
            match=(
                "one or more values, entered or calculated, exceed the limits"
            ),
        ):
            service.process()

    @pytest.mark.parametrize(
        "input_description, input_elevation_data",
        [
            ("null values", {"ascent": None, "descent": None}),
            ("not null values", {"ascent": 50, "descent": 75}),
        ],
    )
    def test_it_creates_workout_with_given_elevation_data(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        input_description: str,
        input_elevation_data: Dict,
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            **input_elevation_data,
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.ascent == input_elevation_data["ascent"]
        assert workout.descent == input_elevation_data["descent"]

    def test_it_creates_workout_when_title_is_provided(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "title": "my workout",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.title == "my workout"

    def test_it_creates_workout_when_title_length_exceeds_limit(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        title = self.random_string(TITLE_MAX_CHARACTERS + 1)
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "title": title,
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.title == (title[:TITLE_MAX_CHARACTERS])

    def test_it_creates_workout_when_description_is_provided(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "description": "my workout description",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.description == "my workout description"

    def test_it_creates_workout_when_description_length_exceeds_limit(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        description = self.random_string(DESCRIPTION_MAX_CHARACTERS + 1)
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "description": description,
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert (
            workout.description == (description[:DESCRIPTION_MAX_CHARACTERS])
        )

    def test_it_creates_workout_when_notes_are_provided(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "notes": "workouts notes",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.notes == "workouts notes"

    def test_it_creates_workout_when_notes_length_exceeds_limit(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        notes = self.random_string(NOTES_MAX_CHARACTERS + 1)
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "notes": notes,
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.notes == (notes[:NOTES_MAX_CHARACTERS])

    def test_it_creates_workout_with_given_workout_visibility(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.workout_visibility == VisibilityLevel.PUBLIC

    def test_it_creates_workout_with_user_visibility(
        self, app: "Flask", sport_1_cycling: "Sport", user_1: "User"
    ) -> None:
        user_1.workouts_visibility = VisibilityLevel.FOLLOWERS
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.workout_visibility == VisibilityLevel.FOLLOWERS

    def test_it_creates_workout_with_given_equipment(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "equipment_ids": [equipment_bike_user_1.short_id],
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.equipments == [equipment_bike_user_1]

    def test_it_creates_workout_with_default_equipment(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        equipment_bike_user_1: "Equipment",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.equipments == [equipment_bike_user_1]

    def test_it_creates_workout_without_default_equipment_when_empty_list_provided(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        user_1: "User",
        equipment_bike_user_1: "Equipment",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        db.session.commit()
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
            "equipment_ids": [],
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.equipments == []

    def test_it_raises_exception_when_multiple_equipments_are_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_2_running: "Sport",
        gpx_file: str,
        equipment_shoes_user_1: "Equipment",
        equipment_another_shoes_user_1: "Equipment",
    ) -> None:
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_2_running.id,
            "workout_date": "2025-02-08 09:00",
            "equipment_ids": [
                equipment_shoes_user_1.short_id,
                equipment_another_shoes_user_1.short_id,
            ],
        }
        service = WorkoutCreationService(user_1, workout_data)

        with pytest.raises(
            InvalidEquipmentsException, match="only one equipment can be added"
        ):
            service.process()

    def test_it_does_not_add_inactive_default_equipment(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file: str,
        equipment_bike_user_1: "Equipment",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        db.session.execute(
            insert(UserSportPreferenceEquipment).values(
                [
                    {
                        "equipment_id": equipment_bike_user_1.id,
                        "sport_id": user_1_sport_1_preference.sport_id,
                        "user_id": user_1_sport_1_preference.user_id,
                    }
                ]
            )
        )
        equipment_bike_user_1.is_active = False
        db.session.commit()
        workout_data = {
            "distance": 15,
            "duration": 3000,
            "sport_id": sport_1_cycling.id,
            "workout_date": "2025-02-08 09:00",
        }
        service = WorkoutCreationService(user_1, workout_data)

        service.process()
        db.session.commit()

        workout = Workout.query.one()
        assert workout.equipments == []
        assert equipment_bike_user_1.total_workouts == 0
        assert equipment_bike_user_1.total_distance == 0.0
        assert equipment_bike_user_1.total_duration == timedelta()
        assert equipment_bike_user_1.total_moving == timedelta()

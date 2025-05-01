import os
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import TYPE_CHECKING, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.dialects.postgresql import insert
from werkzeug.datastructures import FileStorage

from fittrackee import db
from fittrackee.equipments.exceptions import (
    InvalidEquipmentException,
    InvalidEquipmentsException,
)
from fittrackee.files import get_absolute_file_path
from fittrackee.tests.mixins import RandomMixin
from fittrackee.users.models import UserSportPreferenceEquipment, UserTask
from fittrackee.visibility_levels import VisibilityLevel
from fittrackee.workouts.exceptions import (
    WorkoutException,
    WorkoutFileException,
)
from fittrackee.workouts.models import (
    DESCRIPTION_MAX_CHARACTERS,
    NOTES_MAX_CHARACTERS,
    TITLE_MAX_CHARACTERS,
    Workout,
    WorkoutSegment,
)
from fittrackee.workouts.services import (
    WorkoutGpxCreationService,
    WorkoutsFromFileCreationService,
)
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsData,
)

from ...fixtures.fixtures_workouts import MESSAGE_ID
from ...mixins import UserTaskMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment, EquipmentType
    from fittrackee.users.models import User, UserSportPreference
    from fittrackee.workouts.models import Sport

# files from gpx_test.zip
TEST_FILES_LIST = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]


class TestWorkoutsFromFileCreationServiceInstantiation:
    def test_it_raises_error_when_sport_id_is_not_provided(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
    ) -> None:
        with pytest.raises(WorkoutException, match="no sport id provided"):
            WorkoutsFromFileCreationService(
                auth_user=user_1,
                file=gpx_file_storage,
                workouts_data={},
            )

    def test_it_raises_error_when_sport_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
    ) -> None:
        with pytest.raises(
            WorkoutException, match="Sport id: 1 does not exist"
        ):
            WorkoutsFromFileCreationService(
                auth_user=user_1,
                file=gpx_file_storage,
                workouts_data={"sport_id": 1},
            )

    def test_it_instantiates_service_with_minimal_data(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        assert service.auth_user == user_1
        assert service.file == gpx_file_storage
        assert service.workouts_data == WorkoutsData(
            sport_id=sport_1_cycling.id
        )
        assert service.sport == sport_1_cycling
        assert service.sport_preferences is None
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )

    def test_it_instantiates_service_with_all_data(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workouts_data = {
            "analysis_visibility": VisibilityLevel.PUBLIC,
            "description": "just a description",
            "equipment_ids": [equipment_bike_user_1.short_id],
            "map_visibility": VisibilityLevel.PUBLIC,
            "notes": "some notes",
            "sport_id": sport_1_cycling.id,
            "title": "workout title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }

        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data=workouts_data,
        )

        assert service.auth_user == user_1
        assert service.file == gpx_file_storage
        assert service.workouts_data == WorkoutsData(**workouts_data)  # type: ignore
        assert service.sport == sport_1_cycling
        assert service.sport_preferences is None
        assert (
            service.stopped_speed_threshold
            == sport_1_cycling.stopped_speed_threshold
        )

    def test_it_instantiates_service_when_sport_preference_exists(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
        user_1_sport_1_preference: "UserSportPreference",
    ) -> None:
        user_1_sport_1_preference.stopped_speed_threshold = 12
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        assert service.auth_user == user_1
        assert service.file == gpx_file_storage
        assert service.workouts_data == WorkoutsData(
            sport_id=sport_1_cycling.id
        )
        assert service.sport == sport_1_cycling
        assert service.sport_preferences == user_1_sport_1_preference
        assert service.stopped_speed_threshold == 12


class TestWorkoutsFromFileCreationServiceGetEquipments(RandomMixin):
    def test_equipments_is_none_when_no_equipment_ids_and_no_default_equipments(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        equipments = service.get_equipments()

        assert equipments is None

    def test_it_raises_error_when_equipment_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        equipement_id = self.random_short_id()
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "equipment_ids": [equipement_id],
                "sport_id": sport_1_cycling.id,
            },
        )

        with pytest.raises(
            InvalidEquipmentException,
            match=f"equipment with id {equipement_id} does not exist",
        ):
            service.get_equipments()

    def test_equipments_contains_equipment_when_equipment_ids_in_workouts_data(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "equipment_ids": [equipment_bike_user_1.short_id],
                "sport_id": sport_1_cycling.id,
            },
        )

        equipments = service.get_equipments()

        assert equipments == [equipment_bike_user_1]

    def test_equipments_contains_default_equipments_when_default_equipments_exist(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
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
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        equipments = service.get_equipments()

        assert equipments == [equipment_bike_user_1]


class TestWorkoutsFromFileCreationServiceGetFilePath:
    def test_it_gets_file_path(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        workout_date = datetime.now(tz=timezone.utc).strftime(
            "%Y-%m-%d_%H-%M-%S"
        )
        extension = ".png"
        token = "tJq625gj_kQ"

        with patch("secrets.token_urlsafe", return_value=token):
            file_path = service.get_file_path(workout_date, extension)

        assert file_path == (
            f"workouts/{sport_1_cycling.id}/{workout_date}_"
            f"{sport_1_cycling.id}_{token}{extension}"
        )


class TestWorkoutsFromFileCreationServiceCreateWorkout(RandomMixin):
    def test_it_raises_error_when_no_file_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(WorkoutException, match="no workout file provided"):
            service.create_workout_from_file(extension="gpx", equipments=None)

    def test_it_creates_workout_when_extension_is_gpx_and_with_minimal_data(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file with name
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.user_id == user_1.id
        assert new_workout.sport_id == sport_1_cycling.id
        assert new_workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
        )
        assert new_workout.analysis_visibility == VisibilityLevel.PRIVATE
        assert float(new_workout.ascent) == 0.4  # type: ignore
        assert float(new_workout.ave_speed) == 4.61  # type: ignore
        assert new_workout.bounds == [44.67822, 6.07355, 44.68095, 6.07442]
        assert float(new_workout.descent) == 23.4  # type: ignore
        assert new_workout.description is None
        assert float(new_workout.distance) == 0.32  # type: ignore
        assert new_workout.duration == timedelta(minutes=4, seconds=10)
        assert new_workout.gpx is not None
        assert new_workout.map is not None
        assert new_workout.map_visibility == VisibilityLevel.PRIVATE
        assert new_workout.map_id is not None
        assert float(new_workout.max_alt) == 998.0  # type: ignore
        assert float(new_workout.max_speed) == 5.12  # type: ignore
        assert float(new_workout.min_alt) == 975.0  # type: ignore
        assert new_workout.moving == timedelta(minutes=4, seconds=10)
        assert new_workout.notes is None
        assert new_workout.pauses == timedelta(seconds=0)
        assert new_workout.suspended_at is None
        assert new_workout.title == "just a workout"
        assert new_workout.weather_start is None
        assert new_workout.weather_end is None
        assert new_workout.workout_visibility == VisibilityLevel.PRIVATE
        assert WorkoutSegment.query.count() == 1

    def test_it_creates_workout_when_extension_is_gpx_and_with_all_data(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workouts_data = {
            "analysis_visibility": VisibilityLevel.PUBLIC,
            "description": self.random_string(),
            "equipment_ids": [equipment_bike_user_1.short_id],
            "map_visibility": VisibilityLevel.PUBLIC,
            "notes": self.random_string(),
            "sport_id": sport_1_cycling.id,
            "title": self.random_string(),
            "workout_visibility": VisibilityLevel.PUBLIC,
        }
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data=workouts_data,
        )

        service.create_workout_from_file(
            extension="gpx", equipments=[equipment_bike_user_1]
        )
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
        )
        assert new_workout.analysis_visibility == VisibilityLevel.PUBLIC
        assert new_workout.description == workouts_data["description"]
        assert new_workout.equipments == [equipment_bike_user_1]
        assert new_workout.map_visibility == VisibilityLevel.PUBLIC
        assert new_workout.notes == workouts_data["notes"]
        assert new_workout.sport_id == sport_1_cycling.id
        assert new_workout.workout_visibility == VisibilityLevel.PUBLIC

    @pytest.mark.parametrize(
        "input_map_visibility,input_analysis_visibility,"
        "input_workout_visibility,expected_map_visibility,"
        "expected_analysis_visibility",
        [
            (
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PUBLIC,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.FOLLOWERS,
            ),
            (
                VisibilityLevel.PUBLIC,
                VisibilityLevel.FOLLOWERS,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
                VisibilityLevel.PRIVATE,
            ),
        ],
    )
    def test_workout_is_created_with_valid_privacy_parameters_when_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        gpx_file_storage: "FileStorage",  # gpx file
        input_analysis_visibility: "VisibilityLevel",
        input_map_visibility: "VisibilityLevel",
        input_workout_visibility: "VisibilityLevel",
        expected_analysis_visibility: "VisibilityLevel",
        expected_map_visibility: "VisibilityLevel",
    ) -> None:
        """
        when workout visibility is stricter, map visibility is initialised
        with workout visibility value
        """
        workouts_data = {
            "analysis_visibility": input_analysis_visibility,
            "map_visibility": input_map_visibility,
            "sport_id": sport_1_cycling.id,
            "workout_visibility": input_workout_visibility,
        }
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data=workouts_data,
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.analysis_visibility == expected_analysis_visibility
        assert new_workout.map_visibility == expected_map_visibility
        assert new_workout.workout_visibility == input_workout_visibility

    def test_it_creates_workout_with_user_visibility(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file with name
        sport_1_cycling: "Sport",
    ) -> None:
        user_1.analysis_visibility = VisibilityLevel.FOLLOWERS
        user_1.map_visibility = VisibilityLevel.FOLLOWERS
        user_1.workouts_visibility = VisibilityLevel.PUBLIC
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.analysis_visibility == user_1.analysis_visibility
        assert new_workout.map_visibility == user_1.map_visibility
        assert new_workout.workout_visibility == user_1.workouts_visibility

    def test_it_creates_gpx_file_in_user_directory(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        gpx_file_storage: "FileStorage",  # gpx file, date: 2018-03-13 12:44:45
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        expected_token = self.random_string()

        with patch("secrets.token_urlsafe", return_value=expected_token):
            service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.gpx == (
            f"workouts/{user_1.id}/2018-03-13_12-44-45_"
            f"{sport_1_cycling.id}_{expected_token}.gpx"
        )
        with open(get_absolute_file_path(new_workout.gpx)) as f:
            assert f.read() == gpx_file

    def test_it_creates_map_image_in_user_directory(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file, date: 2018-03-13 12:44:45
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        expected_token = self.random_string()

        with patch("secrets.token_urlsafe", return_value=expected_token):
            service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.map == (
            f"workouts/{user_1.id}/2018-03-13_12-44-45_"
            f"{sport_1_cycling.id}_{expected_token}.png"
        )
        assert os.path.exists(get_absolute_file_path(new_workout.map))

    def test_it_generates_title_when_no_title_in_workout_data_and_file(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_wo_name: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file_wo_name))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.title == "Cycling (Sport) - 2018-03-13 12:44:45"

    def test_it_generates_title_with_user_timezone(
        self,
        app: "Flask",
        user_1_paris: "User",
        gpx_file_wo_name: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file_wo_name))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1_paris,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.title == "Cycling (Sport) - 2018-03-13 13:44:45"

    @pytest.mark.parametrize(
        "input_test_description,input_description,expected_description",
        [
            ("empty description", "", None),
            ("short description", "test workout", "test workout"),
            (
                "description with special characters",
                "test \n'workout'©",
                "test \n'workout'©",
            ),
        ],
    )
    def test_it_creates_workout_with_provided_description(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
        input_test_description: str,
        input_description: str,
        expected_description: str,
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "sport_id": sport_1_cycling.id,
                "description": input_description,
            },
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.description == expected_description

    def test_it_creates_workout_with_description_from_gpx_file(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_with_description: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx",
            stream=BytesIO(str.encode(gpx_file_with_description)),
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.description == "this is workout description"

    def test_it_overrides_gpx_description_when_description_is_provided(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_with_description: str,
        sport_1_cycling: "Sport",
    ) -> None:
        description = "this is workout description"
        gpx_file_storage = FileStorage(
            filename="file.gpx",
            stream=BytesIO(str.encode(gpx_file_with_description)),
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "sport_id": sport_1_cycling.id,
                "description": description,
            },
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.description == description

    def test_it_creates_workout_when_title_exceeds_limit(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file
        sport_1_cycling: "Sport",
    ) -> None:
        title = self.random_string(length=TITLE_MAX_CHARACTERS + 1)
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id, "title": title},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.title == title[:TITLE_MAX_CHARACTERS]

    def test_it_creates_workout_when_description_exceeds_limits(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file
        sport_1_cycling: "Sport",
    ) -> None:
        description = self.random_string(length=DESCRIPTION_MAX_CHARACTERS + 1)
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "sport_id": sport_1_cycling.id,
                "description": description,
            },
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert (
            new_workout.description == description[:DESCRIPTION_MAX_CHARACTERS]
        )

    def test_it_creates_workout_when_notes_exceed_limits(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file
        sport_1_cycling: "Sport",
    ) -> None:
        notes = self.random_string(length=NOTES_MAX_CHARACTERS + 1)
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id, "notes": notes},
        )

        service.create_workout_from_file(extension="gpx", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.notes == notes[:NOTES_MAX_CHARACTERS]

    def test_it_returns_new_workout(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file_storage: "FileStorage",  # gpx file with name
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        new_workout = service.create_workout_from_file(
            extension="gpx", equipments=None
        )
        db.session.commit()

        assert new_workout == Workout.query.one()

    def test_it_returns_new_workout_from_workout_file_content(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        gpx_file_storage: "FileStorage",  # gpx file with name
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        expected_token = self.random_string()

        with patch("secrets.token_urlsafe", return_value=expected_token):
            new_workout = service.create_workout_from_file(
                extension="gpx",
                equipments=None,
                workout_file=gpx_file_storage.stream,
            )
        db.session.commit()

        assert new_workout == Workout.query.one()
        assert new_workout.gpx == (
            f"workouts/{user_1.id}/2018-03-13_12-44-45_"
            f"{sport_1_cycling.id}_{expected_token}.gpx"
        )
        with open(get_absolute_file_path(new_workout.gpx)) as f:
            assert f.read() == gpx_file

    def test_it_creates_workout_when_extension_is_kml(
        self,
        app: "Flask",
        user_1: "User",
        kml_2_3_with_one_track: str,
        sport_1_cycling: "Sport",
    ) -> None:
        kml_file_storage = FileStorage(
            filename="file.kml",
            stream=BytesIO(str.encode(kml_2_3_with_one_track)),
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=kml_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="kml", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.user_id == user_1.id
        assert new_workout.sport_id == sport_1_cycling.id
        assert new_workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
        )
        assert new_workout.analysis_visibility == VisibilityLevel.PRIVATE
        assert float(new_workout.ascent) == 0.4  # type: ignore
        assert float(new_workout.ave_speed) == 4.61  # type: ignore
        assert new_workout.bounds == [44.67822, 6.07355, 44.68095, 6.07442]
        assert float(new_workout.descent) == 23.4  # type: ignore
        assert new_workout.description == "some description"
        assert float(new_workout.distance) == 0.32  # type: ignore
        assert new_workout.duration == timedelta(minutes=4, seconds=10)
        assert new_workout.gpx is not None
        assert new_workout.map is not None
        assert new_workout.map_visibility == VisibilityLevel.PRIVATE
        assert new_workout.map_id is not None
        assert float(new_workout.max_alt) == 998.0  # type: ignore
        assert float(new_workout.max_speed) == 5.25  # type: ignore
        assert float(new_workout.min_alt) == 975.0  # type: ignore
        assert new_workout.moving == timedelta(minutes=4, seconds=10)
        assert new_workout.notes is None
        assert new_workout.pauses == timedelta(seconds=0)
        assert new_workout.suspended_at is None
        assert new_workout.title == "just a workout"
        assert new_workout.weather_start is None
        assert new_workout.weather_end is None
        assert new_workout.workout_visibility == VisibilityLevel.PRIVATE
        assert WorkoutSegment.query.count() == 1

    def test_it_creates_workout_when_extension_is_kmz(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        file_path = os.path.join(app.root_path, "tests/files/example.kmz")
        with open(file_path, "rb") as kmz_file:
            kmz_file_storage = FileStorage(
                filename="example.kmz", stream=BytesIO(kmz_file.read())
            )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=kmz_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.create_workout_from_file(extension="kmz", equipments=None)
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.user_id == user_1.id
        assert new_workout.sport_id == sport_1_cycling.id
        assert new_workout.workout_date == datetime(
            2018, 3, 13, 12, 44, 45, tzinfo=timezone.utc
        )
        assert new_workout.analysis_visibility == VisibilityLevel.PRIVATE
        assert float(new_workout.ascent) == 0.4  # type: ignore
        assert float(new_workout.ave_speed) == 4.59  # type: ignore
        assert new_workout.bounds == [44.67822, 6.07355, 44.68095, 6.07442]
        assert float(new_workout.descent) == 23.4  # type: ignore
        assert new_workout.description == "some description"
        assert float(new_workout.distance) == 0.299  # type: ignore
        assert new_workout.duration == timedelta(minutes=4, seconds=10)
        assert new_workout.gpx is not None
        assert new_workout.map is not None
        assert new_workout.map_visibility == VisibilityLevel.PRIVATE
        assert new_workout.map_id is not None
        assert float(new_workout.max_alt) == 998.0  # type: ignore
        assert float(new_workout.max_speed) == 5.41  # type: ignore
        assert float(new_workout.min_alt) == 975.0  # type: ignore
        assert new_workout.moving == timedelta(minutes=3, seconds=55)
        assert new_workout.notes is None
        assert new_workout.pauses == timedelta(seconds=15)
        assert new_workout.suspended_at is None
        assert new_workout.title == "just a workout"
        assert new_workout.weather_start is None
        assert new_workout.weather_end is None
        assert new_workout.workout_visibility == VisibilityLevel.PRIVATE
        assert WorkoutSegment.query.count() == 2


class WorkoutsFromFileCreationServiceTestCase:
    @staticmethod
    def get_service(
        app: "Flask",
        user: "User",
        sport: "Sport",
        file_path: str,
        workout_data: Optional[Dict] = None,
    ) -> WorkoutsFromFileCreationService:
        if not workout_data:
            workout_data = {}
        file_path = os.path.join(app.root_path, file_path)
        with open(file_path, "rb") as zip_file:
            archive_file_storage = FileStorage(
                filename="workouts.zip", stream=BytesIO(zip_file.read())
            )
            return WorkoutsFromFileCreationService(
                auth_user=user,
                file=archive_file_storage,
                workouts_data={"sport_id": sport.id, **workout_data},
            )

    @staticmethod
    def get_undeleted_files(app: "Flask", user: "User") -> List[str]:
        upload_directory = os.path.join(
            app.config["UPLOAD_FOLDER"], f"workouts/{user.id}"
        )
        return [
            name
            for name in os.listdir(upload_directory)
            if os.path.isfile(os.path.join(upload_directory, name))
        ]


class TestWorkoutsFromFileCreationServiceGetFilesFromArchive(
    WorkoutsFromFileCreationServiceTestCase
):
    def test_it_raises_error_when_no_file_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(WorkoutException, match="no workout file provided"):
            service.get_files_from_archive()

    def test_it_raises_error_when_archive_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        # archive_file_storage is not an archive but a gpx file
        archive_file_storage = FileStorage(filename="workouts.zip")
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=archive_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(WorkoutFileException, match="invalid zip file"):
            service.get_files_from_archive()

    def test_it_raises_error_when_no_workout_files_in_archive(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        # the archive contains only a doc file
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test_no_gpx.zip"
        )

        with pytest.raises(
            WorkoutFileException,
            match="archive does not contain valid workout files",
        ):
            service.get_files_from_archive()

    def test_it_raises_error_when_files_number_exceeds_limit(
        self,
        app_with_max_workouts: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app_with_max_workouts,
            user_1,
            sport_1_cycling,
            "tests/files/gpx_test.zip",
        )

        with pytest.raises(
            WorkoutFileException,
            match="the number of files in the archive exceeds the limit",
        ):
            service.get_files_from_archive()

    def test_it_raises_error_when_a_file_exceeds_size_limit(
        self,
        app_with_max_file_size: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app_with_max_file_size,
            user_1,
            sport_1_cycling,
            "tests/files/gpx_test.zip",
        )

        with pytest.raises(
            WorkoutFileException,
            match=(
                "at least one file in zip archive exceeds size limit, "
                "please check the archive"
            ),
        ):
            service.get_files_from_archive()

    def test_it_returns_files_list(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        files_to_process = service.get_files_from_archive()

        assert files_to_process == TEST_FILES_LIST

    def test_it_returns_files_list_when_archive_contains_folder(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test_folder.zip"
        )

        files_to_process = service.get_files_from_archive()

        assert files_to_process == [
            "folder/test_1.gpx",
            "folder/test_2.gpx",
            "folder/test_3.gpx",
        ]


class TestWorkoutsFromFileCreationServiceProcessArchiveContent(
    WorkoutsFromFileCreationServiceTestCase
):
    def test_it_raises_error_when_files_to_process_is_empty_list(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        file_path = os.path.join(
            app.root_path, "tests/files/gpx_test_no_gpx.zip"
        )
        with open(file_path, "rb") as zip_file:
            archive_file_storage = FileStorage(
                filename="workouts.zip", stream=BytesIO(zip_file.read())
            )

        with pytest.raises(
            WorkoutFileException, match="No files from archive to process"
        ):
            service.process_archive_content(
                archive_content=archive_file_storage.stream,
                files_to_process=[],
                equipments=None,
            )

    def test_it_returns_error_when_file_does_not_exist_in_archive(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        file_path = os.path.join(
            app.root_path, "tests/files/gpx_test_no_gpx.zip"
        )
        with open(file_path, "rb") as zip_file:
            archive_file_storage = FileStorage(
                filename="workouts.zip", stream=BytesIO(zip_file.read())
            )

        new_workouts, processing_output = service.process_archive_content(
            archive_content=archive_file_storage.stream,
            files_to_process=["invalid.txt"],
            equipments=None,
        )

        assert new_workouts == []
        assert processing_output == {
            "invalid.txt": (
                "There is no item named 'invalid.txt' in the archive"
            )
        }

    def test_it_creates_workouts(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        with open(file_path, "rb") as zip_file:
            archive_file_storage = FileStorage(
                filename="workouts.zip", stream=BytesIO(zip_file.read())
            )

        service.process_archive_content(
            archive_content=archive_file_storage.stream,
            files_to_process=["test_1.gpx", "test_2.gpx"],
            equipments=None,
        )
        db.session.commit()

        workouts = Workout.query.all()
        assert len(workouts) == 2
        assert workouts[0].sport_id == sport_1_cycling.id
        assert workouts[1].sport_id == sport_1_cycling.id
        assert WorkoutSegment.query.count() == 2

    def test_it_creates_workouts_with_equipments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_type_1_shoe: "EquipmentType",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        equipments = [equipment_shoes_user_1]
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        file_path = os.path.join(app.root_path, "tests/files/gpx_test.zip")
        with open(file_path, "rb") as zip_file:
            archive_file_storage = FileStorage(
                filename="workouts.zip", stream=BytesIO(zip_file.read())
            )

        service.process_archive_content(
            archive_content=archive_file_storage.stream,
            files_to_process=["test_1.gpx", "test_2.gpx"],
            equipments=equipments,
        )
        db.session.commit()

        workouts = Workout.query.all()
        assert len(workouts) == 2
        for n in range(2):
            assert workouts[n].sport_id == sport_1_cycling.id
            assert workouts[n].equipments == equipments


class TestWorkoutsFromFileCreationServiceAddWorkoutsUploadTask(
    UserTaskMixin, WorkoutsFromFileCreationServiceTestCase
):
    def test_it_raises_error_when_no_file_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(WorkoutException, match="no workout file provided"):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=None,
            )

    def test_it_raises_error_when_files_to_process_is_empty_list(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        with pytest.raises(
            WorkoutFileException, match="No files from archive to process"
        ):
            service.add_workouts_upload_task(
                files_to_process=[],
                equipments=None,
            )

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [
            ("queued", {"progress": 0}),
            ("in_progress", {"progress": 10}),
        ],
    )
    def test_it_raises_error_when_ongoing_task_exists(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        input_status: str,
        input_task_data: Dict,
    ) -> None:
        self.create_workouts_upload_task(user_1, **input_task_data)
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        with (
            patch.object(tempfile, "mkstemp", return_value=(None, None)),
            pytest.raises(
                WorkoutException, match="ongoing upload task exists"
            ),
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=None,
            )

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [
            ("aborted", {"aborted": True}),
            ("errored", {"errored": True, "progress": 10}),
            ("successful", {"progress": 100}),
        ],
    )
    def test_it_does_not_raises_error_when_existing_task_is_errored(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        input_status: str,
        input_task_data: Dict,
        upload_workouts_archive_mock: MagicMock,
    ) -> None:
        self.create_workouts_upload_task(user_1, **input_task_data)
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")

        with patch.object(
            tempfile, "mkstemp", return_value=(fd, temp_file_path)
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=None,
            )

        assert UserTask.query.filter_by(user_id=user_1.id).count() == 2

    def test_it_creates_task_with_minimal_data(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        upload_workouts_archive_mock: MagicMock,
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        archive_size = 2000

        with (
            patch(
                (
                    "fittrackee.workouts.services."
                    "workouts_from_file_creation_service.os.path.getsize"
                ),
                return_value=archive_size,
            ),
            patch.object(
                tempfile, "mkstemp", return_value=(fd, temp_file_path)
            ),
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=None,
            )

        upload_task = UserTask.query.filter_by(user_id=user_1.id).one()
        assert upload_task.data == {
            "new_workouts_count": 0,
            "workouts_data": {
                "sport_id": sport_1_cycling.id,
                "analysis_visibility": None,
                "description": None,
                "equipment_ids": None,
                "map_visibility": None,
                "notes": None,
                "title": None,
                "workout_visibility": None,
            },
            "files_to_process": TEST_FILES_LIST,
            "equipment_ids": None,
            "original_file_name": "workouts.zip",
        }
        assert upload_task.errored is False
        assert upload_task.errors == {
            "archive": None,
            "files": {},
        }
        assert upload_task.file_path == temp_file_path
        assert upload_task.file_size == archive_size
        assert upload_task.message_id == MESSAGE_ID
        assert upload_task.progress == 0
        assert upload_task.task_type == "workouts_archive_upload"
        assert upload_task.user_id == user_1.id

        # file cleanup
        os.close(fd)
        os.remove(temp_file_path)

    def test_it_creates_task_with_all_data(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_type_1_shoe: "EquipmentType",
        equipment_bike_user_1: "Equipment",
        upload_workouts_archive_mock: MagicMock,
    ) -> None:
        workouts_data = {
            "analysis_visibility": VisibilityLevel.FOLLOWERS,
            "description": "some description",
            "equipment_ids": [equipment_bike_user_1.short_id],
            "map_visibility": VisibilityLevel.PRIVATE,
            "notes": "some notes",
            "title": "some title",
            "workout_visibility": VisibilityLevel.PUBLIC,
        }
        service = self.get_service(
            app,
            user_1,
            sport_1_cycling,
            "tests/files/gpx_test.zip",
            workouts_data,
        )
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        archive_size = 2000

        with (
            patch(
                (
                    "fittrackee.workouts.services."
                    "workouts_from_file_creation_service.os.path.getsize"
                ),
                return_value=archive_size,
            ),
            patch.object(
                tempfile, "mkstemp", return_value=(fd, temp_file_path)
            ),
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=[equipment_bike_user_1],
            )

        upload_task = UserTask.query.filter_by(user_id=user_1.id).one()
        assert upload_task.data == {
            "new_workouts_count": 0,
            "workouts_data": {
                "sport_id": sport_1_cycling.id,
                **workouts_data,
            },
            "files_to_process": TEST_FILES_LIST,
            "equipment_ids": [equipment_bike_user_1.short_id],
            "original_file_name": "workouts.zip",
        }
        assert upload_task.errored is False
        assert upload_task.errors == {
            "archive": None,
            "files": {},
        }
        assert upload_task.file_path == temp_file_path
        assert upload_task.file_size == archive_size
        assert upload_task.message_id == MESSAGE_ID
        assert upload_task.progress == 0
        assert upload_task.task_type == "workouts_archive_upload"
        assert upload_task.user_id == user_1.id

        # file cleanup
        os.close(fd)
        os.remove(temp_file_path)

    def test_it_creates_task_when_completed_tasks_for_user_exist(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
        sport_1_cycling: "Sport",
        upload_workouts_archive_mock: MagicMock,
    ) -> None:
        self.create_workouts_upload_task(user_1, progress=100)
        self.create_workouts_upload_task(user_1, progress=100, errored=True)

        self.create_workouts_upload_task(user_2, progress=20)
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")

        with patch.object(
            tempfile, "mkstemp", return_value=(fd, temp_file_path)
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=None,
            )

        assert UserTask.query.filter_by(user_id=user_1.id).count() == 3

        # file cleanup
        os.close(fd)
        os.remove(temp_file_path)

    def test_it_calls_upload_workouts_archive_with_equipments(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        upload_workouts_archive_mock: MagicMock,
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")

        with (
            patch.object(
                tempfile, "mkstemp", return_value=(fd, temp_file_path)
            ),
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=None,
            )

        upload_task = UserTask.query.filter_by(user_id=user_1.id).one()
        upload_workouts_archive_mock.send.assert_called_once_with(
            task_id=upload_task.id
        )

        # file cleanup
        os.close(fd)
        os.remove(temp_file_path)

    def test_it_store_archive_content_in_temporary_file(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_type_1_shoe: "EquipmentType",
        equipment_shoes_user_1: "Equipment",
        upload_workouts_archive_mock: MagicMock,
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")

        with (
            patch.object(
                tempfile, "mkstemp", return_value=(fd, temp_file_path)
            ),
        ):
            service.add_workouts_upload_task(
                files_to_process=TEST_FILES_LIST,
                equipments=[equipment_shoes_user_1],
            )

        with zipfile.ZipFile(temp_file_path, "r") as zip_ref:
            assert {file.filename for file in zip_ref.infolist()} == {
                *TEST_FILES_LIST,
                "fichier.doc",
            }

        # file cleanup
        os.close(fd)
        os.remove(temp_file_path)


class TestWorkoutsFromFileCreationServiceProcessZipArchive(
    WorkoutsFromFileCreationServiceTestCase
):
    def test_it_raises_error_when_no_file_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(WorkoutException, match="no workout file provided"):
            service.process_zip_archive(equipments=None)

    def test_it_creates_one_workout_and_returns_errored_workout_when_archive_contains_invalid_file(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        # the archive contains 2 gpx files including invalid one
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test_incorrect.zip"
        )

        new_workouts, processing_output = service.process_zip_archive(
            equipments=None
        )

        assert len(new_workouts) == 1
        assert processing_output == {
            "task_short_id": None,
            "errored_workouts": {"test_4.gpx": "no tracks in gpx file"},
        }

    def test_it_calls_process_archive_content(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_type_1_shoe: "EquipmentType",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        with (
            patch.object(
                WorkoutsFromFileCreationService,
                "process_archive_content",
                return_value=([], {}),
            ) as process_archive_content_mock,
            patch.object(
                WorkoutsFromFileCreationService, "add_workouts_upload_task"
            ) as add_workouts_upload_task_mock,
        ):
            service.process_zip_archive(equipments=[equipment_shoes_user_1])

        process_archive_content_mock.assert_called_once_with(
            archive_content=service._get_archive_content(),
            files_to_process=TEST_FILES_LIST,
            equipments=[equipment_shoes_user_1],
        )
        add_workouts_upload_task_mock.assert_not_called()

    def test_it_calls_process_archive_content_when_file_are_in_folder(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test_folder.zip"
        )

        with patch.object(
            WorkoutsFromFileCreationService,
            "process_archive_content",
            return_value=([], {}),
        ) as process_archive_content_mock:
            service.process_zip_archive(equipments=None)

        process_archive_content_mock.assert_called_once_with(
            archive_content=service._get_archive_content(),
            files_to_process=[
                "folder/test_1.gpx",
                "folder/test_2.gpx",
                "folder/test_3.gpx",
            ],
            equipments=None,
        )

    def test_it_calls_add_workouts_upload_task_when_files_exceeds_limit(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_type_1_shoe: "EquipmentType",
        equipment_shoes_user_1: "Equipment",
    ) -> None:
        app.config.update(
            {"file_limit_import": 10, "file_sync_limit_import": 2}
        )
        equipments = [equipment_shoes_user_1]
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        with (
            patch.object(
                WorkoutsFromFileCreationService, "process_archive_content"
            ) as process_archive_content_mock,
            patch.object(
                WorkoutsFromFileCreationService, "add_workouts_upload_task"
            ) as add_workouts_upload_task_mock,
        ):
            service.process_zip_archive(equipments=equipments)

        add_workouts_upload_task_mock.assert_called_once_with(
            TEST_FILES_LIST, equipments
        )
        process_archive_content_mock.assert_not_called()


class TestWorkoutsFromFileCreationServiceProcessForOneFile(
    WorkoutsFromFileCreationServiceTestCase
):
    def test_it_raises_when_no_file_is_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(WorkoutException, match="no workout file provided"):
            service.process()

    def test_it_raises_error_when_file_has_no_filename(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename=None, stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(
            WorkoutFileException, match="workout file has no filename"
        ):
            service.process()

    def test_it_raises_error_when_file_extension_is_not_supported(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.tar", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with pytest.raises(
            WorkoutFileException, match="workout file invalid extension"
        ):
            service.process()

    def test_it_creates_workout_when_file_has_gpx_extension(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.process()
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.sport_id == sport_1_cycling.id
        assert new_workout.map is not None
        assert WorkoutSegment.query.count() == 1

    def test_it_creates_workout_from_gpx_file_with_default_equipment(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
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
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        service.process()
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.equipments == [equipment_bike_user_1]
        assert equipment_bike_user_1.total_workouts == 1
        assert equipment_bike_user_1.total_distance == new_workout.distance
        assert equipment_bike_user_1.total_duration == new_workout.duration
        assert equipment_bike_user_1.total_moving == new_workout.moving

    def test_it_creates_workout_without_default_equipment_when_empty_list_provided(  # noqa
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
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
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "sport_id": sport_1_cycling.id,
                "equipment_ids": [],
            },
        )

        service.process()
        db.session.commit()

        new_workout = Workout.query.one()
        assert new_workout.equipments == []

    def test_it_raises_exception_when_multiple_equipments_are_provided(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_2_running: "Sport",
        equipment_shoes_user_1: "Equipment",
        equipment_another_shoes_user_1: "Equipment",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={
                "sport_id": sport_2_running.id,
                "equipment_ids": [
                    equipment_shoes_user_1.short_id,
                    equipment_another_shoes_user_1.short_id,
                ],
            },
        )

        with pytest.raises(
            InvalidEquipmentsException, match="only one equipment can be added"
        ):
            service.process()

    def test_it_deletes_workout_files_on_error(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with (
            patch.object(
                WorkoutGpxCreationService,
                "get_map_hash",
                side_effect=[Exception("error")],
            ),
            pytest.raises(
                WorkoutException, match="error when generating map image"
            ),
        ):
            service.process()
            db.session.commit()

        undeleted_files = self.get_undeleted_files(app, user_1)
        assert len(undeleted_files) == 0

    def test_it_deletes_map_files_on_error_with_workout_files(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with (
            patch.object(
                WorkoutGpxCreationService,
                "get_map_hash",
                side_effect=[Exception("error")],
            ),
            pytest.raises(
                WorkoutException, match="error when generating map image"
            ),
        ):
            service.process()
            db.session.commit()

        undeleted_files = self.get_undeleted_files(app, user_1)
        assert len(undeleted_files) == 0

    def test_it_does_not_delete_previous_workout(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        gpx_file_with_description: str,
        sport_1_cycling: "Sport",
    ) -> None:
        # successful creation
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=FileStorage(
                filename="file.gpx",
                stream=BytesIO(str.encode(gpx_file_with_description)),
            ),
            workouts_data={"sport_id": sport_1_cycling.id},
        )
        service.process()
        db.session.commit()
        # second creation (with error)
        gpx_file_storage = FileStorage(
            filename="file.gpx", stream=BytesIO(str.encode(gpx_file))
        )
        service = WorkoutsFromFileCreationService(
            auth_user=user_1,
            file=gpx_file_storage,
            workouts_data={"sport_id": sport_1_cycling.id},
        )

        with (
            patch.object(
                WorkoutGpxCreationService,
                "get_map_hash",
                side_effect=[Exception("error")],
            ),
            pytest.raises(
                WorkoutException, match="error when generating map image"
            ),
        ):
            service.process()
            db.session.commit()

        undeleted_files = self.get_undeleted_files(app, user_1)
        assert len(undeleted_files) == 2  # gpx and map files


class TestWorkoutsFromFileCreationServiceProcessForSyncArchiveUpload(
    WorkoutsFromFileCreationServiceTestCase
):
    def test_it_returns_created_workouts_and_processing_data(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        new_workouts, processing_output = service.process()

        assert len(new_workouts) == 3
        assert processing_output == {
            "errored_workouts": {},
            "task_short_id": None,
        }

    def test_it_creates_workouts(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        service.process()

        assert Workout.query.count() == 3
        assert WorkoutSegment.query.count() == 3

    def test_it_creates_workouts_from_archive_with_default_equipment(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
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
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        service.process()

        workouts = Workout.query.all()
        total_distance = 0
        total_duration = timedelta()
        total_moving = timedelta()
        for workout in workouts:
            assert workout.equipments == [equipment_bike_user_1]
            total_distance += workout.distance
            total_duration += workout.duration
            total_moving += workout.moving
        assert equipment_bike_user_1.total_workouts == 3
        assert equipment_bike_user_1.total_distance == total_distance
        assert equipment_bike_user_1.total_duration == total_duration
        assert equipment_bike_user_1.total_moving == total_moving

    @pytest.mark.parametrize(
        "input_desc,input_visibility",
        [
            ("private", VisibilityLevel.PRIVATE),
            ("followers_only", VisibilityLevel.FOLLOWERS),
            ("public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_creates_workouts_with_user_visibilities_when_no_provided(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
        input_desc: str,
        input_visibility: "VisibilityLevel",
    ) -> None:
        user_1.map_visibility = input_visibility
        user_1.analysis_visibility = input_visibility
        user_1.workouts_visibility = input_visibility
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        service.process()

        for workout in Workout.query.all():
            assert workout.analysis_visibility == input_visibility
            assert workout.map_visibility == input_visibility
            assert workout.workout_visibility == input_visibility

    @pytest.mark.parametrize(
        "input_desc,input_visibility",
        [
            ("private", VisibilityLevel.PRIVATE),
            ("followers_only", VisibilityLevel.FOLLOWERS),
            ("public", VisibilityLevel.PUBLIC),
        ],
    )
    def test_it_creates_workouts_with_given_visibilities(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
        input_desc: str,
        input_visibility: "VisibilityLevel",
    ) -> None:
        service = self.get_service(
            app,
            user_1,
            sport_1_cycling,
            "tests/files/gpx_test.zip",
            workout_data={
                "analysis_visibility": input_visibility,
                "map_visibility": input_visibility,
                "workout_visibility": input_visibility,
            },
        )

        service.process()

        for workout in Workout.query.all():
            assert workout.analysis_visibility == input_visibility
            assert workout.map_visibility == input_visibility
            assert workout.workout_visibility == input_visibility

    def test_it_creates_workouts_and_returns_error_when_one_workout_is_errored(
        self,
        app: "Flask",
        user_1: "User",
        gpx_file: str,
        sport_1_cycling: "Sport",
    ) -> None:
        service = self.get_service(
            app, user_1, sport_1_cycling, "tests/files/gpx_test.zip"
        )

        with (
            patch.object(
                WorkoutGpxCreationService,
                "get_map_hash",
                side_effect=[
                    None,  # processing first file w/o error
                    Exception("error"),  # error on second file
                    None,  # processing third file w/o error
                ],
            ),
        ):
            service.process()
            db.session.commit()

        workouts = Workout.query.all()
        assert len(workouts) == 2
        assert {workout.title for workout in workouts} == {
            "just a workout n°1",
            "just a workout n°3",
        }

        undeleted_files = self.get_undeleted_files(app, user_1)
        assert len(undeleted_files) == 4  # 2 gpx and 2 map gpx

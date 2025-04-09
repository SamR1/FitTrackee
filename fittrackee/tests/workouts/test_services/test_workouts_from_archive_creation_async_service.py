import os
import shutil
import tempfile
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from unittest.mock import MagicMock, patch

import pytest

from fittrackee import db
from fittrackee.users.models import UserTask
from fittrackee.workouts.exceptions import WorkoutException
from fittrackee.workouts.services import (
    WorkoutsFromArchiveCreationAsyncService,
)
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsData,
)

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class WorkoutsFromArchiveCreationAsyncServiceTestCase:
    @staticmethod
    def get_upload_task(
        user: "User",
        workouts_data: Dict,
        files_to_process: List[str],
        equipment_ids: Optional[List[int]],
        file_path: str,
    ) -> "UserTask":
        upload_task = UserTask(
            user_id=user.id,
            task_type="workouts_archive_upload",
            data={
                "workouts_data": workouts_data,
                "files_to_process": files_to_process,
                "equipment_ids": equipment_ids,
            },
            file_path=file_path,
        )
        db.session.add(upload_task)
        db.session.commit()
        return upload_task


class TestWorkoutsFromArchiveCreationAsyncServiceInstantiation(
    WorkoutsFromArchiveCreationAsyncServiceTestCase
):
    def test_it_raises_error_when_task_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        with pytest.raises(WorkoutException, match="no import task found"):
            WorkoutsFromArchiveCreationAsyncService(task_id=1)

    def test_it_raises_error_when_task_type_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        upload_task = UserTask(
            user_id=user_1.id,
            task_type="user_data_export",
        )
        db.session.add(upload_task)
        db.session.commit()

        with pytest.raises(WorkoutException, match="no import task found"):
            WorkoutsFromArchiveCreationAsyncService(task_id=upload_task.id)

    def test_it_instantiates_service(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        workouts_data = {"sport_id": sport_1_cycling.id}
        files_to_process = ["example.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        file_path = "some path"
        upload_task = self.get_upload_task(
            user_1, workouts_data, files_to_process, equipment_ids, file_path
        )

        service = WorkoutsFromArchiveCreationAsyncService(task_id=1)

        assert service.auth_user == user_1
        assert service.equipment_ids == equipment_ids
        assert service.file_path == file_path
        assert service.files_to_process == files_to_process
        assert service.upload_task == upload_task
        assert service.workouts_data == WorkoutsData(**workouts_data)  # type: ignore


class TestWorkoutsFromArchiveCreationAsyncServiceProcess(
    WorkoutsFromArchiveCreationAsyncServiceTestCase
):
    def test_it_returns_empty_workouts_lists_when_file_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        files_to_process = ["example.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        file_path = "invalid/path"
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )

        new_workouts, processing_output = service.process()

        assert new_workouts == []
        assert processing_output == {
            "errored_workouts": {},
            "task_short_id": upload_task.short_id,
        }

    def test_it_updates_task_with_error_when_file_does_not_exist(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        files_to_process = ["example.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        file_path = "invalid/path"
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )

        service.process()

        assert upload_task.progress == 0
        assert upload_task.errored is True
        assert upload_task.errors == {
            "archive": "archive file does not exist",
            "files": {},
        }

    @pytest.mark.parametrize("input_equipment_ids", [None, []])
    def test_it_calls_process_archive_content_when_no_equipment_ids(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        input_equipment_ids: Union[List, None],
    ) -> None:
        files_to_process = ["example.gpx"]
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=input_equipment_ids,
            file_path="some/path",
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )
        open_mock = MagicMock()

        with (
            patch.object(
                WorkoutsFromArchiveCreationAsyncService,
                "process_archive_content",
                return_value=([], {}),
            ) as process_archive_content_mock,
            patch(
                "builtins.open",
                return_value=open_mock,
            ),
        ):
            service.process()

        process_archive_content_mock.assert_called_once_with(
            archive_content=open_mock.__enter__(),
            files_to_process=files_to_process,
            equipments=input_equipment_ids,
            upload_task=upload_task,
        )

    def test_it_calls_process_archive_content_when_equipment_ids_are_provided(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        files_to_process = ["example.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path="some/path",
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )
        open_mock = MagicMock()

        with (
            patch.object(
                WorkoutsFromArchiveCreationAsyncService,
                "process_archive_content",
                return_value=([], {}),
            ) as process_archive_content_mock,
            patch(
                "builtins.open",
                return_value=open_mock,
            ),
        ):
            service.process()

        process_archive_content_mock.assert_called_once_with(
            archive_content=open_mock.__enter__(),
            files_to_process=files_to_process,
            equipments=[equipment_bike_user_1],
            upload_task=upload_task,
        )

    def test_it_creates_workouts(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        files_to_process = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        fd, file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        shutil.copyfile(
            os.path.join(app.root_path, "tests/files/gpx_test.zip"), file_path
        )
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )

        workouts, processing_output = service.process()

        assert len(workouts) == 3
        assert processing_output == {
            "errored_workouts": {},
            "task_short_id": upload_task.short_id,
        }

    def test_it_updates_task(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        files_to_process = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        fd, file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        shutil.copyfile(
            os.path.join(app.root_path, "tests/files/gpx_test.zip"), file_path
        )
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )

        service.process()

        assert upload_task.progress == 100
        assert upload_task.errored is False
        assert upload_task.errors == {
            "archive": None,
            "files": {},
        }

    def test_it_deletes_temp_file_after_import(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        equipment_bike_user_1: "Equipment",
    ) -> None:
        files_to_process = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]
        equipment_ids = [equipment_bike_user_1.id]
        fd, file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        shutil.copyfile(
            os.path.join(app.root_path, "tests/files/gpx_test.zip"), file_path
        )
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )

        service.process()

        assert os.path.isfile(file_path) is False

    def test_it_creates_workout_and_store_error_when_one_file_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        files_to_process = ["test_1.gpx", "test_4.gpx"]
        fd, file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        shutil.copyfile(
            os.path.join(app.root_path, "tests/files/gpx_test_incorrect.zip"),
            file_path,
        )
        upload_task = self.get_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=None,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )

        new_workouts, _ = service.process()

        assert len(new_workouts) == 1
        assert upload_task.progress == 100
        assert upload_task.errored is True
        assert upload_task.errors == {
            "archive": None,
            "files": {"test_4.gpx": "no tracks in gpx file"},
        }

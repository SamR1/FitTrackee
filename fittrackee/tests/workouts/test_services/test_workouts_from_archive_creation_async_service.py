import os
import shutil
import tempfile
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Union
from unittest.mock import MagicMock, patch

import pytest
from time_machine import travel

from fittrackee.users.models import Notification
from fittrackee.workouts.exceptions import WorkoutException
from fittrackee.workouts.services import (
    WorkoutsFromArchiveCreationAsyncService,
)
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsData,
)

from ...mixins import UserTaskMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.equipments.models import Equipment
    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestWorkoutsFromArchiveCreationAsyncServiceInstantiation(UserTaskMixin):
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
        data_export_task = self.create_user_data_export_task(user_1)

        with pytest.raises(WorkoutException, match="no import task found"):
            WorkoutsFromArchiveCreationAsyncService(
                task_id=data_export_task.id
            )

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
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data=workouts_data,
            files_to_process=files_to_process,
            equipment_ids=equipment_ids,
            file_path=file_path,
        )

        service = WorkoutsFromArchiveCreationAsyncService(task_id=1)

        assert service.auth_user == user_1
        assert service.equipment_ids == equipment_ids
        assert service.file_path == file_path
        assert service.files_to_process == files_to_process
        assert service.upload_task == upload_task
        assert service.workouts_data == WorkoutsData(**workouts_data)  # type: ignore


class TestWorkoutsFromArchiveCreationAsyncServiceProcess(UserTaskMixin):
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
        upload_task = self.create_workouts_upload_task(
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
        upload_task = self.create_workouts_upload_task(
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
        upload_task = self.create_workouts_upload_task(
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
        upload_task = self.create_workouts_upload_task(
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
        upload_task = self.create_workouts_upload_task(
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
        upload_task = self.create_workouts_upload_task(
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
        upload_task = self.create_workouts_upload_task(
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

    def test_it_creates_notification(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        files_to_process = ["test_1.gpx", "test_2.gpx", "test_3.gpx"]
        fd, file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        shutil.copyfile(
            os.path.join(app.root_path, "tests/files/gpx_test.zip"), file_path
        )
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=files_to_process,
            equipment_ids=None,
            file_path=file_path,
        )
        service = WorkoutsFromArchiveCreationAsyncService(
            task_id=upload_task.id
        )
        now = datetime.now(tz=timezone.utc)

        with travel(now, tick=False):
            service.process()

        notification = Notification.query.filter_by(
            event_object_id=upload_task.id
        ).one()
        assert notification.created_at == now
        assert notification.event_type == upload_task.task_type
        assert notification.from_user_id == user_1.id
        assert notification.marked_as_read is False
        assert notification.to_user_id == user_1.id

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
        upload_task = self.create_workouts_upload_task(
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

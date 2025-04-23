import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict
from unittest.mock import MagicMock, patch

import pytest
from time_machine import travel

from fittrackee import db
from fittrackee.exceptions import TaskException
from fittrackee.users.models import Notification
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsFromArchiveCreationAsyncService,
)
from fittrackee.workouts.tasks import (
    process_workouts_archive_upload,
    process_workouts_archives_uploads,
    update_task_and_clean,
)

from ..mixins import RandomMixin, UserTaskMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestUpdateTaskAndClean(UserTaskMixin):
    def test_it_does_not_raise_error_when_no_task(self) -> None:
        update_task_and_clean(error="some error")

    def test_it_updates_task_when_task_is_provided(
        self, app: "Flask", user_1: "User"
    ) -> None:
        error = "some error"
        task = self.create_workouts_upload_task(user_1)

        update_task_and_clean(error=error, upload_task=task)

        assert task.aborted is False
        assert task.errored is True
        assert task.errors == {
            "archive": error,
            "files": {},
        }

    def test_it_updates_task_when_task_id_is_provided(
        self, app: "Flask", user_1: "User"
    ) -> None:
        error = "some error"
        task = self.create_workouts_upload_task(user_1)

        update_task_and_clean(error=error, upload_task_id=task.id)

        assert task.aborted is False
        assert task.errored is True
        assert task.errors == {
            "archive": error,
            "files": {},
        }

    def test_it_updates_task_when_task_is_aborted(
        self, app: "Flask", user_1: "User"
    ) -> None:
        task = self.create_workouts_upload_task(user_1)

        update_task_and_clean(
            error="task execution aborted", upload_task_id=task.id
        )

        assert task.aborted is True
        assert task.errored is False
        assert task.errors == {
            "archive": None,
            "files": {},
        }

    def test_it_creates_notification(
        self, app: "Flask", user_1: "User"
    ) -> None:
        task = self.create_workouts_upload_task(user_1)

        update_task_and_clean(error="some error", upload_task_id=task.id)

        assert (
            Notification.query.filter_by(
                from_user_id=task.user_id,
                to_user_id=task.user_id,
                event_object_id=task.id,
                event_type=task.task_type,
            ).first()
            is not None
        )

    def test_it_does_not_create_notification_when_task_is_aborted(
        self, app: "Flask", user_1: "User"
    ) -> None:
        task = self.create_workouts_upload_task(user_1)

        update_task_and_clean(
            error="task execution aborted", upload_task_id=task.id
        )

        assert (
            Notification.query.filter_by(
                from_user_id=task.user_id,
                to_user_id=task.user_id,
                event_object_id=task.id,
                event_type=task.task_type,
            ).first()
            is None
        )

    def test_it_does_not_raise_error_when_notification_already_exists(
        self, app: "Flask", user_1: "User"
    ) -> None:
        task = self.create_workouts_upload_task(user_1)
        notification = Notification(
            from_user_id=task.user_id,
            to_user_id=task.user_id,
            created_at=datetime.now(tz=timezone.utc),
            event_object_id=task.id,
            event_type=task.task_type,
        )
        db.session.add(notification)
        db.session.commit()

        update_task_and_clean(error="some error", upload_task_id=task.id)

    def test_it_deletes_temporary_archive_file(
        self, app: "Flask", user_1: "User"
    ) -> None:
        file_path = self.generate_temporary_archive()
        task = self.create_workouts_upload_task(user_1, file_path=file_path)

        update_task_and_clean(error="some error", upload_task_id=task.id)

        assert os.path.isfile(file_path) is False


class TestProcessWorkoutsArchivesUploads(UserTaskMixin):
    def test_it_returns_0_when_no_queued_archive_upload_tasks(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.create_user_data_export_task(user_1)
        self.create_workouts_upload_task(user_1, progress=10)
        self.create_workouts_upload_task(user_1, errored=True)
        logger = MagicMock()

        count = process_workouts_archives_uploads(max_count=1, logger=logger)

        assert count == 0

    def test_it_process_only_max_count_of_archive_upload_tasks(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        workouts_data = {"sport_id": sport_1_cycling.id}
        task_1 = self.create_workouts_upload_task(
            user_1, workouts_data=workouts_data
        )
        task_2 = self.create_workouts_upload_task(
            user_1, workouts_data=workouts_data
        )
        now = datetime.now(tz=timezone.utc)
        logger = MagicMock()

        with travel(now, tick=False):
            count = process_workouts_archives_uploads(
                max_count=1, logger=logger
            )

        assert count == 1
        assert task_1.updated_at == now
        assert task_2.updated_at != now

    def test_it_updates_task_on_error(
        self, app: "Flask", user_1: "User", sport_1_cycling: "Sport"
    ) -> None:
        task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            file_path="invalid/file/path",
        )
        logger = MagicMock()

        try:
            with (
                patch.object(
                    WorkoutsFromArchiveCreationAsyncService,
                    "process",
                    side_effect=Exception,
                ),
                patch(
                    "fittrackee.workouts.tasks.update_task_and_clean"
                ) as update_task_and_clean_mock,
            ):
                process_workouts_archives_uploads(max_count=1, logger=logger)
        except Exception:
            pass

        update_task_and_clean_mock.assert_called_once_with(
            error="error during archive processing", upload_task_id=task.id
        )


class TestProcessWorkoutsArchivesUploadTask(RandomMixin, UserTaskMixin):
    def test_it_raises_error_when_task_id_is_invalid(
        self, app: "Flask", user_1: "User"
    ) -> None:
        logger = MagicMock()

        with pytest.raises(TaskException, match="Invalid task id"):
            process_workouts_archive_upload(
                task_short_id="invalid", logger=logger
            )

    def test_it_raises_error_when_task_does_not_exist(
        self, app: "Flask", user_1: "User"
    ) -> None:
        logger = MagicMock()

        with pytest.raises(TaskException, match="No task found"):
            process_workouts_archive_upload(
                task_short_id=self.random_short_id(), logger=logger
            )

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [
            ("aborted", {"aborted": True}),
            ("errored", {"errored": True}),
            ("successful", {"progress": 100}),
        ],
    )
    def test_it_raises_error_when_task_is_not_queued(
        self,
        app: "Flask",
        user_1: "User",
        input_status: str,
        input_task_data: Dict,
    ) -> None:
        upload_task = self.create_workouts_upload_task(
            user_1, **input_task_data
        )
        logger = MagicMock()

        with pytest.raises(TaskException, match="Task is not queued"):
            process_workouts_archive_upload(
                task_short_id=upload_task.short_id, logger=logger
            )

    def test_it_process_queued_task(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        workouts_data = {"sport_id": sport_1_cycling.id}
        upload_task = self.create_workouts_upload_task(
            user_1, workouts_data=workouts_data
        )
        now = datetime.now(tz=timezone.utc)
        logger = MagicMock()

        with travel(now, tick=False):
            process_workouts_archive_upload(
                task_short_id=upload_task.short_id, logger=logger
            )

        assert upload_task.updated_at == now

from typing import TYPE_CHECKING
from unittest.mock import patch

from click.testing import CliRunner

from fittrackee import db
from fittrackee.cli import cli
from fittrackee.workouts.commands import logger
from fittrackee.workouts.exceptions import WorkoutException
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsFromArchiveCreationAsyncService,
)

from ..mixins import UserTaskMixin

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestCliWorkoutsArchiveUpload(UserTaskMixin):
    def test_it_displays_0_when_no_archives_to_process(
        self, app: "Flask", caplog: "LogCaptureFixture", user_1: "User"
    ) -> None:
        self.create_workouts_upload_task(user_1, errored=True)
        self.create_workouts_upload_task(user_1, aborted=True)
        self.create_workouts_upload_task(user_1, progress=10)
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "archive_upload",
                "--max",
                "1",
            ],
        )

        assert result.exit_code == 0
        assert caplog.records[0].message == "\nWorkouts archives processed: 0."

    def test_it_raises_error_when_archive_is_invalid(
        self, app: "Flask", caplog: "LogCaptureFixture", user_1: "User"
    ) -> None:
        self.create_workouts_upload_task(user_1)
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "archive_upload",
                "--max",
                "1",
            ],
        )

        assert result.exit_code == 1
        assert isinstance(result.exception, WorkoutException)

    def test_it_calls_process_workouts_archives_upload(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["example.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()
        max_archives = 3

        with patch(
            "fittrackee.workouts.commands.process_workouts_archives_upload",
            return_value=max_archives,
        ) as process_workouts_archives_upload_mock:
            runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_upload",
                    "--max",
                    str(max_archives),
                ],
            )

        process_workouts_archives_upload_mock.assert_called_once_with(
            max_archives, logger
        )

    def test_it_displayed_errored_files_count(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()
        upload_task.errors = {
            "archive": None,
            "files": {"file_2": "some errors"},
        }
        db.session.commit()

        with patch.object(
            WorkoutsFromArchiveCreationAsyncService,
            "process",
            return_value=1,
        ):
            result = runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_upload",
                    "--max",
                    "1",
                ],
            )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message
            == "Processing task '1' (files: 2, size: 0 Bytes)..."
        )
        assert caplog.records[1].message == " > errored files: 1"
        assert caplog.records[2].message == "\nWorkouts archives processed: 1."

    def test_it_displayed_archive_error(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        # archive file does not exist
        self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["file_1.gpx", "file_2.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "archive_upload",
                "--max",
                "1",
            ],
        )

        assert result.exit_code == 0

        assert (
            caplog.records[0].message
            == "Processing task '1' (files: 2, size: 0 Bytes)..."
        )
        assert (
            caplog.records[1].message
            == " > archive error: archive file does not exist"
        )
        assert caplog.records[2].message == "\nWorkouts archives processed: 1."

    def test_it_displays_count_when_archives_are_processed(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["example.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()

        with patch.object(
            WorkoutsFromArchiveCreationAsyncService,
            "process",
            return_value=1,
        ):
            result = runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_upload",
                    "--max",
                    "1",
                ],
            )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message
            == "Processing task '1' (files: 1, size: 0 Bytes)..."
        )
        assert caplog.records[1].message == "\nWorkouts archives processed: 1."

    def test_it_updates_task_on_keyboard_interruption(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["example.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()

        with patch.object(
            WorkoutsFromArchiveCreationAsyncService,
            "process",
            side_effect=KeyboardInterrupt(),
        ):
            result = runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_upload",
                    "--max",
                    "1",
                ],
            )

        db.session.refresh(upload_task)
        assert upload_task.aborted is True
        assert upload_task.errored is False
        assert upload_task.errors == {"archive": None, "files": {}}
        assert result.exit_code == 1
        assert len(caplog.records) == 1
        assert (
            caplog.records[0].message
            == "Processing task '1' (files: 1, size: 0 Bytes)..."
        )

    def test_it_updates_task_on_error(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["example.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()

        with patch.object(
            WorkoutsFromArchiveCreationAsyncService,
            "process",
            side_effect=Exception(),
        ):
            result = runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_upload",
                    "--max",
                    "1",
                ],
            )

        db.session.refresh(upload_task)
        assert upload_task.aborted is False
        assert upload_task.errored is True
        assert upload_task.errors == {
            "archive": "error during archive processing",
            "files": {},
        }
        assert result.exit_code == 1
        assert len(caplog.records) == 1
        assert (
            caplog.records[0].message
            == "Processing task '1' (files: 1, size: 0 Bytes)..."
        )

import os
import tempfile
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

from ..mixins import RandomMixin, UserTaskMixin

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture
    from flask import Flask

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestCliWorkoutsArchiveUploads(UserTaskMixin):
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
                "archive_uploads",
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
                "archive_uploads",
                "--max",
                "1",
            ],
        )

        assert result.exit_code == 1
        assert isinstance(result.exception, WorkoutException)

    def test_it_calls_process_workouts_archives_uploads(
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
            "fittrackee.workouts.commands.process_workouts_archives_uploads",
            return_value=max_archives,
        ) as process_workouts_archives_uploads_mock:
            runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_uploads",
                    "--max",
                    str(max_archives),
                ],
            )

        process_workouts_archives_uploads_mock.assert_called_once_with(
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
                    "archive_uploads",
                    "--max",
                    "1",
                ],
            )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 2, size: 0 Bytes)"
        )
        assert caplog.records[1].message == " > errored files: 1"
        assert caplog.records[2].message == " > done."
        assert caplog.records[3].message == "\nWorkouts archives processed: 1."

    def test_it_displayed_archive_error(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        # archive file does not exist
        upload_task = self.create_workouts_upload_task(
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
                "archive_uploads",
                "--max",
                "1",
            ],
        )

        assert result.exit_code == 0

        assert (
            caplog.records[0].message
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 2, size: 0 Bytes)"
        )
        assert (
            caplog.records[1].message
            == " > archive error: archive file does not exist"
        )
        assert caplog.records[2].message == " > done."
        assert caplog.records[3].message == "\nWorkouts archives processed: 1."

    def test_it_displays_count_when_archives_are_processed(
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
            return_value=1,
        ):
            result = runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_uploads",
                    "--max",
                    "1",
                ],
            )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 1, size: 0 Bytes)"
        )
        assert caplog.records[1].message == " > done."
        assert caplog.records[2].message == "\nWorkouts archives processed: 1."

    def test_it_displays_files_detail_when_verbose_is_enabled(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        with (
            open(fd, "wb") as temp_file,
            open(
                os.path.join(
                    app.root_path, "tests/files/gpx_test_incorrect.zip"
                ),
                "rb",
            ) as zip_file,
        ):
            temp_file.write(zip_file.read())
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["test_4.gpx", "test_1.gpx"],
            equipment_ids=None,
            file_path=temp_file_path,
        )
        upload_task.file_size = 1000
        db.session.commit()
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "archive_uploads",
                "--max",
                "1",
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 2, size: 1.0 kB)"
        )
        assert caplog.records[1].message == " > starting archive processing..."
        assert caplog.records[2].message == "  - file 1/2"
        assert (
            caplog.records[3].message
            == "    > error occurred: no tracks in gpx file"
        )
        assert caplog.records[4].message == "  - file 2/2"
        assert caplog.records[5].message == "    > upload done"
        assert caplog.records[6].message == " > errored files: 1"
        assert caplog.records[7].message == " > done."
        assert caplog.records[8].message == "\nWorkouts archives processed: 1."

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
                    "archive_uploads",
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
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 1, size: 0 Bytes)"
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
                    "archive_uploads",
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
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 1, size: 0 Bytes)"
        )


class TestCliWorkoutsArchiveUploadTask(RandomMixin, UserTaskMixin):
    def test_it_raises_error_when_process_workouts_archives_upload_raisies_exceptio(  # noqa
        self, app: "Flask", caplog: "LogCaptureFixture", user_1: "User"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "archive_upload",
                "--id",
                self.random_short_id(),
            ],
        )

        assert result.exit_code == 1
        assert result.exception is not None

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
                    "--id",
                    upload_task.short_id,
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
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 1, size: 0 Bytes)"
        )

    def test_it_calls_process_workouts_archive_upload(
        self,
        app: "Flask",
        user_1: "User",
        sport_1_cycling: "Sport",
        caplog: "LogCaptureFixture",
    ) -> None:
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["example.gpx"],
            equipment_ids=None,
            file_path="some path",
        )
        runner = CliRunner()

        with patch(
            "fittrackee.workouts.commands.process_workouts_archive_upload",
        ) as process_workouts_archive_upload_mock:
            result = runner.invoke(
                cli,
                [
                    "workouts",
                    "archive_upload",
                    "--id",
                    upload_task.short_id,
                ],
            )

        process_workouts_archive_upload_mock.assert_called_once_with(
            upload_task.short_id, logger
        )

        assert result.exit_code == 0
        assert caplog.records[0].message == "\nDone."

    def test_it_displays_message_when_verbose_is_enabled(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        sport_1_cycling: "Sport",
    ) -> None:
        fd, temp_file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        with (
            open(fd, "wb") as temp_file,
            open(
                os.path.join(
                    app.root_path, "tests/files/gpx_test_incorrect.zip"
                ),
                "rb",
            ) as zip_file,
        ):
            temp_file.write(zip_file.read())
        upload_task = self.create_workouts_upload_task(
            user_1,
            workouts_data={"sport_id": sport_1_cycling.id},
            files_to_process=["test_4.gpx", "test_1.gpx"],
            equipment_ids=None,
            file_path=temp_file_path,
        )
        upload_task.file_size = 1000
        db.session.commit()
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ["workouts", "archive_upload", "--id", upload_task.short_id, "-v"],
        )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 2, size: 1.0 kB)"
        )
        assert caplog.records[1].message == " > starting archive processing..."
        assert caplog.records[2].message == "  - file 1/2"
        assert (
            caplog.records[3].message
            == "    > error occurred: no tracks in gpx file"
        )
        assert caplog.records[4].message == "  - file 2/2"
        assert caplog.records[5].message == "    > upload done"
        assert caplog.records[6].message == " > errored files: 1"
        assert caplog.records[7].message == "\nDone."

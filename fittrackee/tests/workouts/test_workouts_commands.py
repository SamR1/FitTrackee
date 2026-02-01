import os
import tempfile
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
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
        error = "some error"

        with patch.object(
            WorkoutsFromArchiveCreationAsyncService,
            "process",
            side_effect=Exception(error),
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
        assert len(caplog.records) == 2
        assert (
            caplog.records[0].message
            == f"Processing task '{upload_task.short_id}' "
            f"(files: 1, size: 0 Bytes)"
        )
        assert caplog.records[1].message == error

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


class TestCliWorkoutsRefresh(UserTaskMixin):
    def test_it_displays_message_when_no_workouts_to_refresh(
        self, app: "Flask", caplog: "LogCaptureFixture"
    ) -> None:
        runner = CliRunner()

        with patch("click.confirm"):
            result = runner.invoke(cli, ["workouts", "refresh"])

        assert result.exit_code == 0
        assert caplog.messages == ["No workouts to refresh.", "\nDone."]

    def test_it_displays_message_when_no_workouts_to_refresh_and_verbose_is_true(  # noqa
        self, app: "Flask", caplog: "LogCaptureFixture"
    ) -> None:
        runner = CliRunner()

        with patch("click.confirm"):
            result = runner.invoke(cli, ["workouts", "refresh", "--verbose"])

        assert result.exit_code == 0
        assert caplog.messages == ["No workouts to refresh.", "\nDone."]

    def test_it_raises_error_when_sport_does_not_exist(
        self, app: "Flask"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                "--sport-id",
                "0",
            ],
        )

        assert result.exit_code == 2
        assert (
            "Invalid value for '--sport-id': invalid sport id '0'"
            in result.output
        )

    def test_it_raises_error_when_user_does_not_exist(
        self, app: "Flask"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                "--user",
                "Sam",
            ],
        )

        assert result.exit_code == 2
        assert (
            "Invalid value for '--user': user 'Sam' does not exist"
            in result.output
        )

    @pytest.mark.parametrize("input_option", ["--from", "--to"])
    def test_it_raises_error_when_date_format_is_invalid(
        self, app: "Flask", input_option: str
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                input_option,
                "01-01-2025",
            ],
        )

        assert result.exit_code == 2
        assert "'01-01-2025' does not match format '%Y-%m-%d'" in result.output

    def test_it_raises_error_when_order_is_invalid(self, app: "Flask") -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                "--order",
                "invalid",
            ],
        )

        assert result.exit_code == 2
        assert "Invalid value for '--order'" in result.output

    def test_it_raises_error_when_extension_is_invalid(
        self, app: "Flask"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                "--extension",
                ".txt",
            ],
        )

        assert result.exit_code == 2
        assert "Invalid value for '--extension'" in result.output

    def test_it_raises_error_when_new_sport_id_not_provided_with_sport_id(
        self, app: "Flask", sport_1_cycling: "Sport"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                "--new-sport-id",
                "1",
            ],
        )

        assert result.exit_code == 2
        assert (
            "'--new-sport-id' must be provided with '--sport-id'"
            in result.output
        )

    def test_it_raises_error_when_on_file_error_is_invalid(
        self, app: "Flask"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "workouts",
                "refresh",
                "--on-file-error",
                "invalid",
            ],
        )

        assert result.exit_code == 2
        assert "Invalid value for '--on-file-error'" in result.output

    def test_it_calls_workouts_from_file_refresh_service_with_default_values(
        self, app: "Flask"
    ) -> None:
        runner = CliRunner()

        with (
            patch("click.confirm"),
            patch(
                "fittrackee.workouts.commands.WorkoutsFromFileRefreshService"
            ) as refresh_with_file_service_mock,
            patch(
                "fittrackee.workouts.commands.WorkoutsWithoutFileRefreshService"
            ) as refresh_without_file_service_mock,
        ):
            runner.invoke(cli, ["workouts", "refresh"])

        refresh_with_file_service_mock.assert_called_once_with(
            sport_id=None,
            new_sport_id=None,
            date_from=None,
            date_to=None,
            per_page=10,
            page=1,
            order="asc",
            user=None,
            extension=None,
            with_weather=False,
            with_elevation=False,
            on_file_error=None,
            logger=logger,
            verbose=False,
        )
        refresh_with_file_service_mock.return_value.refresh.assert_called_once()
        refresh_without_file_service_mock.assert_not_called()

    def test_it_calls_workouts_from_file_refresh_service_with_all_values(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
    ) -> None:
        runner = CliRunner()

        with (
            patch("click.confirm"),
            patch(
                "fittrackee.workouts.commands.WorkoutsFromFileRefreshService"
            ) as refresh_with_file_service_mock,
            patch(
                "fittrackee.workouts.commands.WorkoutsWithoutFileRefreshService"
            ) as refresh_without_file_service_mock,
        ):
            runner.invoke(
                cli,
                [
                    "workouts",
                    "refresh",
                    "--sport-id",
                    f"{sport_1_cycling.id}",
                    "--new-sport-id",
                    f"{sport_2_running.id}",
                    "--user",
                    user_1.username,
                    "--from",
                    "2025-01-01",
                    "--to",
                    "2025-06-01",
                    "--per-page",
                    "100",
                    "--page",
                    "2",
                    "--order",
                    "desc",
                    "--extension",
                    "fit",
                    "--with-weather",
                    "--with-elevation",
                    "--on-file-error",
                    "delete-workout",
                    "--verbose",
                ],
            )

        refresh_with_file_service_mock.assert_called_once_with(
            sport_id=sport_1_cycling.id,
            new_sport_id=sport_2_running.id,
            date_from=datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
            date_to=datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc),
            per_page=100,
            page=2,
            order="desc",
            user=user_1.username,
            extension="fit",
            with_weather=True,
            with_elevation=True,
            on_file_error="delete-workout",
            logger=logger,
            verbose=True,
        )
        refresh_with_file_service_mock.return_value.refresh.assert_called_once()
        refresh_without_file_service_mock.assert_not_called()

    def test_it_calls_workouts_without_file_refresh_service_with_default_values(  # noqa
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
    ) -> None:
        runner = CliRunner()

        with (
            patch("click.confirm"),
            patch(
                "fittrackee.workouts.commands.WorkoutsFromFileRefreshService"
            ) as refresh_with_file_service_mock,
            patch(
                "fittrackee.workouts.commands.WorkoutsWithoutFileRefreshService"
            ) as refresh_without_file_service_mock,
        ):
            runner.invoke(
                cli,
                [
                    "workouts",
                    "refresh",
                    "--without-file",
                ],
            )

        refresh_without_file_service_mock.assert_called_once_with(
            sport_id=None,
            new_sport_id=None,
            date_from=None,
            date_to=None,
            per_page=10,
            page=1,
            order="asc",
            user=None,
            logger=logger,
            verbose=False,
        )
        refresh_without_file_service_mock.return_value.refresh.assert_called_once()
        refresh_with_file_service_mock.assert_not_called()

    def test_it_calls_workouts_without_file_refresh_service_with_all_values(
        self,
        app: "Flask",
        sport_1_cycling: "Sport",
        sport_2_running: "Sport",
        user_1: "User",
    ) -> None:
        runner = CliRunner()

        with (
            patch("click.confirm"),
            patch(
                "fittrackee.workouts.commands.WorkoutsFromFileRefreshService"
            ) as refresh_with_file_service_mock,
            patch(
                "fittrackee.workouts.commands.WorkoutsWithoutFileRefreshService"
            ) as refresh_without_file_service_mock,
        ):
            runner.invoke(
                cli,
                [
                    "workouts",
                    "refresh",
                    "--sport-id",
                    f"{sport_1_cycling.id}",
                    "--new-sport-id",
                    f"{sport_2_running.id}",
                    "--user",
                    user_1.username,
                    "--from",
                    "2025-01-01",
                    "--to",
                    "2025-06-01",
                    "--per-page",
                    "100",
                    "--page",
                    "2",
                    "--order",
                    "desc",
                    "--without-file",
                    "--verbose",
                ],
            )

        refresh_without_file_service_mock.assert_called_once_with(
            sport_id=sport_1_cycling.id,
            new_sport_id=sport_2_running.id,
            date_from=datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc),
            date_to=datetime(2025, 6, 1, 0, 0, tzinfo=timezone.utc),
            per_page=100,
            page=2,
            order="desc",
            user=user_1.username,
            logger=logger,
            verbose=True,
        )
        refresh_without_file_service_mock.return_value.refresh.assert_called_once()
        refresh_with_file_service_mock.assert_not_called()

    def test_it_displays_error_when_refresh_with_file_service_raises_error(
        self, app: "Flask", caplog: "LogCaptureFixture"
    ) -> None:
        error_message = "some error"
        runner = CliRunner()

        with (
            patch("click.confirm"),
            patch(
                "fittrackee.workouts.commands.WorkoutsFromFileRefreshService"
            ) as refresh_with_file_service_mock,
        ):
            refresh_with_file_service_mock.return_value.refresh.side_effect = (
                Exception(error_message)
            )

            result = runner.invoke(cli, ["workouts", "refresh"])

        assert result.exit_code == 1
        assert caplog.messages == [error_message]

    def test_it_displays_error_when_refresh_without_file_service_raises_error(
        self, app: "Flask", caplog: "LogCaptureFixture"
    ) -> None:
        error_message = "some error"
        runner = CliRunner()

        with (
            patch("click.confirm"),
            patch(
                "fittrackee.workouts.commands.WorkoutsWithoutFileRefreshService"
            ) as refresh_without_file_service_mock,
        ):
            refresh_without_file_service_mock.return_value.refresh.side_effect = Exception(  # noqa
                error_message
            )

            result = runner.invoke(
                cli, ["workouts", "refresh", "--without-file"]
            )

        assert result.exit_code == 1
        assert caplog.messages == [error_message]

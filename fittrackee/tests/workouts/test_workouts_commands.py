from typing import TYPE_CHECKING
from unittest.mock import patch

from click.testing import CliRunner
from flask import Flask

from fittrackee.cli import cli
from fittrackee.workouts.exceptions import WorkoutException

from ..mixins import UserTaskMixin

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture

    from fittrackee.users.models import User
    from fittrackee.workouts.models import Sport


class TestCliWorkoutsArchiveUpload(UserTaskMixin):
    def test_it_displays_0_when_no_archives_to_process(
        self, app: Flask, caplog: "LogCaptureFixture"
    ) -> None:
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
        assert caplog.records[0].message == "Workouts archives processed: 0."

    def test_it_raises_error_when_archive_is_invalid(
        self, app: Flask, caplog: "LogCaptureFixture", user_1: "User"
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
        app: Flask,
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
            max_archives
        )

    def test_it_displays_count_when_archives_are_processed(
        self,
        app: Flask,
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
        assert caplog.records[0].message == "Workouts archives processed: 1."

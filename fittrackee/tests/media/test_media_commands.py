from typing import TYPE_CHECKING

from click.testing import CliRunner

from fittrackee.cli import cli
from fittrackee.media.models import Media

from ..mixins import MediaMixin

if TYPE_CHECKING:
    from _pytest.logging import LogCaptureFixture
    from flask import Flask

    from fittrackee.users.models import User


class TestCliMediaAttachmentsClean(MediaMixin):
    def test_it_displays_error_when_days_are_not_provided(
        self, app: "Flask", caplog: "LogCaptureFixture", user_1: "User"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            ["media_attachments", "clean_orphans"],
        )

        assert result.exit_code == 2
        assert "Error: Missing option '--days'." in result.output

    def test_it_displays_0_when_no_media_to_delete(
        self, app: "Flask", caplog: "LogCaptureFixture", user_1: "User"
    ) -> None:
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "media_attachments",
                "clean_orphans",
                "--days",
                "1",
            ],
        )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message == "Deleted orphan media attachments: 0."
        )
        assert caplog.records[1].message == "Freed space: 0 Bytes."

    def test_it_displays_counts_when_media_are_deleted(
        self,
        app: "Flask",
        caplog: "LogCaptureFixture",
        user_1: "User",
        user_2: "User",
    ) -> None:
        self.create_and_store_media(app, user_1)
        self.create_and_store_media(app, user_2)
        runner = CliRunner()

        result = runner.invoke(
            cli,
            [
                "media_attachments",
                "clean_orphans",
                "--days",
                "0",
            ],
        )

        assert result.exit_code == 0
        assert (
            caplog.records[0].message == "Deleted orphan media attachments: 2."
        )
        assert caplog.records[1].message == "Freed space: 2.0 kB."
        assert Media.query.count() == 0

import os
from typing import TYPE_CHECKING

import pytest

from fittrackee.users.tasks import update_task_and_clean

from ..mixins import RandomMixin, UserTaskMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestUpdateTaskAndClean(UserTaskMixin, RandomMixin):
    def test_it_does_not_raise_error_when_no_task(self, app: "Flask") -> None:
        update_task_and_clean(self.random_int())

    def test_it_updates_task(self, app: "Flask", user_1: "User") -> None:
        task = self.create_user_data_export_task(user_1)

        update_task_and_clean(task_id=task.id)

        assert task.errored is True
        assert task.errors == {}

    @pytest.mark.parametrize(
        "input_file",
        [
            "user_data.json",
            "user_workouts_data.json",
            "user_equipments_data.json",
            "user_comments_data.json",
            "export.zip",
        ],
    )
    def test_it_deletes_files(
        self, app: "Flask", user_1: "User", input_file: str
    ) -> None:
        file_path = self.generate_temporary_data_export(user_1.id, input_file)
        task = self.create_user_data_export_task(user_1, file_path=file_path)

        update_task_and_clean(task_id=task.id)

        assert os.path.isfile(file_path) is False

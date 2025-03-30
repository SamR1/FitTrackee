import json
from typing import TYPE_CHECKING

from fittrackee import db
from fittrackee.users.models import UserTask

from ..mixins import ApiTestCaseMixin, BaseTestMixin
from ..utils import jsonify_dict

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestWorkoutsTasksGetTasks(ApiTestCaseMixin, BaseTestMixin):
    route = "/api/workouts/tasks"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
    ) -> None:
        client = app.test_client()

        response = client.get(self.route)

        self.assert_401(response)

    def test_it_returns_empty_list_when_no_import_tasks_for_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        user_2_workout_import_task = UserTask(
            user_id=user_2.id, task_type="workouts_archive_import"
        )
        db.session.add(user_2_workout_import_task)
        user_1_export_data_task = UserTask(
            user_id=user_1.id, task_type="user_data_export"
        )
        db.session.add(user_1_export_data_task)
        db.session.commit()

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route, headers=dict(Authorization=f"Bearer {auth_token}")
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["data"]["tasks"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_tasks_ordered_by_creation_date(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        tasks = []
        for _ in range(3):
            export_data_task = UserTask(
                user_id=user_1.id, task_type="workouts_archive_import"
            )
            db.session.add(export_data_task)
            db.session.commit()
            tasks.append(export_data_task)

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route, headers=dict(Authorization=f"Bearer {auth_token}")
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        user_tasks = data["data"]["tasks"]
        assert len(user_tasks) == 3
        assert user_tasks[0] == jsonify_dict(tasks[2].serialize())
        assert user_tasks[1] == jsonify_dict(tasks[1].serialize())
        assert user_tasks[2] == jsonify_dict(tasks[0].serialize())
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 3,
        }

    def test_it_returns_page_2(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        tasks = []
        for _ in range(6):
            export_data_task = UserTask(
                user_id=user_1.id, task_type="workouts_archive_import"
            )
            db.session.add(export_data_task)
            db.session.commit()
            tasks.append(export_data_task)

        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            f"{self.route}?page=2",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["data"]["tasks"] == [jsonify_dict(tasks[0].serialize())]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 6,
        }


class TestWorkoutsTasksGetTask(ApiTestCaseMixin, BaseTestMixin):
    route = "/api/workouts/tasks/{task_id}"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
    ) -> None:
        client = app.test_client()

        response = client.get(
            self.route.format(task_id=self.random_short_id())
        )

        self.assert_401(response)

    def test_it_returns_404_when_no_task_found(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(task_id=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_404_when_task_do_not_belong_to_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        export_data_task = UserTask(
            user_id=user_2.id, task_type="workouts_archive_import"
        )
        db.session.add(export_data_task)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(task_id=export_data_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_user_task(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        export_data_task = UserTask(
            user_id=user_1.id, task_type="workouts_archive_import"
        )
        db.session.add(export_data_task)
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(task_id=export_data_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["task"] == jsonify_dict(export_data_task.serialize())

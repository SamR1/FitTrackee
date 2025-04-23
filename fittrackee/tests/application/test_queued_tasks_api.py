import json
from typing import TYPE_CHECKING

import pytest

from ..mixins import ApiTestCaseMixin, UserTaskMixin
from ..utils import jsonify_dict

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestGetQueuedTasksCount(UserTaskMixin, ApiTestCaseMixin):
    route = "api/tasks/queued"

    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.get(self.route, content_type="application/json")

        self.assert_401(response)

    def test_it_returns_403_when_user_has_no_admin_rights(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_zero_when_no_queued_tasks(
        self, app: "Flask", user_1_admin: "User", user_2: "User"
    ) -> None:
        self.create_user_data_export_task(user_2, progress=100)
        self.create_workouts_upload_task(user_2, errored=True)
        self.create_workouts_upload_task(user_2, aborted=True)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["counts"] == {
            "user_data_export": 0,
            "workouts_archive_upload": 0,
        }

    def test_it_returns_count_when_no_tasks(
        self, app: "Flask", user_1_admin: "User", user_2: "User"
    ) -> None:
        self.create_user_data_export_task(user_2)
        self.create_workouts_upload_task(user_2)
        self.create_workouts_upload_task(user_1_admin)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["counts"] == {
            "user_data_export": 1,
            "workouts_archive_upload": 2,
        }


class TestGetQueuedTasksForTaskType(UserTaskMixin, ApiTestCaseMixin):
    route = "api/tasks/queued/{task_type}"

    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.get(
            self.route.format(task_type="user_data_export"),
            content_type="application/json",
        )

        self.assert_401(response)

    def test_it_returns_403_when_user_has_no_admin_rights(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(task_type="user_data_export"),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_403(response)

    def test_it_returns_400_when_task_type_is_invalid(
        self, app: "Flask", user_1_admin: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(task_type="invalid"),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(response, "invalid task type", "invalid")

    @pytest.mark.parametrize(
        "input_task_type", ["user_data_export", "workouts_archive_upload"]
    )
    def test_it_returns_empty_list_when_no_queued_tasks_for_a_given_task_type(
        self,
        app: "Flask",
        user_1_admin: "User",
        user_2: "User",
        input_task_type: str,
    ) -> None:
        self.create_user_data_export_task(user_2, progress=100)
        self.create_workouts_upload_task(user_2, errored=True)
        self.create_workouts_upload_task(user_2, aborted=True)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(task_type=input_task_type),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["queued_tasks"] == []
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 0,
            "total": 0,
        }

    def test_it_returns_queued_data_export_tasks_ordered_by_creation_date_descending(  # noqa
        self,
        app: "Flask",
        user_1_admin: "User",
        user_2: "User",
        user_3: "User",
    ) -> None:
        user_2_data_export = self.create_user_data_export_task(user_2)
        user_3_data_export = self.create_user_data_export_task(user_3)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(task_type="user_data_export"),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["queued_tasks"] == [
            jsonify_dict(
                user_3_data_export.serialize(
                    current_user=user_1_admin, for_admin=True, task_user=user_3
                )
            ),
            jsonify_dict(
                user_2_data_export.serialize(
                    current_user=user_1_admin, for_admin=True, task_user=user_2
                )
            ),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 2,
        }

    def test_it_returns_queued_workouts_upload_tasks(
        self,
        app: "Flask",
        user_1_admin: "User",
        user_2: "User",
        user_3: "User",
    ) -> None:
        user_2_workouts_upload = self.create_workouts_upload_task(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            self.route.format(task_type="workouts_archive_upload"),
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["queued_tasks"] == [
            jsonify_dict(
                user_2_workouts_upload.serialize(
                    current_user=user_1_admin, for_admin=True, task_user=user_2
                )
            ),
        ]
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": False,
            "page": 1,
            "pages": 1,
            "total": 1,
        }

    def test_it_returns_page_2(
        self,
        app: "Flask",
        user_1_admin: "User",
        user_2: "User",
        user_3: "User",
    ) -> None:
        for _ in range(6):
            self.create_workouts_upload_task(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1_admin.email
        )

        response = client.get(
            f"{self.route.format(task_type='workouts_archive_upload')}?page=2",
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert len(data["queued_tasks"]) == 1
        assert data["pagination"] == {
            "has_next": False,
            "has_prev": True,
            "page": 2,
            "pages": 2,
            "total": 6,
        }

import json
from typing import TYPE_CHECKING, Dict
from unittest.mock import patch

import pytest

from fittrackee import abortable, db
from fittrackee.users.models import UserTask

from ..mixins import ApiTestCaseMixin, BaseTestMixin, UserTaskMixin
from ..utils import OAUTH_SCOPES, jsonify_dict

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User

MESSAGE_ID = "e7640357-3b8d-47be-885d-68104cdfe4b2"


class TestWorkoutsTasksGetTasks(
    ApiTestCaseMixin, BaseTestMixin, UserTaskMixin
):
    route = "/api/workouts/upload-tasks"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
    ) -> None:
        client = app.test_client()

        response = client.get(self.route)

        self.assert_401(response)

    def test_it_returns_empty_list_when_no_upload_tasks_for_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        self.create_workouts_upload_task(user_2)
        self.create_user_data_export_task(user_1)

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
            workouts_upload_task = self.create_workouts_upload_task(user_1)
            tasks.append(workouts_upload_task)

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
            workouts_upload_task = self.create_workouts_upload_task(user_1)
            tasks.append(workouts_upload_task)

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

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            self.route,
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestWorkoutsTasksGetTask(UserTaskMixin, ApiTestCaseMixin, BaseTestMixin):
    route = "/api/workouts/upload-tasks/{task_id}"

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

    def test_it_returns_404_when_task_does_not_belong_to_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(task_id=workouts_upload_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_404_when_task_is_not_a_workouts_upload_task(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        export_data_task = self.create_user_data_export_task(user_1)
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
        workouts_upload_task = self.create_workouts_upload_task(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.get(
            self.route.format(task_id=workouts_upload_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["task"] == jsonify_dict(workouts_upload_task.serialize())

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.get(
            self.route.format(task_id=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestWorkoutsTasksDeleteTask(
    ApiTestCaseMixin, BaseTestMixin, UserTaskMixin
):
    route = "/api/workouts/upload-tasks/{task_id}"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
    ) -> None:
        client = app.test_client()

        response = client.delete(
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

        response = client.delete(
            self.route.format(task_id=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_404_when_task_does_not_belong_to_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(task_id=workouts_upload_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_404_when_task_is_not_workouts_upload_task(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        export_data_task = self.create_user_data_export_task(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(task_id=export_data_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [
            ("aborted", {"aborted": True}),
            ("errored", {"errored": True}),
            ("successful", {"progress": 100}),
        ],
    )
    def test_it_deletes_user_task_when_status_is_valid(
        self,
        app: "Flask",
        user_1: "User",
        input_status: str,
        input_task_data: Dict,
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(
            user_1, **input_task_data
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(task_id=workouts_upload_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 204
        assert UserTask.query.count() == 0

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [("queued", {"progress": 0}), ("in_progress", {"progress": 10})],
    )
    def test_it_returns_400_when_status_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        input_status: str,
        input_task_data: Dict,
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(
            user_1, **input_task_data
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(task_id=workouts_upload_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response,
            "queued or ongoing workout upload task can not be deleted",
        )

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:read": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.delete(
            self.route.format(task_id=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)


class TestWorkoutsTasksAbortTask(
    UserTaskMixin, ApiTestCaseMixin, BaseTestMixin
):
    route = "/api/workouts/upload-tasks/{task_id}/abort"

    def test_it_returns_error_if_user_is_not_authenticated(
        self,
        app: "Flask",
    ) -> None:
        client = app.test_client()

        response = client.post(
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

        response = client.post(
            self.route.format(task_id=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_404_when_task_does_not_belong_to_user(
        self,
        app: "Flask",
        user_1: "User",
        user_2: "User",
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(
            user_2, message_id=MESSAGE_ID
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(task_id=workouts_upload_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    def test_it_returns_404_when_task_is_not_a_workouts_upload_task(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        export_data_task = self.create_user_data_export_task(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(task_id=export_data_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_404_with_message(response, "no task found")

    @pytest.mark.parametrize(
        "input_status, input_task_data",
        [
            ("aborted", {"aborted": True}),
            ("errored", {"errored": True}),
            ("successful", {"progress": 100}),
        ],
    )
    def test_it_returns_400_when_task_status_is_invalid(
        self,
        app: "Flask",
        user_1: "User",
        input_status: str,
        input_task_data: Dict,
    ) -> None:
        export_data_task = self.create_workouts_upload_task(
            user_1, message_id=MESSAGE_ID, **input_task_data
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(task_id=export_data_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_400(
            response, "only queued and ongoing tasks can be aborted"
        )

    def test_it_returns_500_when_message_id_is_none(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        export_data_task = self.create_workouts_upload_task(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route.format(task_id=export_data_task.short_id),
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        self.assert_500(response, "error when aborting task")

    def test_it_calls_dramatiq_abort_when_task_is_valid(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(
            user_1, message_id=MESSAGE_ID
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch("fittrackee.workouts.workouts.abort") as abort_mock:
            client.post(
                self.route.format(task_id=workouts_upload_task.short_id),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        abort_mock.assert_called_once_with(
            message_id=MESSAGE_ID, middleware=abortable
        )

    def test_it_returns_500_when_dramatiq_abort_raises_exception(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(
            user_1, message_id=MESSAGE_ID
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch(
            "fittrackee.workouts.workouts.abort", side_effect=Exception()
        ):
            response = client.post(
                self.route.format(task_id=workouts_upload_task.short_id),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        self.assert_500(response, "error when aborting task")

    def test_it_returns_aborted_user_task(
        self,
        app: "Flask",
        user_1: "User",
    ) -> None:
        workouts_upload_task = self.create_workouts_upload_task(
            user_1, message_id=MESSAGE_ID
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        with patch("fittrackee.workouts.workouts.abort"):
            response = client.post(
                self.route.format(task_id=workouts_upload_task.short_id),
                headers=dict(Authorization=f"Bearer {auth_token}"),
            )

        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data["status"] == "success"
        assert data["task"] == jsonify_dict(workouts_upload_task.serialize())
        db.session.refresh(workouts_upload_task)
        assert workouts_upload_task.aborted is True

    @pytest.mark.parametrize(
        "client_scope, can_access",
        {**OAUTH_SCOPES, "workouts:write": True}.items(),
    )
    def test_expected_scopes_are_defined(
        self,
        app: "Flask",
        user_1: "User",
        client_scope: str,
        can_access: bool,
    ) -> None:
        (
            client,
            oauth_client,
            access_token,
            _,
        ) = self.create_oauth2_client_and_issue_token(
            app, user_1, scope=client_scope
        )

        response = client.post(
            self.route.format(task_id=self.random_short_id()),
            headers=dict(Authorization=f"Bearer {access_token}"),
        )

        self.assert_response_scope(response, can_access)

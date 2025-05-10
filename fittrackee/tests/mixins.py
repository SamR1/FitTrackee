import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from unittest.mock import Mock
from urllib.parse import parse_qs
from uuid import uuid4

from flask import Flask, current_app
from flask.testing import FlaskClient
from urllib3.util import parse_url
from werkzeug.test import TestResponse

from fittrackee import db
from fittrackee.comments.models import Comment
from fittrackee.files import get_absolute_file_path
from fittrackee.oauth2.client import create_oauth2_client
from fittrackee.oauth2.models import OAuth2Client, OAuth2Token
from fittrackee.reports.models import Report, ReportAction, ReportActionAppeal
from fittrackee.users.models import User, UserTask
from fittrackee.utils import encode_uuid
from fittrackee.workouts.models import Workout

from .custom_asserts import (
    assert_errored_response,
    assert_oauth_errored_response,
)
from .utils import (
    TEST_OAUTH_CLIENT_METADATA,
    get_date_string,
    random_email,
    random_int,
    random_string,
)


class BaseTestMixin:
    """call args are returned differently between Python 3.7 and 3.7+"""

    @staticmethod
    def get_args(call_args: Tuple) -> Tuple:
        if len(call_args) == 2:
            args, _ = call_args
        else:
            _, args, _ = call_args
        return args

    @staticmethod
    def get_kwargs(call_args: Tuple) -> Dict:
        if len(call_args) == 2:
            _, kwargs = call_args
        else:
            _, _, kwargs = call_args
        return kwargs

    def assert_call_args_keys_equal(
        self, mock: Mock, expected_keys: List
    ) -> None:
        args_list = self.get_kwargs(mock.call_args)
        assert list(args_list.keys()) == expected_keys

    @staticmethod
    def assert_dict_contains_subset(container: Dict, subset: Dict) -> None:
        assert subset.items() <= container.items()


class RandomMixin:
    @staticmethod
    def random_string(
        length: Optional[int] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> str:
        return random_string(length, prefix, suffix)

    @staticmethod
    def random_domain() -> str:
        return random_string(prefix="https://", suffix="com")

    @staticmethod
    def random_email() -> str:
        return random_email()

    @staticmethod
    def random_int(min_value: int = 0, max_value: int = 999999) -> int:
        return random_int(min_value, max_value)

    @staticmethod
    def random_short_id() -> str:
        return encode_uuid(uuid4())

    @staticmethod
    def get_date_string(
        *,
        date_format: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> str:
        return get_date_string(
            date_format if date_format else "%a, %d %b %Y %H:%M:%S GMT", date
        )


class OAuth2Mixin(RandomMixin):
    @staticmethod
    def create_oauth2_client(
        user: User,
        metadata: Optional[Dict] = None,
        scope: Optional[str] = None,
    ) -> OAuth2Client:
        client_metadata = (
            TEST_OAUTH_CLIENT_METADATA if metadata is None else metadata
        )
        if scope is not None:
            client_metadata["scope"] = scope
        oauth_client = create_oauth2_client(client_metadata, user)
        db.session.add(oauth_client)
        db.session.commit()
        return oauth_client

    def create_oauth2_token(
        self,
        oauth_client: OAuth2Client,
        issued_at: Optional[int] = None,
        access_token_revoked_at: Optional[int] = 0,
        expires_in: Optional[int] = 1000,
    ) -> OAuth2Token:
        issued_at = issued_at if issued_at else int(time.time())
        token = OAuth2Token(
            client_id=oauth_client.client_id,
            access_token=self.random_string(),
            refresh_token=self.random_string(),
            issued_at=issued_at,
            access_token_revoked_at=access_token_revoked_at,
            expires_in=expires_in,
        )
        db.session.add(token)
        db.session.commit()
        return token


class ApiTestCaseMixin(OAuth2Mixin, RandomMixin):
    @staticmethod
    def get_test_client_and_auth_token(
        app: Flask, user_email: str
    ) -> Tuple[FlaskClient, str]:
        client = app.test_client()
        resp_login = client.post(
            "/api/auth/login",
            data=json.dumps(
                dict(
                    email=user_email,
                    password="12345678",
                )
            ),
            content_type="application/json",
        )
        auth_token = json.loads(resp_login.data.decode())["auth_token"]
        return client, auth_token

    @staticmethod
    def authorize_client(
        client: FlaskClient,
        oauth_client: OAuth2Client,
        auth_token: str,
        scope: Optional[str] = None,
        code_challenge: Optional[Dict] = None,
    ) -> Union[List[str], str]:
        if code_challenge is None:
            code_challenge = {}
        response = client.post(
            "/api/oauth/authorize",
            data={
                "client_id": oauth_client.client_id,
                "confirm": True,
                "response_type": "code",
                "scope": "read" if not scope else scope,
                **code_challenge,
            },
            headers=dict(
                Authorization=f"Bearer {auth_token}",
                content_type="multipart/form-data",
            ),
        )
        data = json.loads(response.data.decode())
        parsed_url = parse_url(data["redirect_url"])
        code = parse_qs(parsed_url.query).get("code", "")
        return code

    def create_oauth2_client_and_issue_token(
        self, app: Flask, user: User, scope: Optional[str] = None
    ) -> Tuple[FlaskClient, OAuth2Client, str, str]:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user.email
        )
        oauth_client = self.create_oauth2_client(user, scope=scope)
        code = self.authorize_client(
            client, oauth_client, auth_token, scope=scope
        )
        response = client.post(
            "/api/oauth/token",
            data={
                "client_id": oauth_client.client_id,
                "client_secret": oauth_client.client_secret,
                "grant_type": "authorization_code",
                "code": code,
            },
            headers=dict(content_type="multipart/form-data"),
        )
        data = json.loads(response.data.decode())
        return client, oauth_client, data.get("access_token"), auth_token

    @staticmethod
    def assert_400(
        response: TestResponse,
        error_message: Optional[str] = "invalid payload",
        status: Optional[str] = "error",
    ) -> Dict:
        return assert_errored_response(
            response, 400, error_message=error_message, status=status
        )

    @staticmethod
    def assert_401(
        response: TestResponse,
        error_message: Optional[str] = "provide a valid auth token",
    ) -> Dict:
        return assert_errored_response(
            response, 401, error_message=error_message
        )

    @staticmethod
    def assert_403(
        response: TestResponse,
        error_message: Optional[str] = "you do not have permissions",
    ) -> Dict:
        return assert_errored_response(response, 403, error_message)

    @staticmethod
    def assert_404(response: TestResponse) -> Dict:
        return assert_errored_response(response, 404, status="not found")

    @staticmethod
    def assert_404_with_entity(response: TestResponse, entity: str) -> Dict:
        error_message = f"{entity} does not exist"
        return assert_errored_response(
            response, 404, error_message=error_message, status="not found"
        )

    @staticmethod
    def assert_404_with_message(
        response: TestResponse, error_message: str
    ) -> Dict:
        return assert_errored_response(
            response, 404, error_message=error_message, status="not found"
        )

    @staticmethod
    def assert_413(
        response: TestResponse,
        error_message: Optional[str] = None,
        match: Optional[str] = None,
    ) -> Dict:
        return assert_errored_response(
            response,
            413,
            error_message=error_message,
            status="fail",
            match=match,
        )

    @staticmethod
    def assert_500(
        response: TestResponse,
        error_message: Optional[str] = (
            "error, please try again or contact the administrator"
        ),
        status: Optional[str] = "error",
    ) -> Dict:
        return assert_errored_response(
            response, 500, error_message=error_message, status=status
        )

    @staticmethod
    def assert_unsupported_grant_type(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response, 400, error="unsupported_grant_type"
        )

    @staticmethod
    def assert_invalid_client(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response,
            400,
            error="invalid_client",
        )

    @staticmethod
    def assert_invalid_grant(
        response: TestResponse, error_description: Optional[str] = None
    ) -> Dict:
        return assert_oauth_errored_response(
            response,
            400,
            error="invalid_grant",
            error_description=error_description,
        )

    @staticmethod
    def assert_invalid_request(
        response: TestResponse, error_description: Optional[str] = None
    ) -> Dict:
        return assert_oauth_errored_response(
            response,
            400,
            error="invalid_request",
            error_description=error_description,
        )

    @staticmethod
    def assert_invalid_token(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response,
            401,
            error="invalid_token",
            error_description=(
                "The access token provided is expired, revoked, malformed, "
                "or invalid for other reasons."
            ),
        )

    @staticmethod
    def assert_insufficient_scope(response: TestResponse) -> Dict:
        return assert_oauth_errored_response(
            response,
            403,
            error="insufficient_scope",
            error_description=(
                "The request requires higher privileges than provided by "
                "the access token."
            ),
        )

    @staticmethod
    def assert_not_insufficient_scope_error(response: TestResponse) -> None:
        assert response.status_code != 403

    def assert_response_scope(
        self, response: TestResponse, can_access: bool
    ) -> None:
        if can_access:
            self.assert_not_insufficient_scope_error(response)
        else:
            self.assert_insufficient_scope(response)

    @staticmethod
    def assert_return_not_found(
        url: str, client: FlaskClient, auth_token: str, message: str
    ) -> None:
        response = client.post(
            url,
            content_type="application/json",
            headers=dict(Authorization=f"Bearer {auth_token}"),
        )

        assert response.status_code == 404
        data = json.loads(response.data.decode())
        assert data["status"] == "not found"
        assert data["message"] == message

    def assert_return_user_not_found(
        self, url: str, client: FlaskClient, auth_token: str
    ) -> None:
        self.assert_return_not_found(
            url, client, auth_token, "user does not exist"
        )


class ReportMixin(RandomMixin):
    def create_report(
        self,
        *,
        reporter: User,
        reported_object: Union[Comment, User, Workout],
        note: Optional[str] = None,
    ) -> Report:
        report = Report(
            note=note if note else self.random_string(),
            reported_by=reporter.id,
            reported_object=reported_object,
        )
        db.session.add(report)
        db.session.commit()
        return report

    def create_user_report(self, reporter: User, user: User) -> Report:
        return self.create_report(reporter=reporter, reported_object=user)

    @staticmethod
    def create_report_action(
        moderator: User,
        user: User,
        report_id: int,
        *,
        action_type: Optional[str] = None,
        comment_id: Optional[int] = None,
        workout_id: Optional[int] = None,
    ) -> ReportAction:
        report_action = ReportAction(
            moderator_id=moderator.id,
            action_type=action_type if action_type else "user_suspension",
            comment_id=(
                comment_id
                if (
                    comment_id
                    and action_type
                    and action_type.startswith("comment_")
                )
                else None
            ),
            report_id=report_id,
            user_id=user.id,
            workout_id=(
                workout_id
                if (
                    workout_id
                    and action_type
                    and action_type.startswith("workout_")
                )
                else None
            ),
        )
        db.session.add(report_action)
        db.session.commit()
        return report_action

    def create_report_user_action(
        self,
        admin: User,
        user: User,
        action_type: str = "user_suspension",
        report_id: Optional[int] = None,
    ) -> ReportAction:
        report_id = (
            report_id if report_id else self.create_user_report(admin, user).id
        )
        report_action = self.create_report_action(
            admin, user, action_type=action_type, report_id=report_id
        )
        user.suspended_at = (
            datetime.now(timezone.utc)
            if action_type == "user_suspension"
            else None
        )
        db.session.commit()
        return report_action

    def create_report_workout_action(
        self,
        admin: User,
        user: User,
        workout: Workout,
        action_type: str = "workout_suspension",
    ) -> ReportAction:
        report_action = ReportAction(
            action_type=action_type,
            moderator_id=admin.id,
            report_id=self.create_report(
                reporter=admin, reported_object=workout
            ).id,
            workout_id=workout.id,
            user_id=user.id,
        )
        db.session.add(report_action)
        return report_action

    def create_report_comment_action(
        self,
        admin: User,
        user: User,
        comment: Comment,
        action_type: str = "comment_suspension",
    ) -> ReportAction:
        report_action = ReportAction(
            action_type=action_type,
            moderator_id=admin.id,
            comment_id=comment.id,
            report_id=self.create_report(
                reporter=admin, reported_object=comment
            ).id,
            user_id=user.id,
        )
        db.session.add(report_action)
        comment.suspended_at = (
            datetime.now(timezone.utc)
            if action_type == "comment_suspension"
            else None
        )
        return report_action

    def create_report_comment_actions(
        self, admin: User, user: User, comment: Comment
    ) -> ReportAction:
        for n in range(2):
            action_type = (
                "comment_suspension" if n % 2 == 0 else "comment_unsuspension"
            )
            report_action = self.create_report_comment_action(
                admin, user, comment, action_type
            )
            db.session.add(report_action)
        report_action = self.create_report_comment_action(
            admin, user, comment, "comment_suspension"
        )
        db.session.add(report_action)
        return report_action

    def create_action_appeal(
        self, action_id: int, user: User, with_commit: bool = True
    ) -> ReportActionAppeal:
        report_action_appeal = ReportActionAppeal(
            action_id=action_id,
            user_id=user.id,
            text=self.random_string(),
        )
        db.session.add(report_action_appeal)
        if with_commit:
            db.session.commit()
        return report_action_appeal


class UserTaskMixin:
    @staticmethod
    def create_user_data_export_task(
        user: "User",
        *,
        created_at: Optional[datetime] = None,
        progress: int = 0,
        errored: bool = False,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        message_id: Optional[str] = None,
    ) -> "UserTask":
        data_export_task = UserTask(
            user_id=user.id,
            created_at=created_at,
            task_type="user_data_export",
        )
        data_export_task.progress = progress
        data_export_task.errored = errored
        data_export_task.file_path = file_path
        data_export_task.file_size = file_size
        data_export_task.message_id = message_id
        db.session.add(data_export_task)
        db.session.commit()
        return data_export_task

    @staticmethod
    def generate_temporary_data_export(
        user_id: int,
        file: str,
    ) -> str:
        file_path = get_absolute_file_path(
            os.path.join("exports", str(user_id), file)
        )
        export_file = Path(file_path)
        export_file.parent.mkdir(exist_ok=True, parents=True)
        export_file.write_text("some text")
        return file_path

    @staticmethod
    def create_workouts_upload_task(
        user: "User",
        *,
        workouts_data: Optional[Dict] = None,
        files_to_process: Optional[List[str]] = None,
        equipment_ids: Optional[List[int]] = None,
        file_path: str = "",
        file_size: Optional[int] = None,
        progress: int = 0,
        new_workouts_count: int = 0,
        errored: bool = False,
        original_file_name: Optional[str] = None,
        aborted: bool = False,
        message_id: Optional[str] = None,
        updated_at: Optional[datetime] = None,
    ) -> "UserTask":
        upload_task = UserTask(
            user_id=user.id,
            task_type="workouts_archive_upload",
            data={
                "new_workouts_count": new_workouts_count,
                "workouts_data": workouts_data if workouts_data else {},
                "files_to_process": files_to_process
                if files_to_process
                else [],
                "equipment_ids": equipment_ids,
                "original_file_name": original_file_name,
            },
            file_path=file_path,
        )
        upload_task.aborted = aborted
        upload_task.progress = progress
        upload_task.errored = errored
        upload_task.file_size = file_size
        upload_task.message_id = message_id
        upload_task.updated_at = updated_at
        db.session.add(upload_task)
        db.session.commit()
        return upload_task

    @staticmethod
    def generate_temporary_archive(
        zip_archive: str = "tests/files/gpx_test.zip",
    ) -> str:
        _, file_path = tempfile.mkstemp(prefix="archive_", suffix=".zip")
        shutil.copyfile(
            os.path.join(current_app.root_path, zip_archive), file_path
        )
        return file_path
